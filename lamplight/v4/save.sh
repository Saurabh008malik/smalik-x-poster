#!/bin/bash
# save lamp4 working files to branch work-lamplight-david
set -e
W=/home/claude/workbr
if [ ! -d $W/.git ]; then git clone -q --depth 1 --filter=blob:limit=20m https://github.com/Saurabh008malik/smalik-x-poster $W; cd $W; git config user.name Claude; git config user.email noreply@anthropic.com; (git fetch -q --depth 1 origin work-lamplight-david && git checkout -q -B work-lamplight-david FETCH_HEAD) || git checkout -q -b work-lamplight-david; fi
cd $W; mkdir -p lamplight/v4
(cd /home/claude/lamp4 && find . -type f \( -name "*.txt" -o -name "*.json" -o -name "*.py" -o -name "*.sh" -o -name "*.jpg" -o -name "*.md" \) -not -path "./img/*" -not -path "./web/*" -not -path "./clips/*" -not -path "./shorts/*" -print0 | xargs -0 -I{} cp --parents {} /home/claude/workbr/lamplight/v4/)
git add -A lamplight/v4; git commit -qm "lamplight v4 David: work in progress ($1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
git push -q origin HEAD:work-lamplight-david && echo saved
