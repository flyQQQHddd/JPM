#!/bin/bash

git add ./ProposalSearcher.py
git add ./proposals.csv
git add ./README.md
git add ./commit.sh
git add ./jvet.sh
git add ./jvet.ps1
git add ./.gitignore
git status

echo "Commit messages: $1"
git commit -m $1