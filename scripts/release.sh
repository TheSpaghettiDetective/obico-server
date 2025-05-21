#!/bin/bash -e

if ! git diff-index --quiet HEAD --; then
    echo "Local changes not commited. Aborting release."
    exit 1
fi

git checkout pre-release && git merge master

cd frontend && nvm use && yarn && yarn build && cd ..

git add frontend/builds && git commit -m "Check in built bundles"

git push && git checkout master
