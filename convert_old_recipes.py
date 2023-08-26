#!/usr/bin/env python3
import click
import json
import os
import re
import os.path as op
import requests
import time
import zipfile
from typing import Tuple, Optional
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By


TEMPLATE = """---
tags:
{tags}
---

# {title}

{imgs}

- Serves: {servings}
{{ #serves }}
- Working time: {working_time}
- Waiting time: {waiting_time}

## Description

{description}

## Ingredients {{ #ingredients }}

{ingredients}

## Directions

{directions}

## Notes

## Source
{source}
## Comments
"""


@click.group()
def cli():
    pass


@cli.command()
@click.argument('zip_path')
@click.option('--output_dir', default='converted_tandoor_recipes/', help="Where to save outputs", show_default=True)
@click.option('--recipe_idx', nargs=2, default=(0, 10), help="Index of recipes to save out (as the start and stop value in the range).", show_default=True)
def convert_tandoor(zip_path: str, output_dir: str = 'converted_tandoor_recipes/',
                    recipe_idx: Optional[Tuple[int]] = (0, 10)):
    recipes = zipfile.ZipFile(zip_path, 'r')
    os.makedirs(op.join(output_dir, 'images'), exist_ok=True)
    recipe_list = recipes.filelist
    if recipe_idx is not None:
        recipe_list = recipe_list[slice(*recipe_idx)]
    for rec_i, rcp in enumerate(recipe_list):
        rec_dict = {k: '' for k in ['tags', 'title', 'imgs', 'servings', 'working_time', 'waiting_time',
                                    'description', 'ingredients', 'directions', 'source']}
        # they're nested zip files
        rcp = zipfile.ZipFile(recipes.open(rcp), 'r')
        rec = json.loads(rcp.read(rcp.filelist[0]))
        rec_dict['tags'] = '\n - '.join([k['name'] for k in rec['keywords']])
        title = rec['name']
        rec_dict['title'] = title
        print(f"Converting {recipe_idx[0]+rec_i} ({rcp.filename}), {title}")
        slug = '_'.join(title.lower().split(' ')[:3]).replace(',', '').replace('…', '_').replace('(', '').replace(')', '')
        slug = re.sub("[(),.'&\"’]", "", slug)
        slug = unidecode(slug)
        imgs = []
        for i, img in enumerate(rcp.filelist[1:]):
            ext = op.splitext(img.filename)[-1]
            with open(op.join(output_dir, 'images', f'{slug}-{i}{ext}'), 'wb') as f:
                f.write(rcp.read(img))
            imgs.append(f'{slug}-{i}{ext}')
        rec_dict['imgs'] = '\n\n'.join([f'![Recipe picture](../images/{img})' for img in imgs])
        rec_dict['servings'] = f'{rec["servings"]} {rec["servings_text"]}'
        rec_dict['working_time'] = rec['working_time']
        rec_dict['waiting_time'] = rec['waiting_time']
        if rec['description']:
            rec_dict['description'] = rec['description']
        ingrs = []
        dirs = []
        dir_steps = []
        for st in rec['steps']:
            if st['name']:
                dirs.append(f"### {st['name']}")
            dir_steps.append(st['order']+1)
            dirs.append(st['instruction'].replace('# ', '### '))
            for ingr in st['ingredients']:
                note = f'({ingr["note"]})' if ingr['note'] else ''
                if ingr['food']:
                    ingr_txt = "- "
                    if ingr['amount']:
                        ingr_txt += str(ingr['amount'])
                    if ingr['unit']:
                        ingr_txt += ' ' + ingr['unit']['name'] + ' '
                    ingr_txt += f"{ingr['food']['name']} {note}"
                else:
                    ingr_txt = f"\n### {ingr['note']}\n"
                ingrs.append(ingr_txt)
        if ingrs:
            rec_dict['ingredients'] = '\n'.join(ingrs)
        if '\n2. ' in '\n'.join(dirs) or '\n- ' in '\n'.join(dirs):
            # then we don't need to number steps
            rec_dict['directions'] = '\n\n'.join(dirs)
        elif '\n'.join(dirs):
            # don't need to add anything if there's no content
            rec_dict['directions'] = '\n\n'.join([f'{i}. {d}' for i, d in zip(dir_steps, dirs)])
        source = re.findall("Source: (.*)", rec_dict['directions'])
        if source:
            rec_dict['source'] = '\n' + source[0] + '\n'
            rec_dict['directions'] = re.sub("Source: (.*)", "", rec_dict['directions'])
        rec_dict['directions'] = rec_dict['directions'].replace('…', '_')
        if rec_dict['directions'] ==  '1. ':
            # then the only contents of directions *was* the source, which got removed, so drop this
            rec_dict['directions'] = ""
        with open(op.join(output_dir, f'{slug}.md'), 'w') as f:
            f.write(TEMPLATE.format(**rec_dict))


