const FormData = require('form-data');
const fs = require('fs');
const { request } = require('http');
const https = require('node:https');

//calls api for uploading files
const SLPoptions = {
    hostname:'www.upsmash.net',
    port: '443',
    path: '/upload_slp',
    method: 'POST'
};

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
            console.log(filesToSend[current_num])
            const readStream = fs.createReadStream(filesToSend[current_num]);
            let readStreamSplitPath = readStream['path'].split('\\')
            form.append(readStreamSplitPath[readStreamSplitPath.length - 1], readStream);
        }
        //console.log('end batch')
        SLPoptions['headers'] = form.getHeaders();
        const req = https.request(SLPoptions, (response) => {
            response.setEncoding('utf8');
            response.on('end', () => {
                // console.log('No more data in response.');
            });
            req.end();
        });
        req.on('error', (err) => {
            console.log(err);
        });
        form.pipe(req);
        batchStartNum = current_num;
    }
}

module.exports = { file_submit };