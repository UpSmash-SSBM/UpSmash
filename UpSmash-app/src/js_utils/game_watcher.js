const chokidar = require('chokidar');
const { SlippiGame } = require("@slippi/slippi-js");
const _ = require("lodash");
const { file_submit } = require('./file_submit');
const https = require('node:https');

const slippi_game_end_types = {
    1: "TIME!",
    2: "GAME!",
    7: "No Contest",
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function rating(connect_code, sleep_amount) {
    await sleep(sleep_amount);
    // this guy is going to actually tell the server to get new rank when its called
    // just submit the new file, and then update the rank server side, don't parse locally
    const rank_options = {
      hostname:'www.upsmash.net',
      port: '443',
      path: '/rating/' + connect_code.replace('#','-'),
      method: 'GET'
    }
    return new Promise(function (resolve, reject) {
        const req = https.request(rank_options, (response) => {
            response.setEncoding('utf8');
            //console.log(response.statusCode);
            // catches the servers response and prints it
            response.on('data', (rating_response) => {
                if (response.statusCode == 200) {
                    var json_response = JSON.parse(rating_response)
                    resolve(json_response['rating'])
                }
            });
            // if the response is over, writes it also
            response.on('end', () => {
                //console.log('No more data in response.');
            });
        });
        // error processing
        req.on('error', (err) => {
            console.log(response.statusCode);
            console.log(err);
        });
        // send the actual data
        req.end();
    })
}

function file_change_handler(path, isFirstEndFrame) {
    try {
        game = new SlippiGame(path, { processOnTheFly: true });
    } catch (err) {
        console.log(err);
        return;
    }
    let settings, frames, latestFrame, gameEnd;
    settings = game.getSettings();
    frames = game.getFrames();
    latestFrame = game.getLatestFrame();
    gameEnd = game.getGameEnd();
    let matchId = settings['matchInfo']['matchId'];
    let matchSub = matchId.split('.')[1];
    let matchType = matchSub.split('-')[0];
    
    // gameEnd will be null until the game is over
    if (gameEnd && !isFirstEndFrame) { //isFirstEndFrame is used because there are actually two end frames
        if (matchType == 'ranked') { 
            const endMessage = _.get(slippi_game_end_types, gameEnd.gameEndMethod) || "Unknown";
            const lrasText = gameEnd.gameEndMethod === 7 ? ` | Quitter Index: ${gameEnd.lrasInitiatorIndex}` : "";
            //console.log(`[Game Complete] Type: ${endMessage}${lrasText}`)
            // console.log(gameEnd)
            players = settings['players']
            //console.log(players)
            for (let i = 0; i < players.length; i++) {
                console.log('updating rating for ' + players[i]['connectCode'])
                rating(players[i]['connectCode'], 5000)
            }
            // console.log(player_wins)
        }
        let fileList = new Array();
        fileList.push(path);
        // console.log('sending played game')
        file_submit(fileList);
        // console.log('sent played game')
        return true;
    }
    return false;
}

function game_checker(item) {
    const watcher = chokidar.watch(item, {
        depth: 1,
        persistent: true,
        usePolling: true,
        ignoreInitial: true,
    });
    let current_game_path = "";
    let isFirstEndFrame = false;
    watcher
    .on('ready', function() {
        console.log('Initial scan complete. Ready for changes')
    })
    .on('add', function(path) { 
        console.log('ADDED')
    })
    .on('change', (path) => {
        if (current_game_path != path) {
            current_game_path = path;
            isFirstEndFrame = false;
            console.log("New game");
        }
        isFirstEndFrame = file_change_handler(path, isFirstEndFrame)
    });
}

module.exports = { game_checker, rating };