@cli.command()
@click.argument('json_path')
@click.option('--output_dir', default='converted_trello_recipes/', help="Where to save outputs", show_default=True)
@click.option('--card_idx', nargs=2, default=(0, 10), help="Index of cards to save out (as the start and stop value in the range).", show_default=True)
def convert_trello(json_path: str, output_dir: str = 'converted_trello_recipes/',
                   card_idx: Optional[Tuple[int]] = (0, 10)):
    with open(json_path, 'r') as f:
        recipes = json.load(f)
    os.makedirs(op.join(output_dir, 'images'), exist_ok=True)
    options = webdriver.ChromeOptions() ;
    prefs = {"download.default_directory": op.join(output_dir, 'images')};
    options.add_experimental_option("prefs", prefs);
    driver = webdriver.Chrome(options=options)
    # first time we open up the browser, need to login
    logged_in = False
    # the lists the cards were in, which we'll use to grab keywords
    lists = recipes['lists']
    lists = {l['id']: l['name'].lower() for l in lists}
    # recipes themselves
    cards = recipes['cards']
    if card_idx is not None:
        cards = cards[slice(*card_idx)]
    for rec_i, rec in enumerate(cards):
        title = rec['name']
        print(f"Converting {card_idx[0]+rec_i}, {title}")
        slug = '_'.join(title.lower().split(' ')[:3]).replace(',', '').replace('…', '_').replace('(', '').replace(')', '')
        slug = re.sub("[(),.'&\"’]", "", slug)
        # was inconsistent with section name
        contents = rec['desc'].replace('# ', '## ').replace('Instructions', 'Directions').replace('Preparation', 'Directions')
        contents = contents.replace('# Ingredients', '# Ingredients { #ingredients }')
        contents = contents.replace('Time:', '- Time:').replace('’', "'").replace('Yields:', 'Serves:')
        contents = re.sub('Serves: ([0-9]+).*', '- Serves: \\1\n{ #serves }', contents)
        contents += f"\n\n## Comments\n\nTotal comments: {rec['badges']['comments']}\n\n"
        if rec['badges']['comments']:
            comments = ""
            driver.get(rec['url'])
            if not logged_in:
                print("Please login within 30 seconds.")
                time.sleep(30)
                driver.get(rec['url'])
                logged_in = True
            # can take a while to render the card
            time.sleep(3)
            for cmt in driver.find_elements(By.CLASS_NAME, 'phenom-desc'):
                author = cmt.find_element(By.TAG_NAME, 'span').text
                date = cmt.find_element(By.TAG_NAME, 'a').text
                txt = cmt.find_element(By.TAG_NAME, 'p').get_attribute('innerHTML')
                comments += f"- {author}, {date}: {txt}\n\n"
            contents += comments
        imgs = []
        links = []
        i = 0
        for img in rec['attachments']:
            if 'trello' not in img['url']:
                # then this isn't an image, but a link, and we don't need to
                # visit the page, just store it
                links.append(img['url'])

            else:
                driver.get(img['url'])
                if not logged_in:
                    print("Please login within 30 seconds.")
                    time.sleep(30)
                    driver.get(img['url'])
                    logged_in = True
                # if it was a txt or pdf, we downloaded it with the driver.get, and so we're fine
                if img['url'].endswith('pdf') or img['url'].endswith('txt'):
                    imgs.append(op.split(img['url'])[-1])
                else:
                    img = driver.find_element(By.TAG_NAME, 'img')
                    with open(op.join(output_dir, 'images', f'{slug}-{i}.png'), 'wb') as f:
                        f.write(img.screenshot_as_png)
                    imgs.append(f'{slug}-{i}.png')
                    i += 1
        keywords = [lists[rec['idList']]]
        keywords += [l['name'].lower() for l in rec['labels']]
        keywords = '\n  - '.join(keywords)
        header = f"---\ntags:\n  - {keywords}\n---\n"
        header += f"# {title}\n\n"
        for img in imgs:
            header += f"![Recipe picture](../images/{img})\n\n"
        contents = header + contents
        if len(links):
            links = '\n- '.join(links)
            links = f'## Extra links\n\n- {links}\n'
            contents += links
        with open(op.join(output_dir, f'{slug}.md'), 'w') as f:
            f.write(contents)
    driver.close()


if __name__ == '__main__':
    cli()
