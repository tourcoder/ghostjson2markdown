# coding: utf-8
import json
import re
import argparse
import sys
import os


def read_file(filename):
    with open(filename, 'rt') as f:
        dat = f.read()
        db = json.loads(dat)
        return db


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('INPUT_FILE', help="Input Ghost .json file",
                    type=str, action='store')
    ap.add_argument('OUTPUT_DIR', help="Output Directory",
                    type=str, action='store')
    args = ap.parse_args()
    return args


def get_tags(db, postid):
    dtags = db['db'][0]['data']['tags']
    post_tags = db['db'][0]['data']['posts_tags']
    tt = [t['tag_id'] for t in post_tags if t['post_id'] == postid]
    rtags = [tag['name'] for tag in dtags if tag['id'] in tt]
    return rtags


def get_author(db, author_id):
    authors = db['db'][0]['data']['users']
    for a in authors:
        if a['id'] == author_id:
            return a['name']
    return None

def get_posts(db):
    ret = dict()
    for post in db['db'][0]['data']['posts']:
        pid = post['id']
        author_id = get_author(db, post['author_id'])
        if post['title'].find('"') == -1:
            title = '"' + post['title'] + '"'
            print title
        else:
            title = '"' + post['title'].replace("\"", "'") + '"'
            print title
        slug = post['slug']
        stype = post['type']
        created = post['created_at']
        updated = post['updated_at']
        published = post['published_at']
        tags = get_tags(db, pid)
        markdown = ''
        try:
            doc = json.loads(post['mobiledoc'])
            markdown = doc['cards'][0][1]['markdown']
            markdown = markdown.replace('/content/images', '/imgs')
        except:
            pass
        draft = post['status'] == 'draft'

        out = '---\n'
        out += 'title: {}\n'.format(title.encode('utf-8'))
        out += 'slug: {}\n'.format(slug)

        out += 'author: {}\n'.format(author_id) if author_id else ''
        out += 'lastmod: {}\n'.format(updated) if updated else ''
        out += 'date: {}\n'.format(published) if published else ''
        out += 'draft: true\n' if draft else ''

        tstring = "tags: ["
        for t in tags:
            tstring += '"{}", '.format(t.encode('utf-8'))
        if len(tags):
            tstring = tstring[:-2]
        tstring += ']\n'
        out += tstring
        out += '---\n\n'
        out += markdown.encode('utf-8')

        ret[slug] = out
    return(ret)


def write_posts(outdir, posts):
    for k in posts.keys():
        fname = os.path.join(outdir, "{}.md".format(k))
        with open(fname, 'wt') as of:
            of.write(posts[k])


def main():
    args = parse_args()
    db = read_file(args.INPUT_FILE)
    posts = get_posts(db)
    print('Converted {} posts'.format(len(posts)))
    write_posts(args.OUTPUT_DIR, posts)


if __name__ == '__main__':
    main()