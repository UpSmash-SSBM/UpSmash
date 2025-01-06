const myDropzone = new Dropzone("#dropzone", {
    url: "/upload_slp",
    createImageThumbnails: false,
    acceptedFiles: ".slp",
    addRemoveLinks: false,
    disablePreviews: true,
    parallelUploads: 10,
    uploadMultiple: true,
    init: function() {
        this.hiddenFileInput.setAttribute("webkitdirectory", true);
    }
})