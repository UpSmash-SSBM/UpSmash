const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const { request } = require('http');
const { game_checker } = require('./js_utils/game_watcher');
const { file_submit } = require('./js_utils/file_submit');

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
  file_submit(item)
});

ipcMain.on('parentPath', function(e, item) {  
  console.log("check game before")
  game_checker(item)
  console.log("check game after")
});

// this function submits a list of local files in batches of 10
// any leftovers are submitted after

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
