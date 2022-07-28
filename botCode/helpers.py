import re
from typing import Tuple
from databaseHandling.prototype import dbEntry

def repoValidation(repoPath: str, ) -> dbEntry:
    # TODO: Move this to a separate file
    owner = ""
    repo = ""
    repoLink = ""
    entryContent = dbEntry
    regexMatch = re.match("(?:https://)github.com[:/](.*)[:/](.*)", repoPath)
    if regexMatch:
        # get latest release version
        # insert into db: group 1 is the user+repo name
        ownerAndRepo = regexMatch.groups(1)
        owner = ownerAndRepo[0]
        repo = ownerAndRepo[1]
        entryContent.repoOwner = owner
        entryContent.repoName = repo
        entryContent.repoLink = repoPath
        return entryContent
    elif re.match("(.*)[/](.*)", repoPath):
        regexMatch = re.match("(.*)[/](.*)", repoPath)
        owner = regexMatch.groups(1)[0]
        repo = regexMatch.groups(1)[1]
        repoLink = f"https://github.com/{owner}/{repo}"
        entryContent.repoOwner = owner
        entryContent.repoName = repo
        entryContent.repoLink = repoLink
        return entryContent
    else:
        return dbEntry