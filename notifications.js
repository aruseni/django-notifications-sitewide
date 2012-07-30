$.extend($.easing,
{
    easeOutCubic: function (x, t, b, c, d) {
        return c*((t=t/d-1)*t*t + 1) + b;
    }
});

function set_cookie(name, value, expires) {
    var today = new Date();
    var expiration_datetime = new Date(today.getTime() + expires * 24 * 60 * 60 * 1000);
        document.cookie = name + "=" + escape(value) + "; expires=" + expiration_datetime.toGMTString() + "; path=/;";
}

$(document).ready(function() {
    // Top notifications
    $("div.top_notification a.dismiss").click(function(event) {
        event.preventDefault();
        set_cookie("closed_notification_timestamp", $(this).parent().data("timestamp"), 7);
        $(this).fadeOut("fast");
        $("div.top_notification").slideUp("slow", "easeOutCubic", function() {
            $("div.show_notification").fadeIn("slow");
        });
    });

    $("div.show_notification a").click(function(event) {
        event.preventDefault();
        $("div.top_notification").slideDown("slow", "easeOutCubic", function() {
            $("div.top_notification a.dismiss").fadeIn("slow");
            $("div.show_notification").fadeOut("slow");
        });
    });
});
