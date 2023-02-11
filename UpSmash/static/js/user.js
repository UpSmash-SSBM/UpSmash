
$(document).ready(function() {

    
    $(document).on("click",".detailButton",function() {
        var parent = $(this).parents('#match').first();
        parent.find("#matchDetail").toggle();

    });

});
