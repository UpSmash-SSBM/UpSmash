const FormData = require('form-data');
const fs = require('fs');
const { request } = require('http');

//calls api for uploading files
const SLPoptions = {
    hostname:'localhost',
    port: '5000',
    path: '/upload_slp',
    method: 'POST'
};

// this function submits a list of local files in batches of 10
// any leftovers are submitted after
async function file_submit (item) {
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
                //console.log(response.statusCode);
                response.on('end', () => {
                    // console.log('No more data in response.');
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
            }
            const req = request(SLPoptions, (response) => {
                response.setEncoding('utf8');
                // console.log(response.statusCode);
                response.on('data', (chunk) => {
                    // console.log(chunk)
                });
                response.on('end', () => {
                    // console.log('No more data in response.');
                });
                req.end();
            });
            req.on('error', (err) => {
                console.log(err);
            });
            form.pipe(req);
            break
        }
    }
}

module.exports = { file_submit };