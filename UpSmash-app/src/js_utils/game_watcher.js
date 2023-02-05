const chokidar = require('chokidar');
const { SlippiGame } = require("@slippi/slippi-js");
const _ = require("lodash");
const { request } = require('http');
const { file_submit } = require('./file_submit');

const slippi_game_end_types = {
    1: "TIME!",
    2: "GAME!",
    7: "No Contest",
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function rating(connect_code) {
    await sleep(5000);
    // this guy is going to actually tell the server to get new rank when its called
    // just submit the new file, and then update the rank server side, don't parse locally
    const rank_options = {
      hostname:'localhost',
      port: '5000',
      path: '/rating/' + connect_code.replace('#','-'),
      method: 'GET'
    };
  
    const req = request(rank_options, (response) => {
      response.setEncoding('utf8');
      //console.log(response.statusCode);
      // catches the servers response and prints it
      response.on('data', (rating_response) => {
        if (response.statusCode == 200) {
          //console.log(rating_response);
          return rating_response['rating']
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
    req.write(connect_code);
    req.end();
}

function file_change_handler(path) {
    // triggers on file being written to
    // console.log("File change");
    try {
        // create the game if it doesn't exist
        game = new SlippiGame(path, { processOnTheFly: true });
    } catch (err) {
        console.log(err);
        return;
    }
    let fileList = new Array();
    let settings, frames, latestFrame, gameEnd;
    settings = game.getSettings();
    frames = game.getFrames();
    latestFrame = game.getLatestFrame();
    gameEnd = game.getGameEnd();
    let matchId = settings['matchInfo']['matchId'];
    let matchSub = matchId.split('.')[1];
    let matchType = matchSub.split('-')[0];
    if (true || matchType == 'ranked') { 
        // gameEnd will be null until the game is over
        if (gameEnd) {
            const endMessage = _.get(slippi_game_end_types, gameEnd.gameEndMethod) || "Unknown";
            const lrasText = gameEnd.gameEndMethod === 7 ? ` | Quitter Index: ${gameEnd.lrasInitiatorIndex}` : "";
            //console.log(`[Game Complete] Type: ${endMessage}${lrasText}`)
            // console.log(gameEnd)
            players = settings['players']
            //console.log(players)
            for (let i = 0; i < players.length; i++) {
                rating(players[i]['connectCode'])
            }
            // console.log(player_wins)
            
            fileList.push(path);
            if (fileList.length > 0) {
                file_submit(fileList);
            }
        }
    }
}

function game_checker(item) {
    const watcher = chokidar.watch(item, {
        ignored: '/*.slp', // TODO: This doesn't work. Use regex?
        depth: 0,
        persistent: true,
        usePolling: true,
        ignoreInitial: true,
    });
    let current_game_path = "";
    
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
            console.log("New game");
        }
        file_change_handler(path)
    });
}

module.exports = { game_checker, rating };