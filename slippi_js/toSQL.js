var sqlite3 = require('sqlite3').verbose();
var fs = require('fs');
var dbFile = '../UpSmash/db.sqlite3';
var dbExists = fs.existsSync(dbFile);
const { SlippiGame } = require("@slippi/slippi-js");
const calcs = require('./stat_calcs');

//This function grabs the player data assciated with p1 or pplayer from a slp file
//input file needs to be the path to the file of intrest. 
function playerInfo(player, input_file) {
    //create the game
    const game = new SlippiGame(input_file);
    const settings = game.getSettings();
    const metadata = game.getMetadata();
    const stats = game.getStats();
    // did someone win the game? (i.e did it complete)
    const winner = calcs.getWinner(game, stats, settings);
    //player meta data
    const playerconnect = metadata['players'][player]['names']['code'];
    const playerusername = metadata['players'][player]['names']['netplay'];
    const playerdata = ['', playerconnect, playerusername];
    //player slp info for parent table
    const file_sub = file.substring(0,20);
    const slpreplay = ['', file_sub, playerconnect]
    // overall data
    const playerdmgopen = stats['overall'][player]['damagePerOpening']['ratio'];
    const playeropenkill = stats['overall'][player]['openingsPerKill']['ratio'];
    const playerinputs = stats['overall'][player]['inputCounts']['total'];
    const playertotdmg = stats['overall'][player]['totalDamage'];
    const playerkill_count = stats['overall'][player]['killCount'];
    const playerconver_count = stats['overall'][player]['successfulConversions']['count'];
    const playerconver_ratio = stats['overall'][player]['successfulConversions']['ratio'];
    const playeripm = stats['overall'][player]['inputsPerMinute']['total'];
    const playerdipm = stats['overall'][player]['digitalInputsPerMinute']['total'];
    const playerneutralratio = stats['overall'][player]['neutralWinRatio']['ratio'];
    const playercounterratio = stats['overall'][player]['counterHitRatio']['ratio'];
    const playerbt =  stats['overall'][player]['beneficialTradeRatio']['count'];
    const playerbtot =  stats['overall'][player]['beneficialTradeRatio']['total'];
    // plot data
    const playerkillmoves = calcs.calculate_killmoves(stats, player);
    const playerkillID = calcs.most_common_kill(playerkillmoves);
    const playerneutrals = calcs.neutral_openers(stats, player);
    // create the data array
    const player_overall = ['', playerdmgopen, playeropenkill, playerinputs, playertotdmg, playerkill_count, playerconver_count, 
    playerconver_ratio, playeripm, playerdipm, playerneutralratio, playercounterratio, playerbt, playerbtot, playerkillID['shortName'], playerneutrals['shortName']];
    // action counts 
    const playerwavedash = stats['actionCounts'][player]['wavedashCount'];
    const playerwaveland = stats['actionCounts'][player]['wavelandCount'];
    const playerairdodge = stats['actionCounts'][player]['airDodgeCount'];
    const playerdashdance= stats['actionCounts'][player]['dashDanceCount'];
    const playerspotdodge = stats['actionCounts'][player]['spotDodgeCount'];
    const playerledgegrab = stats['actionCounts'][player]['ledgegrabCount'];
    const playerroll = stats['actionCounts'][player]['rollCount'];
    const playerlcancelratio =stats['actionCounts'][player]['lCancelCount']['success'] / (stats['actionCounts'][player]['lCancelCount']['success'] + stats['actionCounts'][player]['lCancelCount']['fail']);
    const playergrab_success = stats['actionCounts'][player]['grabCount']['success'];
    const playergrab_fail = stats['actionCounts'][player]['grabCount']['fail'];
    const playertech_away = stats['actionCounts'][player]['groundTechCount']['away'];
    const playertech_in = stats['actionCounts'][player]['groundTechCount']['in'];
    const playertech = stats['actionCounts'][player]['groundTechCount']['neutral'];
    const playertech_fail = stats['actionCounts'][player]['groundTechCount']['fail'];
    const playerwalltech_ratio = stats['actionCounts'][player]['wallTechCount']['success'] / (stats['actionCounts'][player]['wallTechCount']['success'] + stats['actionCounts'][player]['wallTechCount']['fail']);
    // action counts array
    if (isNaN(playerlcancelratio) != false && isNaN(playerwalltech_ratio) != false) {
        const player_action_count = ['', playerwavedash, playerwaveland,playerairdodge,playerdashdance,playerspotdodge ,playerledgegrab,playerroll,playerlcancelratio,
        playergrab_success,playergrab_fail,playertech_away,playertech_in,playertech,playertech_fail,playerwalltech_ratio];
    } else {
        const player_action_count = ['', playerwavedash, playerwaveland,playerairdodge,playerdashdance,playerspotdodge ,playerledgegrab,playerroll,0,
        playergrab_success,playergrab_fail,playertech_away,playertech_in,playertech,playertech_fail,0];
    }
    return winner, slpreplay, playerdata, player_overall, player_action_count
}

//first we need to access the data from the slp file ( or files) that are in our temp folder
function addToSQL(input_file) {
    let db = new sqlite3.Database('../UpSmash/db.sqlite3', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Connected to Upsmash database');
    });
    winner, slpreplay0, player0data, player0_overall, player0_action_count = playerInfo(0, input_file);
    winner, slpreplay1, player1data, player1_overall, player1_action_count = playerInfo(1, input_file);
    if (winner != false){
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
        if(typeof player0data !== "undefined" && typeof player1data !== "undefined" && typeof slpreplay0 !== "undefined" && typeof slpreplay1 !== "undefined" && 
        typeof player0_overall !== "undefined" && typeof player1_overall !== "undefined" &&  typeof player0_action_count !== "undefined" && player1_action_count !== "undefined"){
            db.serialize(function() {
                db.run(sqlplayer, player0data, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlplayerslippireplay, slpreplay0, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlslippioverall, player0_overall, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlslippiactioncounts, player0_action_count, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlplayer, player1data, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlplayerslippireplay, slpreplay1, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlslippioverall, player1_overall, function(err) {
                    if (err){
                        console.log(err);
                    }
                    console.log(`Row(s) updates: ${this.changes}`);
                });
                db.run(sqlslippiactioncounts, player1_action_count, function(err) {
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
};