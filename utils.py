def getTrackedBugs(version=0,buglist=[]):
    tracked_bugs = []
    if version != 0 and buglist != []:
        index = 0
        while index < len(buglist):
            is_tracked = False
            bug = buglist[index]
            if isTracked(bug, version):
                status = getattr(bug,'cf_status_firefox'+str(version))
                if status != 'fixed' or status != 'wontfix' or status != 'verified' or status != 'disabled' or status != 'unaffected':
                    is_tracked = True
            if is_tracked:
                bug = buglist.pop(index)
                tracked_bugs.append(bug)
            else:
                index += 1
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
        while index < len(buglist):
            toNominateBeta = False
            toNominateAurora = False
            bug = buglist[index]
            statusBeta = getattr(bug, 'cf_status_firefox'+str(beta))
            statusAurora = getattr(bug, 'cf_status_firefox'+str(aurora))
            trackedBeta = isTracked(bug, beta) and statusBeta != 'verified' and statusBeta != 'disabled' and statusBeta != 'fixed'
            trackedAurora = isTracked(bug, aurora) and statusAurora != 'verified' and statusAurora != 'disabled' and statusAurora != 'fixed'
            if trackedBeta or trackedAurora:
                toNominateBeta = False
                toNominateAurora = False
                if bug.id == 813550:
                    print bug.id
                    print trackedBeta
                    print trackedAurora
                for attachment in bug.attachments:
                    toNominateBeta = True
                    toNominateAurora = True
                    if attachment.id == 703562:
                        print attachment.is_patch
                        print attachment.is_obsolete
                    if attachment.is_patch and not attachment.is_obsolete:
                        for flag in attachment.flags:
                            if trackedBeta and flag.name == 'approval-mozilla-beta':
                                toNominateBeta = False
                            elif trackedAurora and flag.name == 'approval-mozilla-aurora':
                                toNominateAurora = False
            if toNominateBeta or toNominateAurora:
                bug = buglist.pop(index)
                to_nominate.append(bug)
            else:
                index += 1
    return to_nominate
    
def getToApproveBugs(buglist=[]):
    to_approve = []
    if buglist != []:
        index = 0
        while index < len(buglist):
            isToApprove = False
            for attachment in buglist[index].attachments:
                for flag in attachment.flags:
                    if flag.name == 'approval-mozilla-beta' and flag.status == '?':
                        isToApprove = True
                    elif flag.name == 'approval-mozilla-aurora' and flag.status == '?':
                        isToApprove = True
            if isToApprove:
                bug = buglist.pop(index)
                to_approve.append(bug)
            else:
                index += 1
    return to_approve
    
def getToUpliftBugs(beta,aurora,buglist=[]):
    to_uplift = []
    if buglist != []:
        index = 0
        while index < len(buglist):
            isToUplift = False
            bug = buglist[index]
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
                bug = buglist.pop(index)
                to_uplift.append(bug)
            else:
                index += 1
    return to_uplift

def isTracked(bug,version):
    try:
        return (getattr(bug, 'cf_tracking_firefox'+str(version)) == '+'
            and getattr(bug, 'cf_status_firefox'+str(version)) == 'affected' or
            getattr(bug, 'cf_status_firefox'+str(version)) == '')
    except AttributeError:
        print 'bug version ' + str(version) + 'does not exist'
    return False
