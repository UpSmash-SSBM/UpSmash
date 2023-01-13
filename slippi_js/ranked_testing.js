const { SlippiGame } = require("@slippi/slippi-js");
const fs = require('fs');

let input_folder = 'C:\\Users\\cjsch\\Documents\\Slippi\\2022-12\\'
let file = 'Game_20221230T161951.slp'
const game = new SlippiGame(input_folder + file);
const settings = game.getSettings();
const matchId = settings['matchInfo']['matchId'];
console.log(matchId);