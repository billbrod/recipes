#!/usr/bin/env bash
set -euo pipefail

sed -i '/{ #recent }/q' docs/index.md
echo "" >> docs/index.md
echo "|Recipe| Date added|" >> docs/index.md
echo "|------|-----------|" >> docs/index.md
all_files="$(git ls-files docs/recipes/*md)"
for file in ${all_files[*]}; do
    if [[ $file != *"index.md" ]]; then
        recipe_name="$(grep -h '^# ' $file)"
        date="$(grep -h 'Date added' $file)"
        file=${file/docs\///}
        echo "|[${recipe_name/\# /}](${file/.md//})|${date/- Date added: /}|" >> docs/index.md
    fi
done
