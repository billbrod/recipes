#!/usr/bin/env bash
set -euo pipefail

sed -i '/{ #summary }/q' docs/cocktails/index.md
echo "" >> docs/cocktails/index.md
echo "|Recipe|Category|Summary|Date added { data-sort-default } |" >> docs/cocktails/index.md
echo "|------|------|------|-----------|" >> docs/cocktails/index.md
all_files="$(git ls-files docs/cocktails/*md)"
for file in ${all_files[*]}; do
    if [[ $file != *"index.md" ]]; then
        recipe_name="$(grep -h '^# ' $file)"
        date="$(grep -h 'Date added' $file)"
        summary="$(grep -B 1 '#summary' $file | head -n1)"
        # there might be multiple cocktail: tags, and this strips out all the newlines
        category="$(grep ' cocktail:' $file | tr '\n' ',')"
        file=${file/docs\///}
        # the double slash means global substitution (single slash just replaces first occurence)
        echo "|[${recipe_name/\# /}](${file/.md//})|${category//- cocktail:/}|${summary/- /}|${date/- Date added: /}|" >> docs/cocktails/index.md
    fi
done
