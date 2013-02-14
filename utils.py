def getTrackedBugs(version=0,buglist=[]):
    tracked_bugs = []
    if version != 0 and buglist != []:
        for bug in buglist:
            is_tracked = False
            if isTracked(bug, version):
                status = getattr(bug,'cf_status_firefox'+str(version))
                if status != 'fixed' or status != 'wontfix' or status != 'verified' or status != 'disabled' or status != 'unaffected':
                    is_tracked = True
            if is_tracked:
                tracked_bugs.append(bug)
    return tracked_bugs
    
def getSecurityBugs(buglist=[]):
    security_bugs = []
    if buglist != []:
        index = 0
        while index < len(buglist):
            isSecurityBug = False
            for group in buglist[index].groups:
                if group.name == 'core-security':
                    isSecurityBug = True
                    break
            if isSecurityBug:
                bug = buglist.pop(index)
                security_bugs.append(bug)
            else:
                index += 1
    return security_bugs

def getToNominateBugs(beta,aurora,buglist=[]):
    to_nominate = []
    if buglist != []:
        index = 0
        for bug in buglist:
            statusBeta = getattr(bug, 'cf_status_firefox'+str(beta))
            statusAurora = getattr(bug, 'cf_status_firefox'+str(aurora))
            trackedBeta = isTracked(bug, beta) and statusBeta != 'verified' and statusBeta != 'disabled' and statusBeta != 'fixed' and statusBeta != 'unaffected'
            trackedAurora = isTracked(bug, aurora) and statusAurora != 'verified' and statusAurora != 'disabled' and statusAurora != 'fixed' and statusAurora != 'unaffected'
            if trackedBeta or trackedAurora:
                toNominateBeta = trackedBeta
                toNominateAurora = trackedAurora
                for attachment in bug.attachments:
                    if attachment.is_patch and not attachment.is_obsolete:
                        for flag in attachment.flags:
                            if trackedBeta and flag.name == 'approval-mozilla-beta':
                                toNominateBeta = False
                            elif trackedAurora and flag.name == 'approval-mozilla-aurora':
                                toNominateAurora = False
                if toNominateBeta or toNominateAurora:
                    to_nominate.append(bug)
    return to_nominate
    
def getToApproveBugs(buglist=[]):
    to_approve = []
    if buglist != []:
        index = 0
        for bug in buglist:
            isToApprove = False
            for attachment in bug.attachments:
                for flag in attachment.flags:
                    if flag.name == 'approval-mozilla-beta' and flag.status == '?':
                        isToApprove = True
                    elif flag.name == 'approval-mozilla-aurora' and flag.status == '?':
                        isToApprove = True
            if isToApprove:
                to_approve.append(bug)
    return to_approve
    
def getToUpliftBugs(beta,aurora,buglist=[]):
    to_uplift = []
    if buglist != []:
        index = 0
        for bug in buglist:
            isToUplift = False
            statusBeta = getattr(bug, 'cf_status_firefox'+str(beta))
            statusAurora = getattr(bug, 'cf_status_firefox'+str(aurora))
            trackedBeta = isTracked(bug, beta) and statusBeta != 'verified' and statusBeta != 'disabled' and statusBeta != 'fixed'
            trackedAurora = isTracked(bug, aurora) and statusAurora != 'verified' and statusAurora != 'disabled' and statusAurora != 'fixed'
            if trackedBeta or trackedAurora:
                for attachment in bug.attachments:
                    if attachment.is_patch and not attachment.is_obsolete:
                        for flag in attachment.flags:
                            if flag.name == 'approval-mozilla-beta' and flag.status == '+' and trackedBeta:
                                isToUplift = True
                            elif flag.name == 'approval-mozilla-aurora' and flag.status == '+' and trackedAurora:
                                isToUplift = True
            if isToUplift:
                to_uplift.append(bug)
    return to_uplift
    
def getNeedsInfoBugs(buglist):
    needs_info = []
    for bug in buglist:
        for flag in bug.flags:
            if flag.name == 'needinfo':
                needs_info.append(bug)
    return needs_info
    
def getUnassignedBugs(buglist):
    unassigned = []
    for bug in buglist:
        if bug.assigned_to == 'nobody@mozilla.org' or bug.assigned_to == 'general':
            unassigned.append(bug)
    return unassigned

def getKeywords(buglist):
    keywords = []
    for bug in buglist:
        for keyword in bug.keywords:
            if keyword not in keywords:
                keywords.append(keyword)
    return keywords

def isTracked(bug,version):
    try:
        return (getattr(bug, 'cf_tracking_firefox'+str(version)) == '+'
            and (getattr(bug, 'cf_status_firefox'+str(version)) == 'affected' or
            getattr(bug, 'cf_status_firefox'+str(version)) == '---'))
    except AttributeError:
        print 'bug version ' + str(version) + 'does not exist'
    return False
