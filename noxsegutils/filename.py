
import os
import glob
import shutil
from difflib import SequenceMatcher as SM

def bili_name_trim(fn, base, char_lim = 75):
    file = fn[len(base) - 3:]
    filename = file[:file.rfind('.')]
    fileext = file[len(filename):]
    return filename[:char_lim] + fileext

def strip_medianame_out(outdir, media):
    mediab = os.path.basename(media)
    r = []
    for file in glob.glob(os.path.join(
            outdir, '*' + mediab[1:mediab.rfind('.')]+ '*'
        )):
        if file == media:
            continue
        outfile = os.path.join(
                os.path.dirname(file),
                bili_name_trim(os.path.basename(file), mediab)
            )
        shutil.move(
            file, 
            outfile
        )
        r.append(outfile)
    return r


def put_medianame_backin(filelists, media, shazamed = '', nonshazamed = ''):
    mediab = os.path.basename(media)
    mediab = mediab[:mediab.rfind('.')]
    r = []
    for file in filelists:
        if ' by ' in os.path.basename(file):
            outdir = shazamed if os.path.isdir(shazamed) else os.path.dirname(file)
        else:
            outdir = nonshazamed if os.path.isdir(nonshazamed) \
                else os.path.dirname(file)
        outfile = os.path.join(
                outdir,
                mediab + '_' + os.path.basename(file))
        shutil.move(
            file, 
            outfile
        )
        r.append(outfile)
    return r

def fuzzy_match_my_file(fname):
    ext = fname[fname.rfind('.'):]
    r = []
    for i in glob.glob(os.path.join(
        os.path.dirname(fname),
        '*' + ext
    )):
        r.append([
            i,
            SM(
                isjunk=None, a = os.path.basename(fname),
                b = os.path.basename(i)).ratio()
        ])
    return r