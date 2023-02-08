const electron = require('electron');
const { ipcRenderer } = electron;
const { SlippiGame } = require("@slippi/slippi-js");
const { request } = require('http');
const https = require('node:https');

// function for getting a list of players games
async function get_database_games(connect_code) {
    const game_options = {
        hostname:'www.upsmash.net',
        port: '443',
        path: '/player_games/' + connect_code.replace('#','-'),
        method: 'GET'
    };
    let response = await doRequest(game_options, connect_code)
    return response
}

//function for determing who the local player is
function get_local(fileList) {
    let codes = new Array();
    let mf = 1;
    let m = 0;
    let item;
    for (file_num in fileList) {
        // console.log(file_num)
        let game = new SlippiGame(fileList[file_num])
        let settings = game.getSettings()
        let players = settings['players']
        // This next line is buggy, needs work
        player1_code = players[0]['connectCode']
        player2_code = players[1]['connectCode']
        codes.push(player1_code, player2_code)
    }
    for (let i=0; i<codes.length; i++) {
        for (let j=i; j<codes.length; j++) {
            if (codes[i] == codes[j]){
                m++;
            }
            if (mf<m) {
                mf=m; 
                item = codes[i];
            }
        }
        m=0;
    }
    return item
}


function doRequest(url, connect_code) {
    return new Promise(function (resolve, reject) {
        const req = https.request(url, (response) => {
            response.setEncoding('utf8');
            //console.log(response.statusCode);
            var body = '';
            // catches the servers response and prints it
            response.on('data', (game_list) => {
                body += game_list
            });
            // if the response is over, writes it also
            response.on('end', function() {
                if (response.statusCode == 200) {
                    resolve(body)
                }
            });
        });
        // error processing
        req.on('error', (err) => {
            console.log(err)
            console.log(err.statusCode);
            reject(err);
        });
        // send the actual data
        req.write(connect_code);
        req.end();
    })
}

// listens for a click change
document.getElementById("slpFolder").addEventListener("change", (event) => {
    // variables to write to in the display in order to tell the user how many files have been uploaded
    let htmlList = document.getElementById("listing");
    let htmlListItem = document.createElement("li");
    // this is the directory where the files are
    let mainFolder = event.target.files[0].path.split('Game')[0]
    // adds the file names to the list, after loop will have the full list of files names to upload
    htmlListItem.textContent = mainFolder;
    htmlList.appendChild(htmlListItem);
    let localFileList = new Array();
    let localFileIDs = new Array();
    for (const file of event.target.files){
        if (file.path.includes('slp')) {
            localFileList.push(file.path);
            let splitFilePath = file.path.split('\\')
            let slippiReplayName = splitFilePath[splitFilePath.length - 1]
            let slippiGameID = slippiReplayName.replace('.slp','')
            localFileIDs.push(slippiGameID)
        }
    }
    //console.log(fileList)
    var connect_local = get_local(localFileList)
    //console.log(connect_local)
    let databaseGamesPromise = get_database_games(connect_local);
    databaseGamesPromise.then((databaseGames) => {
        console.log(databaseGames)
        console.log(localFileIDs)
        let filesToSend = new Array();
        let to_send = localFileIDs.filter(function(item) {
            console.log(item)
            return databaseGames.indexOf(item) == -1;
        });
        console.log(to_send)
        for (suffix in to_send) {
            console.log(suffix)
            let attach = mainFolder + to_send[suffix] + '.slp'
            filesToSend.push(attach)
        }
        console.log(filesToSend)
        if (localFileList.length == event.target.files.length) {
            ipcRenderer.send("fileList", filesToSend)
            ipcRenderer.send("parentPath", mainFolder)
        }; 
    })
}, false);