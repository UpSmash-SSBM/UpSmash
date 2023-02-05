const electron = require('electron');
const { ipcRenderer } = electron;
const { SlippiGame } = require("@slippi/slippi-js");
const { request } = require('http');

//function for determing who the local player is
function get_local(fileList) {
    let codes = new Array();
    let mf = 1;
    let m = 0;
    let item;
    for (file_num in fileList) {
        // console.log(file_num)
        let game = new SlippiGame(fileList[file_num])
        let settings = game.getSettings()
        let players = settings['players']
        // This next line is buggy, needs work
        player1_code = players[0]['connectCode']
        player2_code = players[1]['connectCode']
        codes.push(player1_code, player2_code)
    }
    for (let i=0; i<codes.length; i++) {
        for (let j=i; j<codes.length; j++) {
            if (codes[i] == codes[j]){
                m++;
            }
            if (mf<m) {
                mf=m; 
                item = codes[i];
            }
        }
        m=0;
    }
    return item
}
// function for getting a list of players games
async function games_played(connect_code) {
    const game_options = {
        hostname:'localhost',
        port: '5000',
        path: '/player_games/' + connect_code.replace('#','-'),
        method: 'GET'
    };
    let response = await doRequest(game_options, connect_code)
    return response
}

function doRequest(url, connect_code) {
    return new Promise(function (resolve, reject) {
        const req = request(url, (response) => {
            response.setEncoding('utf8');
            console.log(response.statusCode);
            var body = '';
            // catches the servers response and prints it
            response.on('data', (game_list) => {
                body += game_list
            });
            // if the response is over, writes it also
            response.on('end', function() {
                if (response.statusCode == 200) {
                    resolve(body)
                }
            });
        });
        // error processing
        req.on('error', (err) => {
            console.log(err)
            console.log(response.statusCode);
            reject(err);
        });
        // send the actual data
        req.write(connect_code);
        req.end();
    })
}

// listens for a click change
document.getElementById("slpFolder").addEventListener("change", (event) => {
    // variables to write to in the display in order to tell the user how many files have been uploaded
    let output = document.getElementById("listing");
    let item = document.createElement("li");
    // this is the directory where the files are
    let parent = event.target.files[0].path;
    let final = event.target.files[0].path.split('Game')[0]
    var connect_local;
    // adds the file names to the list, after loop will have the full list of files names to upload
    item.textContent = final;
    output.appendChild(item);
    let fileList = new Array();
    let fileSub = new Array();
    for (const file of event.target.files){
        if (file.path.split('.')[file.path.split('.').length - 1] == 'slp') {
            fileList.push(file.path);
            parent = file.path.split('.')[0, file.path.split('.').length - 2];
            sub = parent.split('\\')[parent.split('\\').length - 1];
            fileSub.push(sub)
        }
    }
    console.log(fileList)
    connect_local = get_local(fileList)
    console.log(connect_local)
    let game_list = games_played(connect_local);
    game_list.then((value) => {
        let to_send_final = new Array()
        let to_send = fileSub.filter(function(item) {
            return value.indexOf(item) == -1;
        });
        for (suffix in to_send) {
            let attach = final + '/' + to_send[suffix] + '.slp'
            to_send_final.push(attach)
        }
        console.log(to_send_final)
        if (fileList.length ==  event.target.files.length) {
            ipcRenderer.send("fileList", to_send_final)
            ipcRenderer.send("parentPath", final)
        }; 
    })
}, false);