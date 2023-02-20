const chokidar = require('chokidar');
const { rating } = require('./js_utils/game_watcher.js');

setInterval(checkForGame, 500); 
let periodCount = 0;
let hasGameStarted = false;
let isFolderSet = false;

let player1_name, player1_wins, player1_code;
let player2_name, player2_wins, player2_code;
let player1_rating = "";
let player2_rating = ""
player1_wins = 0;
player2_wins = 0;
let player_array = new Array();

async function get_rating(player_code) {
    let response = await rating(player_code, 0)
    return response
}

document.getElementById("slpFolder").addEventListener("change", (event) => {
    // console.log(event.target.files[0])
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
    isFolderSet = true;
    const watcher = chokidar.watch(mainFolder, {
        depth: 1,
        persistent: true,
        usePolling: true,
        ignoreInitial: true,
    });

    let current_game_path = "";
    watcher
    .on('add', function(path) { 
    })
    .on('change', (path) => {
        if (current_game_path != path) {
            current_game_path = path;
            //console.log("New game pt2");
        }
        let game = new SlippiGame(path, { processOnTheFly: true });
        let gameEnd = game.getGameEnd();
        let settings = game.getSettings();
        
        players = settings['players']
        player1_name = players[0]['displayName']
        player1_code = players[0]['connectCode']
        player2_name = players[1]['displayName']
        player2_code = players[1]['connectCode']

        let current_player_array = new Array(player1_code, player2_code);
        current_player_array.sort();
        if (current_player_array[0] != player_array[0] || current_player_array[1] != player_array[1]) {
            player1_wins = 0;
            player2_wins = 0;
            player_array = current_player_array;
            console.log('new session')
        }

        if (!hasGameStarted) {
            hasGameStarted = true;
            get_rating(player1_code).then((player_rating) => {
                player1_rating = player_rating;
            })
            get_rating(player2_code).then((player_rating) => {
                player2_rating = player_rating;
            })
        }

        if (gameEnd) {
            if (gameEnd['placements'][0]['position'] == 0) {
                player1_wins += 1
            } else {
                player2_wins += 1
            }
        }
    });
})

function waitingText() {
    if (periodCount > 3) {
        periodCount = 0
    }
    startingText = 'Waiting for a game to start'
    for (let periodNum=0; periodNum<periodCount; periodNum++){
        startingText += '.'
    }
    document.getElementById("waitingText").textContent = startingText

    periodCount += 1
}

function checkForGame() {
    if (isFolderSet && !hasGameStarted) {
        waitingText()
    } else if (isFolderSet && hasGameStarted) {
        let newString = player1_name + ' (' + player1_code + ') ' + ' ' + player1_wins + '-' + player2_wins + ' ' + player2_name + ' (' + player2_code + ') '
        document.getElementById("waitingText").textContent = newString;
        document.getElementById("playerRatings").textContent = player1_rating + "--------" + player2_rating;
    }
}
