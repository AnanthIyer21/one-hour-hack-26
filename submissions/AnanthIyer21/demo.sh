#!/usr/bin/env bash
# Git Roulette demo: a throwaway repo + local bare remote under /tmp only.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="$(mktemp -d /tmp/git-roulette-demo.XXXXXX)"
REPO="$BASE/hackathon-project"
REMOTE="$BASE/remote.git"

export ROULETTE_NONINTERACTIVE=1
export ROULETTE_DUCK_ANSWER="${ROULETTE_DUCK_ANSWER:-yes|idk|it makes every commit a roll of fate decided by whack()|it reroutes the goose away from prod}"

git init -q --bare "$REMOTE"
git init -q "$REPO"
cd "$REPO"
git config user.name "Sleep Deprived Hacker"
git config user.email "hacker@example.com"
git config commit.gpgsign false
git remote add origin "$REMOTE"
python3 "$HERE/roulette.py" install .

commit() {
  local msg="$1" i
  echo "$msg" >> NOTES.md
  git add NOTES.md
  for i in 1 2 3; do
    echo "\$ git commit -m \"$msg\"   (attempt $i)"
    if git commit -q -m "$msg"; then return 0; fi
  done
  echo "(giving up on '$msg' after 3 tries, the fates have spoken)"
}

push() {
  local i
  for i in 1 2 3; do
    echo "\$ git push   (attempt $i)"
    if git push -q origin HEAD:main 2>&1 | grep -v "^error: failed to push\|^hint:"; [ "${PIPESTATUS[0]}" = 0 ]; then return 0; fi
  done
  echo "(the push gods are not listening tonight)"
}

commit "initial commit, it compiles"
commit "fix login bug"
commit "add the duck"
push
commit "remove console.logs before judging"
commit "fix bug in the bug fix"
commit "make the demo not crash"
push
commit "final final FINAL version"
commit "update README at 23:58"
push

echo
echo "\$ python3 roulette.py story"
python3 "$HERE/roulette.py" story .
echo "(demo repo left in $BASE)"
