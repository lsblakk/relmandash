function sortCheckerbox() {
    var listItems = $('#checkerbox').children();
    if (listItems.length > 1) {
        $('#checkerbox').children().remove();
        listItems.sort(function(a,b) {
            var compA = Number($(a).find(".length").text());
            var compB = Number($(b).find(".length").text());
            return (compA > compB) ? -1 : (compA < compB) ? 1 : 0;
        });
        $('#checkerbox').append(listItems);
    }
}

function sortTables() {
    var selected = $("#sort option:selected").text();
    if (selected == 'Severity') {
        sortSeverity();
    } else if (selected == 'Security') {
        sortSecurity();
    } else if (selected == 'Priority') {
        sortNormal('.priority', 'desc');
    } else if (selected == 'ID ascending') {
        sortNormal('.id', 'asc');
    } else if (selected == 'ID descending') {
        sortNormal('.id', 'desc');
    } else if (selected == 'Last modified') {
        sortNormal('.modified', 'asc');
    }
}

function sortSeverity(){
    var severity = ['blocker', 'critical', 'major', 'normal', 'minor', 'trivial', 'enhancement', ''];
    customSort(severity, '.severity', 'asc');
}

function sortSecurity(){
    var security = ['core-security', 'mozilla-corporation-confidential', ''];
    customSort(security, '.security', 'asc');
}

function sortNormal(_class, order) {
    $('tbody').each(function(index, list) {
        var listItems = $(list).children('tr');
        if (listItems.length > 1) {
            $(list).remove('tr');
            listItems.sort(function(a,b) {
                var compA = $(a).find(_class).text();
                var compB = $(b).find(_class).text();
                if (order == 'desc') {
                    return (compA > compB) ? -1 : (compA < compB) ? 1 : 0;
                } else {
                    return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
                }
            });
            $(list).append(listItems);
        }
    });
}

function customSort(weighting, _class, order) {
    $('tbody').each(function(index, list) {
        var listItems = $(list).children('tr');
        if (listItems.length > 1) {
            $(list).remove('tr');
            listItems.sort(function(a,b) {
                var compA = $.inArray($(a).find(_class).text(), weighting);
                var compB = $.inArray($(b).find(_class).text(), weighting);
                if (order == 'desc') {
                    return (compA > compB) ? -1 : (compA < compB) ? 1 : 0;
                } else {
                    return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
                }
            });
            $(list).append(listItems);
        }
    });
}
