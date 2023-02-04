const { SlippiGame } = require("@slippi/slippi-js");
const fs = require('fs');
const { performance } = require('perf_hooks');


let input_folder = '../website/upsmash/static/files/'
let output_folder = '../website/upsmash/static/json/'
//let file = "Game_20221201T132125.slp"
let file = process.argv[2]
let full_filename = input_folder + file
//let game2 = new SlippiGame('C:\\Users\\Ryan\\Documents\\UpSmash\\UpSmash\\static\\files\\Game_20230131T130658.slp')
let file_sub = file.substring(0,20);
// var startTime = performance.now()

const game = new SlippiGame(input_folder + file);
// var endTime = performance.now();
//console.log(`Setup time ${endTime - startTime} milliseconds`);
const settings = game.getSettings();
const metadata = game.getMetadata();
const stats = game.getStats();
const winner = game.getWinners();
// console.log(winner[0]);
const winner_index = winner[0]['playerIndex']
// console.log(winner[0]['playerIndex']);
const winner_tag = settings['players'][winner_index]['connectCode']
//console.log(winner_tag);
// console.log(stats['overall']);
let new_json = {'settings': settings,'metadata':metadata,'stats':stats,'winner':winner_tag};
var startTime = performance.now()
let stats_string = JSON.stringify(new_json, null, 4);
var endTime = performance.now()
//console.log(`JSON stringify time ${endTime - startTime} milliseconds`)
var startTime = performance.now()
fs.writeFileSync(output_folder + file_sub + '.json', stats_string, err => {
    if (err) {
    console.error(err);
    }
    // file written successfully
});
var endTime = performance.now()
//console.log(`Write to file time ${endTime - startTime} milliseconds`)
