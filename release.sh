#!/bin/bash -e

if ! git diff-index --quiet HEAD --; then
    echo "Local changes not commited. Aborting release."
    exit 1
fi
git checkout release
git rebase master
git push
git checkout master
