function recalculateLength() {
    $(".length").each(function(index,list) {
        if ($(list).parent().parent().prop("tagName") == "DIV") {
            $(list).text('(' + $(list).parent().parent().find("tr").length + ')');
        } else if ($(list).parent().parent().prop("tagName") == "LI") {
            $(list).text('(' + $($(list).parent().attr('href')).find("tr").length + ')');
        }
    });
}

function resetTags() {
    $('input:checkbox').removeProp('checked');
    $('#tabs div[aria-expanded="true"]').find("tr").show();
    $('#tabs div[aria-expanded="true"]').find("tr").css("background-color", '#FFFFFF');
    recalculateLength();
}

function colorizeTags() {
    var colors = ['#FFBBBB', '#A3FEBA', '#AAAAFF', '#FFD0BC', '#81F7F3', '#FFFF99', '#A4F0B7', '#FFACEC', '#BAFEA3', '#EAA6EA', '#A9E2F3', '#BBEBFF', '#B4D1B6', '#BCB4F3'];
    $("tag").each(function(index, tag) {
        var color = colors[index];
        $(tag).parent().css('background-color', color);
    });
}

function activateTags() {
    $("tag").click(function() {
        var checkbox = $(this).prev();
        checkbox.prop('checked', !checkbox.prop('checked'));
    });
    
    $("div.filter.keyword > input[type=checkbox]").on( "change", function() {
        var className = $(this).attr('value');
        var selectedPanel = $('#tabs div[aria-expanded="true"]');
        var method = $('#tagmethod option:selected').text();
        
        if (method == 'Highlight') {
            var rows = selectedPanel.find("tr."+className);
            if ($(this).prop('checked') == false) {
                rows.css("background-color", '#FFFFFF');
            } else {
                var originalColor = $(this).parent().css('background-color');
                rows.css("background-color", originalColor);
                if (rows.length == 0) {
                    alert("No bugs with this keyword exists here! Please try another tab :)");
                } 
            }
        } else if (method == 'Filter') {
            if ($("input:checked").length == 0) {
                // show all if none are checked
                selectedPanel.find("tr").show();
            } else {
                // hide all, then display those that have checked keywords
                selectedPanel.find("tr").hide();
                $("input:checked").each(function() {
                    selectedPanel.find("tr."+$(this).val()).show();
                });
            }
        }
        recalculateLength();
    } );
}
