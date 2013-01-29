#sorts bugs according to certain criteria (more criteria soon)

from bugzilla.models import *
from bugzilla.utils import *
from bugzilla.agents import *

severityWeights = { "enhancement"   : 1,
                    "trivial"       : 2,
                    "minor"         : 3,
                    "normal"        : 4,
                    "major"         : 5,
                    "critical"      : 6,
                    "blocker"       : 7  }

def sortSeverityInc(bug_list)
    bug_list.sort(key=lambda bug:severityWeights[bug.severity])
    
def sortSeverityDesc(bug_list)
    bug_list.sort(key=lambda bug:severityWeights[bug.severity], reverse = true)
