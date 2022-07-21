## @file
# Compare maintainers/reviewers from Maintainer.txt and CODEOWERS/REVIEWERS
#
# Copyright (c) 2022, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import sys
import json
import GetMaintainer
from codeowners import CodeOwners
from git import Git

SECTIONS = GetMaintainer.parse_maintainers_file('Maintainers.txt')

def GetOwners(File):
    List = GetMaintainer.get_maintainers(File, SECTIONS)
    Maintainers = []
    Reviewers = []
    for Item in List:
      if Item.startswith('M:'):
        if '[' in Item:
          Maintainers.append('@' + Item.rsplit('[')[1].rsplit(']')[0])
        else:
          Maintainers.append(Item.rsplit('<')[1].rsplit('>')[0])
      if Item.startswith('R:'):
        if '[' in Item:
          Reviewers.append('@' + Item.rsplit('[')[1].rsplit(']')[0])
        else:
          Reviewers.append(Item.rsplit('<')[1].rsplit('>')[0])
    Maintainers = list(set(Maintainers))
    Reviewers = list(set(Reviewers))
    Maintainers.sort()
    Reviewers.sort()
    return Maintainers, Reviewers

try:
    owners    = CodeOwners(open('.github/CODEOWNERS').read())
except:
    sys.exit(".github/CODEOWNERS invalid syntax")
try:
    reviewers = CodeOwners(open('.github/REVIEWERS').read())
except:
    sys.exit(".github/REVIEWERS invalid syntax")

NoMaintainers = 0
Mismatches = 0
for File in Git('.').ls_files().split():
  Maintainers, Reviewers = GetOwners (File)
  CodeOwnersMaintainers = [x[1] for x in owners.of (File)]
  CodeOwnersMaintainers.sort()
  if CodeOwnersMaintainers == [] and Maintainers == []:
      print ('M:',File, 'CO:', CodeOwnersMaintainers, 'Maint:', Maintainers)
      NoMaintainers = NoMaintainers + 1
  if CodeOwnersMaintainers != Maintainers:
      print ('M:',File, 'CO:', CodeOwnersMaintainers, 'Maint:', Maintainers)
      Mismatches = Mismatches + 1
  CodeOwnersReviewers = [x[1] for x in reviewers.of (File)]
  CodeOwnersReviewers.sort()
  if CodeOwnersReviewers != Reviewers:
      print ('R:',File, 'CO:', CodeOwnersReviewers, 'Maint:', Reviewers)
      Mismatches = Mismatches + 1

if NoMaintainers > 0 or Mismatches > 0:
    sys.exit("%d no maintainers.  %d mismatches" % (NoMaintainers, Mismatches))

print ('All files have a maintainer.  No mismatches')