#!/bin/bash -e

if ! git diff-index --quiet HEAD --; then
    echo "Local changes not commited. Aborting release."
    exit 1
fi

git checkout release && git rebase master

cd web/frontend && yarn && yarn build && cd ../..

git add web/frontend/builds && git commit -m "Check in built bundles"

git push && git checkout master
