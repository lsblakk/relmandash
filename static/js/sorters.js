function sortBySeverity(){
    var severity = ['enhancement', 'trivial', 'minor', 'normal', 'major', 'critical', 'blocker'];
    var list = $('tbody');
    var listItems = list.children('tr').get();
    list.remove(listItems);
    listItems.sort(function(a,b){
    var compA = $.inArray($(a).find('.severity').text(), severity);
    var compB = $.inArray($(b).find('.severity').text(), severity);
    return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
    });
    $(list).append(listItems);
}
