const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { request } = require('http');
const FormData = require('form-data');
const { formatWithOptions } = require('util');
const chokidar = require('chokidar');
const { SlippiGame } = require("@slippi/slippi-js");
const _ = require("lodash");

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
//if (require('electron-squirrel-startup')) {
//  app.quit();
//}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
    },
  });
  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  //Build Menu from Template
  const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
  //Insert Menu
  Menu.setApplicationMenu(mainMenu);

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow) ;

ipcMain.on('fileList', function(e, item){
  fileSubmit(item)
});

ipcMain.on('parentPath', function(e, item) {  
  const watcher = chokidar.watch(item, {
    ignored: '/*.slp', // TODO: This doesn't work. Use regex?
    depth: 0,
    persistent: true,
    usePolling: true,
    ignoreInitial: true,
  });
  const gameByPath = {};
  let fileList = new Array();
  let player_wins = [0, 0, 0, 0] //Need to reset this when you play a new player
  watcher
    .on('ready', function() {
      console.log('Initial scan complete. Ready for changes')
    })
    .on('add', function(path) { 
      console.log('ADDED')
    })
    .on('change', (path) => {
      console.log("File change");
      // triggers on file being written to
      // intialize the new variables we need
      let gameState, settings, frames, latestFrame, gameEnd;
      try {
        // create the game if it doesn't exist
        let game = _.get(gameByPath, [path, "game"]); //Confused on this, is it trying to create an empty file if it doesnt exist?
        if (!game) {
          // Make sure to enable `processOnTheFly` to get updated stats as the game progresses
          game = new SlippiGame(path, { processOnTheFly: true });
          gameByPath[path] = {
            game: game,
            state: {
              settings: null,
              detectedPunishes: {},
            },
          };
        }
        gameState = _.get(gameByPath, [path, "state"]);
        settings = game.getSettings();
        frames = game.getFrames();
        latestFrame = game.getLatestFrame();
        gameEnd = game.getGameEnd();
        metadata = game.getMetadata();
        writeOp = game.SlpFileWriterOptions
      } catch (err) {
        console.log(err);
        return;
      }

      const matchId = settings['matchInfo']['matchId'];
      const matchSub = matchId.split('.')[1];
      const matchType = matchSub.split('-')[0];
      if (!gameState.settings && settings) {
        console.log("[Game Start] New game has started");
        //console.log(settings);
        gameState.settings = settings;
      } else {
        console.log("Not a new game");
      }
      if ( matchType == 'ranked') { 
        console.log(gameEnd)
        // gameEnd will be null until the game is over
        if (gameEnd) {
          const endTypes = {
            1: "TIME!",
            2: "GAME!",
            7: "No Contest",
          };
          const endMessage = _.get(endTypes, gameEnd.gameEndMethod) || "Unknown";
          const lrasText = gameEnd.gameEndMethod === 7 ? ` | Quitter Index: ${gameEnd.lrasInitiatorIndex}` : "";
          console.log(`[Game Complete] Type: ${endMessage}${lrasText}`)
          // console.log(gameEnd)
          players = settings['players']
          for (let i = 0; i < players.length; i++) {
            player_wins[i] += gameEnd['placements'][i]['position']
            if (player_wins[i] >= 2) {
              player_wins = [0, 0, 0, 0]
              for (let i = 0; i < players.length; i++) {
                rating(players[i]['connectCode'])
              }
            }
          }
          console.log(player_wins)
          fileList.push(path);
          if (fileList.length == 10) {
            fileSubmit(fileList);
          };
        }
      }
    });
  });

//calls api for uploading files
const SLPoptions = {
  hostname:'localhost',
  port: '5000',
  path: '/upload_slp',
  method: 'POST'
};
// this function submits a list of local files in batches of 10
// any leftovers are submitted after

async function fileSubmit (item) {
  var batch = 11;
  var form = new FormData();
  for (files in item) {
    const readStream = fs.createReadStream(item[files]);
    form.append(readStream['path'].split('\\')[readStream['path'].split('\\').length - 1], readStream);
    SLPoptions['headers'] = form.getHeaders();
    // now make the request to the server if 10 files exist
    if (files % batch == 0 && files != 0) {
      const req = request(SLPoptions, (response) => {
        response.setEncoding('utf8');
        console.log(response.statusCode);
        response.on('end', () => {
          console.log('No more data in response.');
        });
        req.end();
      });
      req.on('error', (err) => {
        console.log(err);
      });
      form.pipe(req);
      var form = new FormData();
    } else if ((item.length - files) < batch) {
      const sub_list = item.slice(files);
      const form = new FormData();
      for (sub_files in sub_list){
        const readStream = fs.createReadStream(sub_list[sub_files]);
        form.append(readStream['path'].split('\\')[readStream['path'].split('\\').length - 1], readStream);
        SLPoptions['headers'] = form.getHeaders();
        };
      const req = request(SLPoptions, (response) => {
        response.setEncoding('utf8');
        console.log(response.statusCode);
        response.on('data', (chunk) => {
          console.log(chunk)
        });
        response.on('end', () => {
          console.log('No more data in response.');
        });
        req.end();
      });
      req.on('error', (err) => {
        console.log(err);
      });
      form.pipe(req);
      break
    }
  };
}

async function rating(connect_code) {
  await sleep(5000);
  // this guy is going to actually tell the server to get new rank when its called
  // just submit the new file, and then update the rank server side, don't parse locally
  const rank_options = {
    hostname:'localhost',
    port: '5000',
    path: '/rating/' + connect_code.replace('#','-'),
    method: 'GET'
  };

  const req = request(rank_options, (response) => {
    response.setEncoding('utf8');
    console.log(response.statusCode);
    // catches the servers response and prints it
    response.on('data', (rating_response) => {
      if (response.statusCode == 200) {
        console.log(rating_response);
      }
    });
    // if the response is over, writes it also
    response.on('end', () => {
      //console.log('No more data in response.');
    });
  });
// error processing
  req.on('error', (err) => {
    console.log(response.statusCode);
    //console.log(err);
  });
  // send the actual data
  req.write(connect_code);
  req.end();
  }
// Create menu template 
const mainMenuTemplate = [
  {
    label:'File',
    submenu: [
      {
        label: 'Quit',
        accelerator: process.platform == 'darwin' ? 'Command+Q' :
        'Ctrl+Q',
        click(){
          app.quit();
        }
      }
    ]
  }
];

//If Mac add empty object to menu 
if(process.platform == 'darwin'){
  mainMenuTemplate.unshift({});
}
// Add Dev tools item if not in production
if(process.env.NODE_ENV !== 'production'){
  mainMenuTemplate.push({
    label: 'Dev tools',
    submenu: [
      {
        label: 'Toggle DevTools',
        accelerator: process.platform == 'darwin' ? 'Command+I' :
        'Ctrl+I',
        click(item, focusedWindow){
          focusedWindow.toggleDevTools();
        }
      },
      {
        role: 'reload'
      }
    ]
  });
}
// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
