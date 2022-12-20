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
            beneficial_trades FLOAT,
            PRIMARY KEY (id), 
            FOREIGN KEY(player_slippi_replay_id) REFERENCES player_slippi_replay (id)
        )`).run().finalize();
    });
    fs.readdir(input_folder, function (err, files) {
        if (err) {
            console.log("Unable to scan directory: " + err);
        }
        files.forEach(function (file) {
            const game = new SlippiGame(input_folder + file);
            const settings = game.getSettings();
            const metadata = game.getMetadata();
            const stats = game.getStats();
            const winner = calcs.getWinner(game, stats, settings);
            if (winner != false){
                let file_sub = file.substring(0,20);
                // player 0 stats
                const p0connect = metadata['players'][0]['names']['code'];
                const p0username = metadata['players'][0]['names']['netplay'];
                const p0data = ['', p0connect, p0username];
                // overall data
                const p0dmgopen = stats['overall'][0]['damagePerOpening']['ratio'];
                const p0openkill = stats['overall'][0]['openingsPerKill']['ratio'];
                const p0inputs = stats['overall'][0]['inputCounts']['total'];
                const p0totdmg = stats['overall'][0]['totalDamage'];
                const p0kill_count = stats['overall'][0]['killCount'];
                const p0conver_count = stats['overall'][0]['successfulConversions']['count'];
                const p0conver_ratio = stats['overall'][0]['successfulConversions']['ratio'];
                const p0ipm = stats['overall'][0]['inputsPerMinute']['total'];
                const p0dipm = stats['overall'][0]['digitalInputsPerMinute']['total'];
                const p0neutralratio = stats['overall'][0]['neutralWinRatio']['ratio'];
                const p0counterratio = stats['overall'][0]['counterHitRatio']['ratio'];
                const p0bt =  stats['overall'][0]['beneficialTradeRatio']['count'];
                const p0btot =  stats['overall'][0]['beneficialTradeRatio']['total'];
                // plot data
                const p0killmoves = calcs.calculate_killmoves(stats, 0);
                const p0killID = calcs.most_common_kill(p0killmoves);
                const p0neutrals = calcs.neutral_openers(stats, 0);
                // create the data array
                const p0_overall = ['', p0dmgopen, p0openkill, p0inputs, p0totdmg, p0kill_count, p0conver_count, 
                p0conver_ratio, p0ipm, p0dipm, p0neutralratio, p0counterratio, p0bt, p0btot, p0killID['shortName'], p0neutrals['shortName']];
                // action counts 
                const p0wavedash = stats['actionCounts'][0]['wavedashCount'];
                const p0waveland = stats['actionCounts'][0]['wavelandCount'];
                const p0airdodge = stats['actionCounts'][0]['airDodgeCount'];
                const p0dashdance= stats['actionCounts'][0]['dashDanceCount'];
                const p0spotdodge = stats['actionCounts'][0]['spotDodgeCount'];
                const p0ledgegrab = stats['actionCounts'][0]['ledgegrabCount'];
                const p0roll = stats['actionCounts'][0]['rollCount'];
                const p0lcancelratio =stats['actionCounts'][0]['lCancelCount']['success'] / (stats['actionCounts'][0]['lCancelCount']['success'] + stats['actionCounts'][0]['lCancelCount']['fail']);
                const p0grab_success = stats['actionCounts'][0]['grabCount']['success'];
                const p0grab_fail = stats['actionCounts'][0]['grabCount']['fail'];
                const p0tech_away = stats['actionCounts'][0]['groundTechCount']['away'];
                const p0tech_in = stats['actionCounts'][0]['groundTechCount']['in'];
                const p0tech = stats['actionCounts'][0]['groundTechCount']['neutral'];
                const p0tech_fail = stats['actionCounts'][0]['groundTechCount']['fail'];
                const p0walltech_ratio = stats['actionCounts'][0]['wallTechCount']['success'] / (stats['actionCounts'][0]['wallTechCount']['success'] + stats['actionCounts'][0]['wallTechCount']['fail']);
                if (isNaN(p0lcancelratio) != false && isNaN(p0walltech_ratio) != false) {
                    const p0_action_count = ['', p0wavedash, p0waveland,p0airdodge,p0dashdance,p0spotdodge ,p0ledgegrab,p0roll,p0lcancelratio,
                    p0grab_success,p0grab_fail,p0tech_away,p0tech_in,p0tech,p0tech_fail,p0walltech_ratio];
                } else {
                    const p0_action_count = ['', p0wavedash, p0waveland,p0airdodge,p0dashdance,p0spotdodge ,p0ledgegrab,p0roll,0,
                    p0grab_success,p0grab_fail,p0tech_away,p0tech_in,p0tech,p0tech_fail,0];
                }

                //player 1 stats
                const p1connect = metadata['players'][1]['names']['code'];
                const p1username = metadata['players'][1]['names']['netplay'];
                const p1data = ['', p0connect, p0username];
                // p1 stats 
                const p1dmgopen = stats['overall'][1]['damagePerOpening']['ratio'];
                const p1openkill = stats['overall'][1]['openingsPerKill']['ratio'];
                const p1inputs = stats['overall'][1]['inputCounts']['total'];
                const p1totdmg = stats['overall'][1]['totalDamage'];
                const p1kill_count = stats['overall'][1]['killCount'];
                const p1conver_count = stats['overall'][1]['successfulConversions']['count'];
                const p1conver_ratio = stats['overall'][1]['successfulConversions']['ratio'];
                const p1ipm = stats['overall'][1]['inputsPerMinute']['total'];
                const p1dipm = stats['overall'][1]['digitalInputsPerMinute']['total'];
                const p1neutralratio = stats['overall'][1]['neutralWinRatio']['ratio'];
                const p1counterratio = stats['overall'][1]['counterHitRatio']['ratio'];
                const p1bt =  stats['overall'][1]['beneficialTradeRatio']['count'];
                const p1btot =  stats['overall'][1]['beneficialTradeRatio']['total'];
                // p1 plot data
                const p1killmoves = calcs.calculate_killmoves(stats, 1);
                const p1killID = calcs.most_common_kill(p1killmoves);
                const p1neutrals = calcs.neutral_openers(stats, 1);
                const p1_overall = ['', p1dmgopen, p1openkill, p1inputs, p1totdmg, p1kill_count, p1conver_count, 
                p1conver_ratio, p1ipm, p1dipm, p1neutralratio, p1counterratio, p1bt, p1btot, p1killID['shortName'], p1neutrals['shortName']];
                // p1 action count
                const p1wavedash = stats['actionCounts'][1]['wavedashCount'];
                const p1waveland = stats['actionCounts'][1]['wavelandCount'];
                const p1airdodge = stats['actionCounts'][1]['airDodgeCount'];
                const p1dashdance= stats['actionCounts'][1]['dashDanceCount'];
                const p1spotdodge = stats['actionCounts'][1]['spotDodgeCount'];
                const p1ledgegrab = stats['actionCounts'][1]['ledgegrabCount'];
                const p1roll = stats['actionCounts'][1]['rollCount'];
                const p1lcancelratio =stats['actionCounts'][1]['lCancelCount']['success'] / (stats['actionCounts'][1]['lCancelCount']['success'] + stats['actionCounts'][1]['lCancelCount']['fail']);
                const p1grab_success = stats['actionCounts'][1]['grabCount']['success'];
                const p1grab_fail = stats['actionCounts'][1]['grabCount']['fail'];
                const p1tech_away = stats['actionCounts'][1]['groundTechCount']['away'];
                const p1tech_in = stats['actionCounts'][1]['groundTechCount']['in'];
                const p1tech = stats['actionCounts'][1]['groundTechCount']['neutral'];
                const p1tech_fail = stats['actionCounts'][1]['groundTechCount']['fail'];
                const p1walltech_ratio = stats['actionCounts'][1]['wallTechCount']['success'] / (stats['actionCounts'][1]['wallTechCount']['success'] + stats['actionCounts'][1]['wallTechCount']['fail']);
                if (isNaN(p1lcancelratio) != false && isNaN(p1walltech_ratio) != false) {
                    const p1_action_count = ['', p1wavedash, p1waveland,p1airdodge,p1dashdance,p1spotdodge ,p1ledgegrab,p1roll,p1lcancelratio,
                    p1grab_success,p1grab_fail,p1tech_away,p1tech_in,p1tech,p1tech_fail,p1walltech_ratio];
                } else {
                    const p1_action_count = ['', p1wavedash, p1waveland,p1airdodge,p1dashdance,p1spotdodge ,p1ledgegrab,p1roll,0,
                    p1grab_success,p1grab_fail,p1tech_away,p1tech_in,p1tech,p1tech_fail,0];
                };
                // slippi replay data
                const p0slpreplay = ['', file_sub, p0connect]
                const p1slpreplay = ['', file_sub, p1connect]
                let sqlplayer = `INSERT INTO player_rating
                ( id, connect_code, datetime, rating) VALUES ( ?, ?, ?, ? )`;
                let sqlplayerslippireplay = `INSERT INTO player_slippi_replay
                ( id, filename, player_id) VALUES ( ?, ?, ? )`;
                let sqlslippioverall = `INSERT INTO slippi_overall
                ( id, player_slippi_replay_id, input_counts, total_damage, kill_count, successful_conversions, successful_conversion_ratio, inputs_per_minute, digital_inputs_per_minute, openings_per_kill
                    , damage_per_opening, neutral_win_ratio, counter_hit_ratio,  beneficial_trades) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )`
                let sqlslippiactioncounts = `INSERT INTO slippi_action_counts
                ( id, player_slippi_replay_id, wavedash, waveland, airdodge, dashdance, spotdodge, ledgegrab, roll, lcancel_success_ratio, grab_success, grab_fail, tech_away, tech_in, tech, tech_fail
                    , wall_tech_success_ratio, datetime) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )`;
                let sqlalltimeplayerstats =`INSERT INTO all_time_player_stats
                ( id, connect_code_id, gamesPlayed, gamesWon, maxElo) VALUES ( ?, ?, ?, ?, ? )`;
                if(typeof p0data !== "undefined" && typeof p1data !== "undefined" && typeof p0slpreplay !== "undefined" && typeof p1slpreplay !== "undefined" && typeof p0_overall !== "undefined" && typeof p1_overall !== "undefined" &&  typeof p0_action_count !== "undefined" && p1_action_count !== "undefined"){
                    db.serialize(function() {
                        db.run(sqlplayer, p0data, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlplayerslippireplay, p0slpreplay, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlslippioverall, p0_overall, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlslippiactioncounts, p0_action_count, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlplayer, p1data, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlplayerslippireplay, p1slpreplay, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlslippioverall, p1_overall, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                        db.run(sqlslippiactioncounts, p1_action_count, function(err) {
                            if (err){
                                console.log(err);
                            }
                            console.log(`Row(s) updates: ${this.changes}`);
                        });
                    });
                }
                else{
                    setTimeout(waitForElement, 250);
                };
            } else {
                console.log('GAME DID NOT COMPLETE')
            };
        });
    });
};