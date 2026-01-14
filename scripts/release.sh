#!/bin/bash -e

if ! git diff-index --quiet HEAD --; then
    echo "Local changes not commited. Aborting release."
    exit 1
fi

git checkout pre-release
git merge master

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd frontend
nvm use
npm install
npm run build
cd ..

git add frontend/builds
git commit -m "Check in built bundles"

git push
git checkout master
