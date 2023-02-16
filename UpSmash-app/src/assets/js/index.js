const electron = require('electron');
const { ipcRenderer } = electron;
const { SlippiGame } = require("@slippi/slippi-js");
const https = require('node:https');

// function for getting a list of players games
async function get_database_games(connect_code) {
    const game_options = {
        hostname:'www.upsmash.net',
        port: '443',
        path: '/player_games/' + connect_code.replace('#','-'),
        method: 'GET'
    };
    let response = await doRequest(game_options)
    return response
}

//function for determing who the local player is
function get_local_code(fileList) {
    let codes = {};
    for (file_num in fileList) {
        // console.log(file_num)
        path = fileList[file_num].path
        // console.log(path)
        if (path.includes('.slp')) {
            let game = new SlippiGame(path)
            let settings = game.getSettings()
            let players = settings['players']
            // This next line is buggy, needs work
            player1_code = players[0]['connectCode']
            player2_code = players[1]['connectCode']
            if (!(player1_code in codes)){
                codes[player1_code] = 0
            } else {
                codes[player1_code] += 1
            }
            if (!(player2_code in codes)){
                codes[player2_code] = 0
            } else {
                codes[player2_code] += 1
            }
        }
        // console.log(codes)
        let maxCount = 0;
        let currentMax = 0;
        let maxCode = "";
        for (const [code, timesSeen] of Object.entries(codes)) {
            if (currentMax < timesSeen) {
                maxCode = code
                currentMax = timesSeen
                maxCount = 1
            } else if (currentMax == timesSeen) {
                maxCount += 1
            }
        }
        if (maxCount == 1) {
            console.log(maxCode)
            return maxCode
        }
    }
}

function doRequest(url, data="") {
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
        req.write(data);
        req.end();
    })
}

// listens for a click change
document.getElementById("slpFolder").addEventListener("change", (event) => {
    // variables to write to in the display in order to tell the user how many files have been uploaded
    let htmlList = document.getElementById("listing");
    let htmlListItem = document.createElement("li");
    // this is the directory where the files are
    let fullPath = event.target.files[0].path.split("\\")
    let parentFolderName = event.target.files[0].webkitRelativePath.split("/")[0]
    // console.log(parentFolderName)
    let topFolderNum;
    for (folderNum in fullPath) {
        let currentFolder = fullPath[folderNum];
        // console.log(currentFolder)
        if (currentFolder == parentFolderName) {
            topFolderNum = parseInt(folderNum) + 1
        }
    }
    fullPath.length = topFolderNum
    mainFolder = fullPath.join("/")
    // console.log(mainFolder)
    
    // adds the file names to the list, after loop will have the full list of files names to upload
    htmlListItem.textContent = mainFolder;
    htmlList.appendChild(htmlListItem);
    var connect_local = get_local_code(event.target.files)
    let databaseGamesPromise = get_database_games(connect_local);
    databaseGamesPromise.then((databaseGames) => {
        let filesToSend = new Array();
        for (const file of event.target.files){
            if (file.path.includes('.slp')) {
                //console.log(file.path)
                let splitFilePath = file.path.split('\\')
                let slippiReplayName = splitFilePath[splitFilePath.length - 1]
                let slippiGameID = slippiReplayName.replace('.slp','')
                if (!databaseGames.includes(slippiGameID)) {
                    //console.log("adding game " + slippiGameID)
                    filesToSend.push(file.path)
                }
            }
        }
        // console.log(filesToSend)
        // console.log('starting sending files')
        ipcRenderer.send("submitFiles", filesToSend)
        ipcRenderer.send("startGameChecker", mainFolder)
    })
}, false);