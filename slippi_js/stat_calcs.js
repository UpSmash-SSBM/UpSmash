var { moves } = require("@slippi/slippi-js");

function calculate_killmoves(stats, playerIndex) {
    // this calculates the kill move by determining if the conversion that took place is for the player and if it killed.
    // once those are true it goes to the last move in the moves block and pulls the moveID
    const conversions = stats['conversions'];
    let forplayer = conversions.filter(eachObj => eachObj.lastHitBy == playerIndex && eachObj.didKill == true);
    const killmoves= []
    forplayer.forEach((conver) => {
        killmoves.push(conver['moves'].slice(-1)[0]['moveId'])
    })
    return killmoves
};

function most_common_kill(killmoves) {
    // this counts the most occuring moveID and then assigns it to the name of the smash move from the move database in slippi. 
    if(killmoves.length == 0)
        return null;
    var modeMap = {};
    var maxEl = killmoves[0], maxCount = 1;
    for(var i = 0; i < killmoves.length; i++)
    {
        var el = killmoves[i];
        if(modeMap[el] == null)
            modeMap[el] = 1;
        else
            modeMap[el]++;  
        if(modeMap[el] > maxCount)
        {
            maxEl = el;
            maxCount = modeMap[el];
        }
    }
    return moves.getMoveInfo(maxEl);
};

function neutral_openers(stats, playerIndex) {
    const conversions = stats['conversions'];
    let forplayer = conversions.filter(eachObj => eachObj.lastHitBy == playerIndex && eachObj.openingType == 'neutral-win');
    const neutrals= []
    forplayer.forEach((conver) => {
        neutrals.push(conver['moves'].slice(0)[0]['moveId'])
    })
    if(neutrals.length == 0)
        return null;
    var modeMap = {};
    var maxEl = neutrals[0], maxCount = 1;
    for(var i = 0; i < neutrals.length; i++)
    {
        var el = neutrals[i];
        if(modeMap[el] == null)
            modeMap[el] = 1;
        else
            modeMap[el]++;  
        if(modeMap[el] > maxCount)
        {
            maxEl = el;
            maxCount = modeMap[el];
        }
    }
    return moves.getMoveInfo(maxEl)
};

function getWinner(game, stats, settings) {
    finish = stats['gameComplete'];
    if (finish == true) {
        pwin = game.getWinners()[0]['playerIndex']
        return settings['players'][pwin]['connectCode'];
    } else {
        return false;
    }
} 

module.exports = { calculate_killmoves, most_common_kill, neutral_openers, getWinner}