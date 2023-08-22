#!/usr/bin/env python3
import click
import json
import os
import os.path as op
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


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
    driver = webdriver.Chrome()
    # first time we open up the browser, need to login
    logged_in = False
    # the lists the cards were in, which we'll use to grab keywords
    lists = recipes['lists']
    lists = {l['id']: l['name'].lower() for l in lists}
    for rec in recipes['cards'][:10]:
        title = rec['name']
        print(f"Converting {title}")
        slug = '_'.join(title.lower().split(' ')[:3]).replace(',', '').replace('…', '_')
        # was inconsistent with section name
        contents = rec['desc'].replace('# ', '## ').replace('# Instructions', '# Directions')
        contents = contents.replace('# Ingredients', '# Ingredients { #ingredients }')
        contents += f"\n\n## Comments\n\nTotal comments: {rec['badges']['comments']}\n\n"
        if rec['badges']['comments']:
            comments = ""
            driver.get(rec['url'])
            if not logged_in:
                time.sleep(30)
                driver.get(rec['url'])
                logged_in = True
            # can take a while to render the card
            time.sleep(3)
            for cmt in driver.find_elements(By.CLASS_NAME, 'phenom-desc'):
                author = cmt.find_element(By.TAG_NAME, 'span').text
                date = cmt.find_element(By.TAG_NAME, 'a').text
                txt = cmt.find_element(By.TAG_NAME, 'p').text
                comments += f"- {author}, {date}: {txt}\n\n"
            contents += comments
        if 'scaled' in rec['cover']:
            for i, img in enumerate(rec['attachments']):
                driver.get(img['url'])
                if not logged_in:
                    time.sleep(30)
                    driver.get(img['url'])
                    logged_in = True
                img = driver.find_element(By.TAG_NAME, 'img')
                with open(op.join(output_dir, 'images', f'{slug}-{i}.png'), 'wb') as f:
                    f.write(img.screenshot_as_png)
        else:
            img = None
        keywords = [lists[rec['idList']]]
        keywords += [l['name'].lower() for l in rec['labels']]
        keywords = '\n  - '.join(keywords)
        header = f"---\ntags:\n  - {keywords}\n---\n"
        header += f"# {title}\n\n"
        if img is not None:
            for j in range(i+1):
                header += f"![Recipe picture][../images/{slug}-{j}.png]\n\n"
        contents = header + contents
        with open(op.join(output_dir, f'{slug}.md'), 'w') as f:
            f.write(contents)
    driver.close()


if __name__ == '__main__':
    cli()
