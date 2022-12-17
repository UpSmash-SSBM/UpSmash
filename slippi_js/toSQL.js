var sqlite3 = require('sqlite3').verbose();
var fs = require('fs');
var dbFile = '../UpSmash/db.sqlite3';
var dbExists = fs.existsSync(dbFile);
const { SlippiGame } = require("@slippi/slippi-js");
const calcs = require('./stat_calcs');

//Before we start lets check that the table with player data exists. It should exist once the website goes
//live so this is really just a startup condition


//first we need to access the data from the slp file ( or files) that are in our temp folder

let input_folder = '../UpSmash/static/files/';

// check if it exits, if not then create it 
if (!dbExists) {
    fs.openSync(dbFile, 'w');
    var db = new sqlite3.Database(dbFile);
    console.log('Creating the Upsmash Database')
} else{
    let db = new sqlite3.Database('../UpSmash/db.sqlite3', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Connected to Upsmash database');
    });
    db.serialize(() => {
        db.prepare(`CREATE TABLE IF NOT EXISTS player (
            id INTEGER NOT NULL, 
            connect_code VARCHAR(10) NOT NULL, 
            username VARCHAR(20), 
            PRIMARY KEY (id)
        )`).run().finalize();
        db.prepare(`CREATE TABLE IF NOT EXISTS player_slippi_replay (
            id INTEGER NOT NULL, 
            filename VARCHAR(100) NOT NULL, 
            player_id INTEGER NOT NULL, 
            PRIMARY KEY (id), 
            FOREIGN KEY(player_id) REFERENCES player (id)
        )`).run().finalize();
        db.prepare(`CREATE TABLE IF NOT EXISTS all_time_player_stats (
            id INTEGER NOT NULL, 
            connect_code_id INTEGER NOT NULL, 
            "gamesPlayed" INTEGER, 
            "gamesWon" INTEGER, 
            "maxElo" INTEGER, 
            PRIMARY KEY (id), 
            FOREIGN KEY(connect_code_id) REFERENCES player (id))`).run().finalize();
        db.prepare(`CREATE TABLE IF NOT EXISTS slippi_action_counts (
            id INTEGER NOT NULL, 
            player_slippi_replay_id INTEGER NOT NULL, 
            wavedash INTEGER, 
            waveland INTEGER, 
            airdodge INTEGER, 
            dashdance INTEGER, 
            spotdodge INTEGER, 
            ledgegrab INTEGER, 
            roll INTEGER, 
            lcancel_success_ratio FLOAT, 
            grab_success INTEGER, 
            grab_fail INTEGER, 
            tech_away INTEGER, 
            tech_in INTEGER, 
            tech INTEGER, 
            tech_fail INTEGER, 
            wall_tech_success_ratio FLOAT, 
            datetime DATETIME, 
            PRIMARY KEY (id), 
            FOREIGN KEY(player_slippi_replay_id) REFERENCES player_slippi_replay (id)
        )`).run().finalize();
        db.prepare(`CREATE TABLE IF NOT EXISTS slippi_overall (
            id INTEGER NOT NULL, 
            player_slippi_replay_id INTEGER NOT NULL, 
            input_counts INTEGER, 
            total_damage FLOAT, 
            kill_count INTEGER, 
            successful_conversions INTEGER, 
            successful_conversion_ratio FLOAT, 
            inputs_per_minute FLOAT, 
            digital_inputs_per_minute FLOAT, 
            openings_per_kill FLOAT, 
            damage_per_opening FLOAT, 
            neutral_win_ratio FLOAT, 
            counter_hit_ratio FLOAT, 
            beneficial_trade_ratio FLOAT, 
            datetime DATETIME, 
            PRIMARY KEY (id), 
            FOREIGN KEY(player_slippi_replay_id) REFERENCES player_slippi_replay (id)
        )`).run().finalize();

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
            // player 0 stats
            const p0connect = metadata['0']
            const p0killmoves = calcs.calculate_killmoves(stats, 0);
            const p0killID = calcs.most_common_kill(p0killmoves);
            const p0neutrals = calcs.neutral_openers(stats, 0);
            const p0dmgopen = stats['overall'][0]['damagePerOpening']['ratio'];
            const p0openkill = stats['overall'][0]['openingsPerKill']['ratio'];
            //player 1 stats
            const p1killmoves = calcs.calculate_killmoves(stats, 1);
            const p1killID = calcs.most_common_kill(p1killmoves);
            const p1neutrals = calcs.neutral_openers(stats, 1);
            const p1dmgopen = stats['overall'][1]['damagePerOpening']['ratio'];
            const p1openkill = stats['overall'][1]['openingsPerKill']['ratio'];


            const winner = calcs.getWinner(game, stats, settings);
            if (winner != false){
                let sqlplayer = `INSERT INTO player_rating
                ( id, connect_code, datetime, rating) VALUES ( ?, ?, ?, ? )`;
                let sqlplayerslippireplay = `INSERT INTO player_slippi_replay
                ( id, filename, player_id) VALUES ( ?, ?, ? )`;
                let sqlslippioverall = `INSERT INTO slippi_overall
                ( id, player_slippi_replay_id, input_counts, total_damage, kill_count, successful_conversions, successful_conversion_ratio, inputs_per_minute, digital_inputs_per_minute, openings_per_kill
                    , damage_per_opening, neutral_win_ratio, counter_hit_ratio, beneficial_trade_ratio, datetime) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )`
                let sqlslippiactioncounts = `INSERT INTO slippi_action_counts
                ( id, player_slippi_replay_id, wavedash, waveland, airdodge, dashdance, spotdodge, ledgegrab, roll, lcancel_success_ratio, grab_success, grab_fail, tech_away, tech_in, tech, tech_fail
                    , wall_tech_success_ratio, datetime) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )`;
                let sqlalltimeplayerstats =`INSERT INTO all_time_player_stats
                ( id, connect_code_id, gamesPlayed, gamesWon, maxElo) VALUES ( ?, ?, ?, ?, ? )`;

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