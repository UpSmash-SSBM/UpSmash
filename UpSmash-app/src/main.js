const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { request } = require('http');
const FormData = require('form-data');
const { formatWithOptions } = require('util');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
//if (require('electron-squirrel-startup')) {
//  app.quit();
//}

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

const options = {
  hostname:'localhost',
  port: '5000',
  path: '/upload_slp',
  method: 'POST'
};

ipcMain.on('fileList', function(e, item){
  var batch = 11;
  var form = new FormData();
  for (files in item) {
    const readStream = fs.createReadStream(item[files]);
    form.append(readStream['path'].split('\\')[readStream['path'].split('\\').length - 1], readStream);
    options['headers'] = form.getHeaders();
    // now make the request to the server if 10 files exist
    if (files % batch == 0 && files != 0) {
      const req = request(options, (response) => {
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
        options['headers'] = form.getHeaders();
        };
      const req = request(options, (response) => {
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
})
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
