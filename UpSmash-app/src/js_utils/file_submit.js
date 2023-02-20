const FormData = require('form-data');
const fs = require('fs');
const https = require('node:https');

const SLPoptions = {
    hostname:'www.upsmash.net',
    port: '443',
    path: '/upload_slp',
    method: 'POST'
};

async function send_slippi_files(form) {
    SLPoptions['headers'] = form.getHeaders();
    let response = await doFormRequest(SLPoptions, form)
    return response
}

function doFormRequest(options, form) {
    return new Promise(function (resolve, reject) {
        const req = https.request(options, (response) => {
            response.setEncoding('utf8');
            var response_body = '';
            response.on('data', (recieved_data) => {
                response_body += recieved_data
            });
            // if the response is over, writes it also
            response.on('end', function() {
                if (response.statusCode == 200) {
                    resolve(response_body)
                } else { 
                    console.log(response.statusCode)
                }
            });
        });
        // error processing
        req.on('error', (err) => {
            console.log(err)
            console.log(err.statusCode);
            reject(err);
        });
        // send the actual data
        form.pipe(req);
    })
}

// this function submits a list of local files in batches of 10
// any leftovers are submitted after
async function file_submit(filesToSend) {
    var batchLength = 10;
    let batchStartNum = 0;
    let length = filesToSend.length
    while (batchStartNum < length) {
        let form = new FormData();
        let end_num = batchStartNum + batchLength;
        for (var current_num = batchStartNum; current_num < end_num && current_num < length; current_num++) {
            //console.log(current_num)
            // console.log(filesToSend[current_num])
            const readStream = fs.createReadStream(filesToSend[current_num]);
            let readStreamSplitPath = readStream['path'].split('\\')
            form.append(readStreamSplitPath[readStreamSplitPath.length - 1], readStream);
        }
        // console.log('end batch')
        console.log("sending " + batchStartNum)
        SLPoptions['headers'] = form.getHeaders();
        
        await send_slippi_files(form);
        batchStartNum = current_num;
    }
}

module.exports = { file_submit };