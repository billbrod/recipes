#!/usr/bin/env bash
set -euo pipefail

sed -i '/{ #recent }/q' docs/index.md
echo "" >> docs/index.md
all_files="$(git ls-files docs/recipes/*md)"
for file in ${all_files[*]}; do
    if [[ $file != *"index.md" ]]; then
        recipe_name="$(grep -h '^# ' $file)"
        date="$(grep -h 'Date added' $file)"
        echo "- ${recipe_name/\# /}: ${date/- Date added: /}" >> docs/index.md
    fi
done
