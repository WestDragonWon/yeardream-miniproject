#!/bin/bash

#run all models
echo "run all models ... "
DIRECTORY="/home/ubuntu/yeardream-miniproject/instance4/ml/models"

echo "pyenv activating ... "
pyenv activate mlenv
for file in "$DIRECTORY"/*.py; do
    python "$file"
done
echo "pyenv deactivating ... "
pyenv deactivate

#git push
echo "git push ... "
BRANCH="instance4"
#ORIGIN_BRANCH="instance4"
COMMIT_MESSAGE="model created or edited"

git add /home/ubuntu/yeardream-miniproject/instance4/ml/models/.
git commit -m "$COMMIT_MESSAGE - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin "$BRANCH"
