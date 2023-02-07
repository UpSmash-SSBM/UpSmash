const chokidar = require('chokidar');
const { rating } = require('./js_utils/game_watcher.js');

setInterval(checkForGame, 500); 
let periodCount = 0;
let gameInProgress = false;
let isFolderSet = false;
let parentFolder;

let player1_name, player1_wins, player1_code, player1_rating;
let player2_name, player2_wins, player2_code, player2_rating;
player1_wins = 0;
player2_wins = 0;

document.getElementById("slpFolder").addEventListener("change", (event) => {
    //console.log('caught event')
    parentFolder = event.target.files[0].path.split('Game')[0];
    //console.log(parentFolder)
    isFolderSet = true;
    const watcher = chokidar.watch(parentFolder, {
        ignored: '/*.slp', // TODO: This doesn't work. Use regex?
        depth: 0,
        persistent: true,
        usePolling: true,
        ignoreInitial: true,
    });

    let current_game_path = "";
    watcher.on('change', (path) => {
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

        if (!gameInProgress) {
            player1_rating = rating(player1_code).then()
            player2_rating = rating(player2_code).then()
            console.log(player1_rating)
        }
        gameInProgress = true;

        if (gameEnd) {
            player1_wins += gameEnd['placements'][0]['position']
            player2_wins += gameEnd['placements'][1]['position']
            gameInProgress = false;
        }
    });
})

function waitingText() {
    if (periodCount > 3) {
        periodCount = 0
    }
    startingText = 'Waiting on game'
    for (let periodNum=0; periodNum<periodCount; periodNum++){
        startingText += '.'
    }
    document.getElementById("waitingText").textContent = startingText

    periodCount += 1
}

function checkForGame() {
    if (isFolderSet && !gameInProgress) {
        waitingText()
    } else if (isFolderSet && gameInProgress) {
        let newString = player1_name + ' (' + player1_code + ') ' + ' ' + player1_wins + '-' + player2_wins + ' ' + player2_name + ' (' + player2_code + ') '
        document.getElementById("waitingText").textContent = newString;
    }
}
