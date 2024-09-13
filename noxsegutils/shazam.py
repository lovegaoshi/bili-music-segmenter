import  os
import glob
import logging
import shutil
import regex
import time
import requests
import asyncio
from shazamio import Shazam

from noxsegutils.extractor import load_config, save_config


semaphore = asyncio.Semaphore(3)
myshazam = Shazam()

SAVE_YAML_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'save.yaml')

async def shazam_orig(file, **kwargs):
    match = await shazam(file)
    return shazam_title(match), match

async def shazaming(
    outdir, media, shazam_coverart_path = '',
    shazam_func = shazam_orig, ignore_fails = False
    ):
    files = glob.glob(os.path.join(
            outdir, '*' + os.path.splitext(os.path.basename(media))[0][1:] + '_*'
        ))
    await asyncio.gather(*[shazam_threaded(
        file, shazam_coverart_path = shazam_coverart_path,
        shazam_func = shazam_func, ignore_fails = ignore_fails
    ) for file in files])
    save = load_config(SAVE_YAML_PATH)
    mediab = os.path.basename(media)
    save[os.path.basename(media) + "shazam"] = glob.glob(os.path.join(
        outdir, '*' + mediab[1:mediab.rfind('.')] + '*'
    ))
    save_config(SAVE_YAML_PATH, save)
    
async def shazam_threaded(
    file, shazam_coverart_path = '',
    shazam_func = shazam_orig, ignore_fails = True
    ):
    results = {}
    if ' by ' in file:
        return
    filename = file[:file.rfind('.')]
    fileext = file[len(filename):]
    fn = os.path.basename(filename)
    logging.info(['shazaming', fn])
    try:
        #match = shazam(file, stop_at_first_match = 1)[-1]
        #results[fn] = shazam_title(match)
        results[fn], match = await shazam_func(file)
        try:
            logging.info([fn, 'shazam found to be', results[fn]])
        except UnicodeEncodeError:
                logging.warning([fn, 'shazam found but cant show unicode burr durr'])
        renamed_file = os.path.join(
            os.path.dirname(file),
            #    r'D:\tmp\ytd\convert2music',
            (fn + f"_{results[fn][0].replace(':', ' ')} by\
                 {results[fn][1].replace(r'/', '')}") + fileext
        )
        shutil.move(file, renamed_file)
        if os.path.isdir(shazam_coverart_path):
            shazam_coverart(match, renamed_file, shazam_coverart_path)
    except (IndexError, KeyError):
        logging.error([fn, 'shazam failed'])
    except Exception:
        if not ignore_fails:
            raise

async def shazam(mp3):
    async with semaphore:
        match = await myshazam.recognize(mp3)
        time.sleep(3)
        return match['track']

def legalize_filename(fn):
    if regex.search(r'\p{IsHangul}',fn) is not None:
        raise KoreanCharException(fn)
    illegal_list = [
        [':', ' '],
        ['"', ''],
        [r'/', ''],
        [r'?', ''],
        [r'*', ''],
        ['\'',''],
        ['<',''],
        ['>',''],
    ]
    for i in illegal_list:
      fn = fn.replace(i[0],i[1])
    return fn

def shazam_title(match):
    title = legalize_filename(match['title'])
    if 'in the style of' in title.lower():
        artist = title[
            title.lower().index('in the style of ') + 
            len('in the style of '):]
        artist = artist[:artist.index(')')]
    else:
        artist = legalize_filename(match['subtitle'])

    return [
    legalize_filename(match['title']),
    legalize_filename(match['subtitle']),    
    ]

def shazam_coverart(match, fn, outdir):
    try:
        albumart = match['images']['coverarthq']
        req = requests.get(albumart)
        with open(os.path.join(
            outdir, os.path.basename(fn) + albumart[albumart.rfind('.'):]
            ), 'wb') as f:
            f.write(req.content)
    except Exception:
        pass


class KoreanCharException(BaseException):
    pass
