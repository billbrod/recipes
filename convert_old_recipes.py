#!/usr/bin/env python3
import click
import json
import os
import os.path as op
import requests
import getpass


@click.group()
def cli():
    pass


@cli.command()
@click.argument('json_path')
@click.option('--output_dir', default='converted_recipes/', help="Where to save outputs")
def convert_trello(json_path, output_dir='converted_recipes/'):
    with open(json_path, 'r') as f:
        recipes = json.load(f)
    os.makedirs(op.join(output_dir, 'images'), exist_ok=True)
    user = input("Enter Trello username: ")
    passwd = getpass.getpass(prompt=f"Enter Trello password for {user}: ")
    for rec in recipes['cards'][:10]:
        title = rec['name']
        slug = '_'.join(title.lower().split(' ')[:3])
        # was inconsistent with section name
        contents = rec['desc'].replace('# ', '## ').replace('# Instructions', '# Directions')
        contents = contents.replace('# Ingredients', '# Ingredients { #ingredients }')
        contents += (
            f"""\n\n## Comments
            Total comments: {rec['badges']['comments']}
            """
        )
        if 'scaled' in rec['cover']:
            # get the largest image
            img = rec['cover']['scaled'][-1]['url']
            r = requests.get(img, stream=True, auth=(user, passwd))
            if r.status_code == 200:
                with open(op.join(output_dir, 'images', f'{slug}.png'), 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        else:
            img = None
        header = f"# {title}\n\n"
        if img is not None:
            header += f"![Recipe picture][../images/{slug}.png]\n\n"
        contents = header + contents
        with open(op.join(output_dir, f'{slug}.md'), 'w') as f:
            f.write(contents)
        # - FIGURE OUT if I can get column, make that a tag
        # - still failing to get images (code 401)
        # - SOME recpies just include an image, that I took, so download those as well-- might already do? skip if no image or description
        # - print default in click helpstring


if __name__ == '__main__':
    cli()
