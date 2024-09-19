#!/bin/bash

#run all models
echo "run all models ... "
DIRECTORY="/home/ubuntu/yeardream-miniproject/instance4/ml/models"

for file in "$DIRECTORY"/*.py; do
    python "$file"
done

#git push
echo "git push ... "
BRANCH="models"
ORIGIN_BRANCH="instance4"
COMMIT_MESSAGE="model created or edited"

git checkout "$BRANCH"
git add /home/ubuntu/yeardream-miniproject/instance4/ml/models/.
git commit -m "$COMMIT_MESSAGE - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin "$BRANCH"
git checkout "$ORIGIN_BRANCH"
