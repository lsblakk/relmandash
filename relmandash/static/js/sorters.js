function sortTables(tab) {
    var selected = $("#"+tab+"_sort option:selected").text();
    if (selected == 'Severity') {
        sortSeverity(tab);
    } else if (selected == 'Security') {
        sortSecurity(tab);
    } else if (selected == 'Priority') {
        sortNormal(tab, '.priority', 'desc');
    } else if (selected == 'ID ascending') {
        sortNormal(tab, '.id', 'asc');
    } else if (selected == 'ID descending') {
        sortNormal(tab, '.id', 'desc');
    }
}

function sortSeverity(table){
    var severity = ['blocker', 'critical', 'major', 'normal', 'minor', 'trivial', 'enhancement', ''];
    customSort(table, severity, '.severity', 'asc');
}

function sortSecurity(table){
    var security = ['core-security', 'mozilla-corporation-confidential', ''];
    customSort(table, security, '.security', 'asc');
}

function sortNormal(table, _class, order) {
    $('.'+table+' tbody').each(function(index, list) {
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

function customSort(table, weighting, _class, order) {
    $('.'+table+' tbody').each(function(index, list) {
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
