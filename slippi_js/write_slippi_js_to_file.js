const { SlippiGame } = require("@slippi/slippi-js");
const fs = require("fs");
//import "chartjs-plugin-labels";
//import Chart from "chart.js";
//const { Chart } = require("chart.js");

class Slpdata {
  constructor(settings, meta, stats) {
    this.settings = settings
    this.meta = meta
    this.stats = stats
  }
}
class SlippiSettings{
  constructor(settings) {
    this.gameMode = settings["gameMode"];
    this.isPAL = settings["isPAL"];
    this.isTeams = settings["isTeams"];
    this.language = settings["language"];
    this.player1Settings = settings["players"][0];
    this.player2Settings = settings["players"][1];
    this.scene = settings["scene"];
    this.slpVersion = settings["slpVersion"];
    this.stageId = settings["stageId"]

  }
}
class SlippiMeta {
  constructor(metadata) {
      this.lastFrame = metadata["lastFrame"];
      this.playedOn = metadata["playedOn"];
      this.netplay1 = metadata["players"][0]["names"]["netplay"];
      this.netplay2 =  metadata["players"][1]["names"]["netplay"];
      this.code1 = metadata["players"][0]["names"]["code"];
      this.code2 = metadata["players"][1]["names"]["code"];
      this.character1 = metadata["players"][0]["characters"];
      this.character2 = metadata["players"][1]["characters"];
  }
}
class SlippiStats{
  constructor(stats) {
    this.stats = stats
    this.actionCounts = stats["actionCounts"]
    this.combos = stats["combos"]
    this.conversions = stats["conversions"]
    this.overall = stats["overall"]
    this.stocks = stats["stocks"]
  }
}
class SlippiPlayerStats extends SlippiStats{
  constructor(stats, playerID) {
      super(stats);
      this.airDodge = this.actionCounts[playerID]["airDodgeCount"];
      this.dashDance = this.actionCounts[playerID]["dashDanceCount"];
      this.grabFail = this.actionCounts[playerID]["grabCount"]["fail"];
      this.grabSuccess = this.actionCounts[playerID]["grabCount"]["success"];
      this.groundTechAway = this.actionCounts[playerID]["groundTechCount"]["away"];
      this.groundTechIn = this.actionCounts[playerID]["groundTechCount"]["in"];
      this.groundTechNeutral = this.actionCounts[playerID]["groundTechCount"]["neutral"];
      this.groundTechFail = this.actionCounts[playerID]["groundTechCount"]["fail"];
      this.lCancelSuccess = this.actionCounts[playerID]["lCancelCount"]["success"];
      this.lCancelFail = this.actionCounts[playerID]["lCancelCount"]["fail"];
      this.ledgegrabCount = this.actionCounts[playerID]["ledgegrabCount"];
      this.playerIndex = this.actionCounts[playerID]["playerIndex"];
      this.rollCount = this.actionCounts[playerID]["rollCount"];
      this.spotDodgeCount = this.actionCounts[playerID]["spotDodgeCount"];
      this.upThrow = this.actionCounts[playerID]["throwCount"]["up"];
      this.forwardThrow = this.actionCounts[playerID]["throwCount"]["forward"];
      this.backThrow = this.actionCounts[playerID]["throwCount"]["back"];
      this.downThrow = this.actionCounts[playerID]["throwCount"]["down"];
      this.wallTechSuccess = this.actionCounts[playerID]["wallTechCount"]["success"];
      this.wallTechFail = this.actionCounts[playerID]["wallTechCount"]["fail"];
      this.wavedashCount = this.actionCounts[playerID]["wavedashCount"];
      this.wavelandCount = this.actionCounts[playerID]["wavelandCount"];
      this.bair = this.actionCounts[playerID]["attackCount"]["bair"];
      this.dair = this.actionCounts[playerID]["attackCount"]["dair"];
      this.dash = this.actionCounts[playerID]["attackCount"]["dash"];
      this.dsmash = this.actionCounts[playerID]["attackCount"]["dsmash"];
      this.dtilt = this.actionCounts[playerID]["attackCount"]["dtilt"];
      this.fair = this.actionCounts[playerID]["attackCount"]["fair"];
      this.fsmash = this.actionCounts[playerID]["attackCount"]["fsmash"];
      this.ftilt = this.actionCounts[playerID]["attackCount"]["ftilt"];
      this.jab1 = this.actionCounts[playerID]["attackCount"]["jab1"];
      this.jab2 = this.actionCounts[playerID]["attackCount"]["jab2"];
      this.jab3 = this.actionCounts[playerID]["attackCount"]["jab3"];
      this.jabm = this.actionCounts[playerID]["attackCount"]["jabm"];
      this.nair = this.actionCounts[playerID]["attackCount"]["nair"];
      this.uair = this.actionCounts[playerID]["attackCount"]["uair"];
      this.usmash = this.actionCounts[playerID]["attackCount"]["usmash"];
      this.utilt = this.actionCounts[playerID]["attackCount"]["utilt"];
      this.damagePerOpening = this.overall[playerID]["damagePerOpening"]["count"]
  }
}

// as a prototype this is harded coded for my local hardrive, but the end prodcut should be pulling the .slp info from an sql database ideally

let input_folder = "C:/Users/Ryan/Documents/Slippi Files/"
getData(input_folder)

function getData(input_folder) {
  fs.readdir(input_folder, function (err, files) {
    data = {};
    //handling error
    if (err) {
        console.log("Unable to scan directory: " + err);
    }
    let str1 = "Reading .slp files from ";
    console.log(str1.concat(input_folder));
    //listing all files using forEach
    files.forEach(function (file) {
        let file_sub = file.substring(0,20);
        const game = new SlippiGame(input_folder + file);
        const settings = game.getSettings();
        const metadata = game.getMetadata();
        const stats = game.getStats();
        data[file_sub] = {"Settings": settings ,"Metadata": metadata , "Stats": stats};
    })
    console.log(data)
    dummy_GameID = "Game_20221201T132125";
    const p1stats = new SlippiPlayerStats(data[dummy_GameID]["Stats"], 0);
    const p2stats = new SlippiPlayerStats(data[dummy_GameID]["Stats"], 1);
    const gameMeta = new SlippiMeta(data[dummy_GameID]["Metadata"]);
    const labels = [gameMeta.netplay1, gameMeta.netplay2]
    const config = {
      type: "bar",
      data: {
        labels: labels,
        datasets :[{
          label: labels[0],
          data: [p1stats.damagePerOpening, p2stats.damagePerOpening],
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(255, 159, 64, 0.2)"
          ],
          borderColor: [
            "rgb(255, 99, 132)",
            "rgb(255, 159, 64)"
          ],
          borderWidth: 1
        }]},
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      },
    };
    var obj = {
      table: []
    };
    obj.table.push(config) 
    var json = JSON.stringify(obj)
    fs.writeFile('graphdata.json', json, (err)=> {
      if (err)
      console.log(err);
    });
  }) 
}
