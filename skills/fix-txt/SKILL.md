---
name: fix-txt
description: "A user-triggered skill for fixing text (grammar check, tidying, rephrasing)."
metadata:
  version: "1.0"
  author: Chan Chi Kit
  category: []
---

## Usage:
The user can request to fix text in the format: `/fix-txt [...] `
Example: "/fix-txt --no-foot-print -gtf --goal=publishable @/text/location"

## Modes:

#### --no-footprint -n:
- Do the minimal adjustments that leave (absolute) zero foot-print of you. (keep user's tone, vocabulary level, sentence structure, ..., any text natures)
- If no-footprint is impossible, then notify the user with a possible trade-off plan. Eg, not enough valid text/references from the user.

#### --propose-only -p:
- Propose instead of editing directly. The default option depends on context.

#### --tidy -t:
- Tidy up text, including removing "uhh..., hmm", compressing "the xxx, uhh... I mean the yyy"

#### --grammar -g:
- Fix grammar (mechanical)

#### --format -f:
- Fix format

#### --make-sense:
- make sure the whole thing make sense. You might want to communicate with the user in case it's necessary.

## Reminder
You can decide more modes based on the goal of the user.