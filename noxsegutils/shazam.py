import  os
import glob
import  multiprocessing
import logging
import shutil
import regex
from functools import partial
from ShazamAPI import Shazam
import requests

from inaConstant import load_config, save_config

SAVE_YAML_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'save.yaml')

def shazam_orig(file, **kwargs):
    match = shazam(file, stop_at_first_match = 1)[-1]
    return shazam_title(match), match

def shazaming(
    outdir, media, shazam_coverart_path = '',
    shazam_func = shazam_orig, ignore_fails = False, threads = 1
    ):
    files = glob.glob(os.path.join(
            outdir, '*' + os.path.splitext(os.path.basename(media))[0][1:] + '_*'
        ))
    if threads > 1 and len(files) > 1:
        p = multiprocessing.Pool(min(threads, len(files)))
        p.map(partial(
            shazam_threaded, shazam_coverart_path = '',
            shazam_func = shazam_orig, ignore_fails = True
            ),
        files)
        p.close()
        p.join()
    else: 
        for file in files:
            shazam_threaded(
                file, shazam_coverart_path = shazam_coverart_path,
                shazam_func = shazam_func, ignore_fails = ignore_fails
                )
    save = load_config(SAVE_YAML_PATH)
    mediab = os.path.basename(media)
    save[os.path.basename(media) + "shazam"] = glob.glob(os.path.join(
        outdir, '*' + mediab[1:mediab.rfind('.')] + '*'
    ))
    save_config(SAVE_YAML_PATH, save)
    
def shazam_threaded(
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
        results[fn], match = shazam_func(file)
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
    except IndexError:
        logging.error([fn, 'shazam failed'])
    except Exception:
        if not ignore_fails:
            raise

def shazam(mp3, stop_at_first_match = 1):
    mp3_file_content_to_recognize = open(mp3, 'rb').read()
    shazamInst = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazamInst.recognizeSong()
    matches = []
    try:
        while True:
            match = next(recognize_generator)
            if len(match[1]['matches']) > 0: 
                matches.append(match)
                if len(matches) > stop_at_first_match:
                    raise StopIteration()
    except StopIteration:
        pass
    return matches

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
    title = legalize_filename(match[1]['track']['title'])
    if 'in the style of' in title.lower():
        artist = title[
            title.lower().index('in the style of ') + 
            len('in the style of '):]
        artist = artist[:artist.index(')')]
    else:
        artist = legalize_filename(match[1]['track']['subtitle'])

    return [
    legalize_filename(match[1]['track']['title']),
    legalize_filename(match[1]['track']['subtitle']),    
    ]

def shazam_coverart(match, fn, outdir):
    try:
        albumart = match[1]['track']['images']['coverarthq']
        req = requests.get(albumart)
        with open(os.path.join(
            outdir, os.path.basename(fn) + albumart[albumart.rfind('.'):]
            ), 'wb') as f:
            f.write(req.content)
    except Exception:
        pass


class KoreanCharException(BaseException):
    pass