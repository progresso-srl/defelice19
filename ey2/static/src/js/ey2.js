$(document).ready(function() {

    $("body").on('hover', ".oe_list_field_binary", function(e) {
        var $a = $(this).find("a");
        $a.removeAttr("download");
    });
});