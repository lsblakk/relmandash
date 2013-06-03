from bugzilla.models import *
from bugzilla.utils import *
from bugzilla.agents import *


def getBugDependencies(bug, bmoagent, include_fields='_default,depends_on', exclude_fields=None):
    dependencies = []
    if bug is not None:
        for dependency in bug.depends_on:
            dependencies.append(bmoagent.get_bug(dependency, include_fields, exclude_fields))
    else:
        raise Exception('invalid bug')
    return dependencies


def getBugBlocks(bug, bmoagent, include_fields='_default,blocks', exclude_fields=None):
    dependencies = []
    if bug is not None:
        for blocked in bug.blocks:
            dependencies.append(bmoagent.get_bug(blocked, include_fields, exclude_fields))
    else:
        raise Exception('invalid bug')
    return dependencies
