from nis import cat
from instaloader import *
import re
import os

def post_links(L, link, random_dir):
    try: shortcode = re.findall(r'/p/.*/', link)[0]
    except: return None
    content = []
    if shortcode:
        shortcode = shortcode[3:-1]
        post = Post.from_shortcode(L.context, shortcode)
        try:
            L.download_post(post, random_dir)
        except:
            if os.path.exists(random_dir):
                os.rmdir(random_dir)
            return None
        files = os.listdir(random_dir)
        caption = ''
        for f in files:
            if f[-3:] == '.xz':
                os.remove(random_dir + '/' + f)
                continue
            elif f[-4:] == ".txt":
                with open(random_dir + '/' + f, 'r') as ff:
                    try: caption = ff.read()
                    except: pass
                try: os.remove(random_dir + '/' + f)
                except: pass
                continue
            content.append(f)
        resp = {}
        resp['files'] =  content 
        if caption == "": caption = "no caption"
        resp['caption'] =  caption
        return resp
    
def igtv_links(L, link:str, random_dir):
    try: shortcode = re.findall(r'/tv/.*/', link)[0]
    except: return None
    content = []
    if shortcode:
        shortcode = shortcode[4:-1]
        post = Post.from_shortcode(L.context, shortcode)
        try:
            L.download_post(post, random_dir)
        except:
            if os.path.exists(random_dir):
                try: os.rmdir(random_dir)
                except: pass
            return None

        files = os.listdir(random_dir)
        caption = ''
        for f in files:
            if f[-3:] == '.xz':
                os.remove(random_dir + '/' + f)
                continue
            elif f[-4:] == ".txt":
                with open(random_dir + '/' + f, 'r') as ff:
                    try: caption = ff.read()
                    except: pass
                try: os.remove(random_dir + '/' + f)
                except: pass
                continue
            content.append(f)

        resp = {}
        resp['files'] =  content 
        if caption == "": caption = "no caption"
        resp['caption'] =  caption
        return resp

def story_links(L, link:str, random_dir):
    link += '\n'
    try: link = link.replace("?", '\n')
    except: pass
    try: mediaid = re.findall(r'/stories/.*\n', link)[0]
    except: return None
    mediaid = mediaid[10:-1]
    mediaid = mediaid.split('/')[1]
    if mediaid:
        story = StoryItem.from_mediaid(L.context, int(mediaid))
        try:
            L.download_storyitem(story, random_dir)
        except:
            if os.path.exists(random_dir):
                try: os.rmdir(random_dir)
                except: pass
            return None

        files = os.listdir(random_dir)
        for f in files:
            if f[-3:] == '.xz':
                try: os.remove(random_dir + '/' + f)
                except: pass
                continue
        return files

def highlight_links(L, link:str, random_dir):
    try: link = link.replace('?', "\n")
    except: pass
    try: link = link.replace('&', "\n")
    except: pass
    try: mediaid = re.findall(r'story_media_id=.*\n', link)[0]
    except: return None
    mediaid = mediaid[15:-1]
    try: mediaid = mediaid.split('_')[0]
    except: pass

    if mediaid:
        story = StoryItem.from_mediaid(L.context, int(mediaid))
        try:
            L.download_storyitem(story, random_dir)
        except:
            if os.path.exists(random_dir):
                try: os.rmdir(random_dir)
                except: pass
            return None

        files = os.listdir(random_dir)
        for f in files:
            if f[-3:] == '.xz':
                try: os.remove(random_dir + '/' + f)
                except: pass
                continue
        return files