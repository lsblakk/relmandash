function recalculateLength() {
    $(".length").each(function() {
        var pp = $(this).parent().parent();
        if (pp.prop("tagName") == "DIV") {
            var rows = pp.find("tbody > tr.show").length;
            if (rows === 0) {
                pp.find(".empty").text("No bugs for current filter");
                //$("thead").hide();
            } else {
                //$("thead").show();
            }
            $(this).text('(' + rows + ')');
        } else if (pp.prop("tagName") == "LI") {
            var rows = $($(this).parent().attr('href')).find("tbody > tr.show").length;
            if (rows === 0 && $($(this).parent().attr('href')).find("div").length === 0) {
                $($(this).parent().attr('href')).find(".empty").text("No bugs for current filter");
                //$("thead").hide();
            } else {
                //$("thead").show();
            }
            $(this).text('(' + rows + ')');
        }
    });
}

function recalculateTotal() {
    $(".empty").text("");
    //$("thead").show();
    var total = 0;
    $(".length").each(function() {
        var pp = $(this).parent().parent();
        if (pp.prop("tagName") == "DIV" && pp.attr("class") != "card") {
            var rows = pp.find("tbody > tr").length;
            if (rows === 0) {
                pp.hide();
            }
            $(this).text('(' + rows + ')');
            $(".length."+pp.attr("id")).text(rows);
        } else if (pp.prop("tagName") == "LI") {
            var href = $(this).parent().attr('href');
            var rows = $(href).find("tbody > tr").length;
            if (rows === 0) {
                if ($(href).find("div").length === 0) {
                    pp.hide();
                } else {
                    $(href).children(".empty").text("No bugs found");
                }
            }
            $(this).text('(' + rows + ')');
            $(".length."+href.substr(1,href.length)).text(rows);
            total += rows;
        }
    });
    if (total === 0) {
        $("#message").text("No bugs found!");
    }
}

function resetTags() {
    $('input:checkbox').removeProp('checked');
    $('#tabs div[aria-expanded="true"]').find("tr").show();
    recalculateTotal();
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
        $(this).prev().prop('checked', !$(this).prev().prop('checked'));
    });

    $("div.filter.keyword > input[type=checkbox]").on( "change", function() {
        if ($("input:checked").length === 0) {
            // show all if none are checked
            //selectedPanel.find("tr").show();
            $("tbody > tr").addClass('show');
            $("tbody > tr").show();
            recalculateTotal();
        } else {
            // hide all, then display those that have checked keywords
            //selectedPanel.find("tr").hide();
            $("tbody > tr").removeClass('show');
            $("tbody > tr").hide();
            $("input:checked").each(function() {
                //selectedPanel.find("tr."+$(this).val()).show();
                $("tbody").find("tr[class~='" + $(this).val() + "']").addClass('show');
                $("tbody").find("tr[class~='" + $(this).val() + "']").show();
            });
            recalculateLength();
        }
    } );
}

function activateComponents() {
    $("div.filter").click(function() {
        $(this).children("input:checkbox")[0].prop('checked', !$(this).children("input:checkbox")[0].prop('checked'));
    });

    $("div.filter > input:checkbox").on( "change", function() {
            if ($("input:checked").length === 0) {
                $("tbody > tr").addClass('show');
                $("tbody > tr").show();
                recalculateTotal();
            } else {
                $("tbody > tr").removeClass('show');
                $("tbody > tr").hide();
                $("input:checked").each(function() {
                    $("tbody").find("tr[class~='" + $(this).val() + "']").addClass('show');
                    $("tbody").find("tr[class~='" + $(this).val() + "']").show();
                });
                recalculateLength();
            }
    } );
}
