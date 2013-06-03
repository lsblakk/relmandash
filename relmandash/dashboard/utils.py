from options import getNeedsInfo


def getTrackedBugs(version=0, buglist=[]):
    tracked_bugs = []
    if version != 0 and buglist != []:
        untracked_statuses = ['fixed', 'wontfix', 'verified', 'disabled', 'unaffected', 'verified disabled']
        for bug in buglist:
            is_tracked = False
            if isTracked(bug, version):
                status = getattr(bug, 'cf_status_firefox'+str(version))
                if status not in untracked_statuses:
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


def getToNominateBugs(beta, aurora, buglist=[]):
    to_nominate = []
    if buglist != []:
        try:
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
        except:
            pass
        print len(to_nominate)
    return to_nominate


def getToApproveBugs(buglist=[]):
    to_approve = []
    if buglist != []:
        for bug in buglist:
            isToApprove = False
            if bug.attachments:
                for attachment in bug.attachments:
                    if attachment.flags:
                        for flag in attachment.flags:
                            if flag.name == 'approval-mozilla-beta' and flag.status == '?':
                                isToApprove = True
                            elif flag.name == 'approval-mozilla-aurora' and flag.status == '?':
                                isToApprove = True
                if isToApprove:
                    to_approve.append(bug)
    return to_approve


def getToUpliftBugs(beta, aurora, buglist=[]):
    to_uplift = []
    if buglist != []:
        try:
            for bug in buglist:
                isToUplift = False
                statusBeta = getattr(bug, 'cf_status_firefox'+str(beta))
                statusAurora = getattr(bug, 'cf_status_firefox'+str(aurora))
                trackedBeta = isTracked(bug, beta) and statusBeta != 'verified' and statusBeta != 'disabled' and statusBeta != 'fixed'
                trackedAurora = isTracked(bug, aurora) and statusAurora != 'verified' and statusAurora != 'disabled' and statusAurora != 'fixed'
                if trackedBeta or trackedAurora:
                    if bug.attachments:
                        for attachment in bug.attachments:
                            print attachment
                            if not attachment.is_obsolete and attachment.flags:
                                for flag in attachment.flags:
                                    if flag.name == 'approval-mozilla-beta' and flag.status == '+' and trackedBeta:
                                        isToUplift = True
                                    elif flag.name == 'approval-mozilla-aurora' and flag.status == '+' and trackedAurora:
                                        isToUplift = True
                if isToUplift:
                    to_uplift.append(bug)
        except Exception, e:
            raise Exception('Retrieving bugs to be uplifted failed: '+str(e))
    return to_uplift


def getNeedsInfoBugs(buglist=[], emails='', bmo=None, vt=None):
    needs_info = []
    if emails != '':
        needsInfoOptions = getNeedsInfo(emails, vt)
        try:
            buglist = bmo.get_bug_list(needsInfoOptions)
        except:
            raise Exception('Bad query: Possible reasons might include bad authentication, results too large, or just plain bad query.')
    for bug in buglist:
        if bug.flags:
            for flag in bug.flags:
                if flag.name == 'needinfo' and bug not in needs_info and (isTracked(bug, vt.beta) or isTracked(bug, vt.aurora) or isTracked(bug, vt.esr)):
                    needs_info.append(bug)
    return needs_info


def getUnassignedBugs(buglist):
    unassigned = []
    unassigned_names = ['nobody', 'nobody@mozilla.org', 'general']
    for bug in buglist:
        if bug.assigned_to.name in unassigned_names:
            unassigned.append(bug)
    return unassigned


def getKeywords(buglist):
    keywords = []
    for bug in buglist:
        for keyword in bug.keywords:
            if keyword not in keywords:
                keywords.append(keyword)
    return keywords


def getComponents(buglist):
    components = []
    for bug in buglist:
        if bug.component not in components:
            components.append(bug.component)
    components.sort()
    return components


def isTracked(bug, version):
    try:
        return (getattr(bug, 'cf_tracking_firefox'+str(version)) == '+'
                and (getattr(bug, 'cf_status_firefox'+str(version)) == 'affected'
                or getattr(bug, 'cf_status_firefox'+str(version)) == '---'))
    except AttributeError:
        print 'bug version ' + str(version) + 'does not exist'
    return False
