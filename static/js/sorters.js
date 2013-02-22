function sortBySeverity(tab){
    var severity = ['blocker', 'critical', 'major', 'normal', 'minor', 'trivial', 'enhancement', ''];
    customSort(tab, severity, '.severity');
}

function sortBySecurity(tab){
    var security = ['core-security', 'mozilla-corporation-confidential', ''];
    customSort(tab, security, '.security');
}

function customSort(tab, weighting, _class) {
    var list = $('#' + tab + ' tbody');
    var listItems = list.children('tr').get();
    list.remove(listItems);
    listItems.sort(function(a,b) {
        var compA = $.inArray($(a).find(_class).text(), weighting);
        var compB = $.inArray($(b).find(_class).text(), weighting);
        return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
    });
    $(list).append(listItems);
}
