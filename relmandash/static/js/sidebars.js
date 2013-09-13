function print_filter(type) {
    var keywords = [];
    $("span."+type).each(function(index) {
        var keyword = $(this).text();
        if ($.inArray(keyword,keywords) == -1) {
            keywords.push(keyword);
            var print = keyword;
            if (type == 'component') {
                print = keyword.replace(/_/g,' ');
            }
            $("#"+type+"_container").append('<div class="filter ' + type + '"><input type="checkbox" value="' + keyword + '"/>' + print + ' <span class="filter_length"></span></div>');
        }
    });
    if (keywords.length === 0) {
        $("#"+type+"_container").append('<span class="extra_info">No keywords related.</span>');
    }
}


// try document.getElementsByClass for count instead
function count_filter() {
    $("input[type=checkbox]").attr("disabled", false);
    $(".filter_length").each(function() {
        var rows = 0;
        rows = $("tr[class~='" + $(this).prev().val() + "']").length;
        $(this).text(" ("+rows+")");
        if (rows === 0) {
            $(this).parent().addClass("disabled");
            $(this).prev().attr("disabled", true);
        }
    });
}

function print_countdown(cycle) {
    var date1 = new Date(cycle.substr(0,4),cycle.substr(4,2)-1,cycle.substr(6,2));
    var date2 = new Date(cycle.substr(9,4),cycle.substr(13,2)-1,cycle.substr(15,2));
    var today = new Date();
    var week = ((today - date1)/((1000*60*60*24)+1)/7)+1;
    var countdown = ((date2 - today)/(1000*60*60*24));

    $("#week").text(Math.round(week));
    $("#daysleft").text(Math.round(countdown)+1);
    if (Math.round(countdown)+1 == 1) {
        $("#days").text(" day");
    } else {
        $("#days").text(" days");
    }
}
