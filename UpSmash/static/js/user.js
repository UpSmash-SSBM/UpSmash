
$(document).ready(function() {

    
    $(document).on("click",".detail",function() {
        console.log("hello");
        $(this).children("#matchDetail").toggle();
    });

});
