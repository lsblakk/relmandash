def getAssignedOptions(email):
    options = {
       'email1':            email,
       'email1_type':       'equals',
       'email1_assigned_to':1,
       'order':             'Last Changed',
       'field0-0-0':        'status',
       'type0-0-0':         'equals',
       'value0-0-0':        'NEW',
       'field0-0-1':        'status',
       'type0-0-1':         'equals',
       'value0-0-1':        'ASSIGNED',
       'field0-0-2':        'status',
       'type0-0-2':         'equals',
       'value0-0-2':        'REOPENED',
       'field0-0-3':        'status',
       'type0-0-3':         'equals',
       'value0-0-3':        'UNCONFIRMED',
       'include_fields':    '_all',
    }
    return options
    
def getToCheckIn(email):
    options = {
        'field0-0-0': 'attachment.attacher',
        'type0-0-0': 'equals',
        'value0-0-0': email,
        'field0-1-0': 'whiteboard',
        'type0-1-0': 'not_contains',
        'value0-1-0': 'fixed',
        'field0-2-0': 'flagtypes.name',
        'type0-2-0': 'substring',
        'value0-2-0': 'review+',
        'field0-3-0':        'status',
        'type0-3-0':         'equals',
        'value0-3-0':        'NEW',
        'field0-3-1':        'status',
        'type0-3-1':         'equals',
        'value0-3-1':        'ASSIGNED',
        'field0-3-2':        'status',
        'type0-3-2':         'equals',
        'value0-3-2':        'REOPENED',
        'field0-3-3':        'status',
        'type0-3-3':         'equals',
        'value0-3-3':        'UNCONFIRMED',
        'include_fields': 'id,summary,status,resolution,last_change_time,attachments',
    }
    return options

def getToReview(email):
    options = {
        'field0-0-0': 'attachment.attacher',
        'type0-0-0': 'equals',
        'value0-0-0': email,
        'field0-1-0': 'flagtypes.name',
        'type0-1-0': 'contains',
        'value0-1-0': '?',
        'field0-2-0':        'status',
        'type0-2-0':         'equals',
        'value0-2-0':        'NEW',
        'field0-2-1':        'status',
        'type0-2-1':         'equals',
        'value0-2-1':        'ASSIGNED',
        'field0-2-2':        'status',
        'type0-2-2':         'equals',
        'value0-2-2':        'REOPENED',
        'field0-2-3':        'status',
        'type0-2-3':         'equals',
        'value0-2-3':        'UNCONFIRMED',
        'include_fields': 'id,summary,status,resolution,last_change_time,attachments',
    }
    return options
    
def getToNag(email):
    options = {
        'email1': this.username,
        'email1_type': "equals",
        'email1_assigned_to': 1,
        'order': "changeddate DESC",
        'field0-2-0':        'status',
        'type0-2-0':         'equals',
        'value0-2-0':        'NEW',
        'field0-2-1':        'status',
        'type0-2-1':         'equals',
        'value0-2-1':        'ASSIGNED',
        'field0-2-2':        'status',
        'type0-2-2':         'equals',
        'value0-2-2':        'REOPENED',
        'field0-2-3':        'status',
        'type0-2-3':         'equals',
        'value0-2-3':        'UNCONFIRMED',
        'include_fields': 'id,summary,status,resolution,last_change_time,attachments',
    }
    return options
