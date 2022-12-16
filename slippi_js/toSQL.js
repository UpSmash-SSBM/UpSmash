var sqlite3 = require('sqlite3').verbose();
var fs = require('fs');
var dbFile = './instance/db.sqlite3';
var dbExists = fs.existsSync('./instance/db.sqlite3');
const { SlippiGame } = require("@slippi/slippi-js");
const calcs = require('./stat_calcs');

//Before we start lets check that the table with player data exists. It should exist once the website goes
//live so this is really just a startup condition


//first we need to access the data from the slp file ( or files) that are in our temp folder

let input_folder = './static/files/';

// check if it exits, if not then create it 
if (!dbExists) {
    fs.openSync(dbFile, 'w');
    var db = new sqlite3.Database(dbFile);
    console.log('Creating the Upsmash Database')
} else{
    let db = new sqlite3.Database('./instance/db.sqlite3', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Connected to Upsmash database');
    });
    db.serialize(() => {
        db.prepare(`CREATE TABLE IF NOT EXISTS US_Lookup (GameID INT, Player1 TEXT, Player2 TEXT)`).run().finalize();
        db.prepare(`CREATE TABLE IF NOT EXISTS US_Data (GameID TEXT, Name TEXT, DmgperOpen INT, OpenperKill INT, TotDmg INT)`).run().finalize();
    });
    fs.readdir(input_folder, function (err, files) {
        if (err) {
            console.log("Unable to scan directory: " + err);
        }
        files.forEach(function (file) {
            let file_sub = file.substring(0,20);
            const game = new SlippiGame(input_folder + file);
            const settings = game.getSettings();
            const metadata = game.getMetadata();
            const stats = game.getStats();
            const p0killmoves = calcs.calculate_killmoves(stats, 0);
            const p0killID = calcs.most_common_kill(p0killmoves);
            const p1killmoves = calcs.calculate_killmoves(stats, 1);
            const p1killID = calcs.most_common_kill(p1killmoves);
            const p0neutrals = calcs.neutral_openers(stats, 0);
            const p1neutrals = calcs.neutral_openers(stats, 1);
            const p0dmgopen = stats['overall'][0]['damagePerOpening']['ratio'];
            const p1dmgopen = stats['overall'][1]['damagePerOpening']['ratio'];
            const p0openkill = stats['overall'][0]['openingsPerKill']['ratio'];
            const p1openkill = stats['overall'][1]['openingsPerKill']['ratio'];
            const winner = calcs.getWinner(game, stats, settings);
            if (winner != false){
                let lookupData = [file_sub.substring(5), metadata['players'][0]['names']['code'], metadata['players'][1]['names']['code']];
                let datap1 = [file_sub.substring(5), metadata['players'][0]['names']['code'], stats['overall'][0]['damagePerOpening']['count'], stats['overall'][0]['openingsPerKill']['count'], stats['overall'][0]['totalDamage']];
                let datap2 = [metadata['players'][1]['names']['code'], stats['overall'][1]['damagePerOpening']['count'], stats['overall'][1]['openingsPerKill']['count'], stats['overall'][1]['totalDamage']];
                let sqlData = `INSERT INTO US_Data(GameID, Name, DmgperOpen, OpenperKill, TotDmg) Values(?, ?, ?, ?, ?)`;
                let sqlLookup = `INSERT INTO US_Lookup(GameID, Player1, Player2) Values(?, ?, ?)`;
                db.serialize(function() {
                    db.run(sqlLookup, lookupData, function(err) {
                        if (err){
                            console.log(err);
                        }
                        console.log(`Row(s) updates: ${this.changes}`);
                    });
                    db.run(sqlData, datap1, function(err) {
                        if (err){
                            console.log(err);
                        }
                        console.log(`Row(s) updates: ${this.changes}`);
                    });
                    db.run(sqlData, datap2, function(err) {
                        if (err){
                            console.log(err);
                        }
                        console.log(`Row(s) updates: ${this.changes}`);
                    });
                });
            } else {
                console.log('GAME DID NOT COMPLETE')
            };
        });
    });
};