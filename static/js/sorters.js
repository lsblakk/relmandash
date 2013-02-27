function sortSeverity(table){
    var severity = ['blocker', 'critical', 'major', 'normal', 'minor', 'trivial', 'enhancement', ''];
    customSort(table, severity, '.severity', 'asc');
}

function sortSecurity(table){
    var security = ['core-security', 'mozilla-corporation-confidential', ''];
    customSort(table, security, '.security', 'asc');
}

function sortNormal(table, _class, order) {
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

function customSort(table, weighting, _class, order) {
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
