#!/usr/bin/env python3
import click
import json
import os
import re
import os.path as op
import requests
import time
from typing import Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By


@click.group()
def cli():
    pass


@cli.command()
@click.argument('json_path')
@click.option('--output_dir', default='converted_recipes/', help="Where to save outputs", show_default=True)
@click.option('--card_idx', nargs=2, default=(0, 10), help="Index of cards to save out (as the start and stop value in the range).", show_default=True)
def convert_trello(json_path: str, output_dir: str = 'converted_recipes/',
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
        slug = '_'.join(title.lower().split(' ')[:3]).replace(',', '').replace('…', '_')
        # was inconsistent with section name
        contents = rec['desc'].replace('# ', '## ').replace('Instructions', 'Directions')
        contents = contents.replace('# Ingredients', '# Ingredients { #ingredients }')
        contents = contents.replace('Time:', '- Time:')
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
            header += f"![Recipe picture][../images/{img}]\n\n"
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
