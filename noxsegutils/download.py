from subprocess import Popen, PIPE
from difflib import SequenceMatcher as SM
import os
import glob
import logging
import tempfile
import time

COOKIES_LOCATION = ['--cookies', 'ytdlp_cookies.txt']

#fuzzy match! 
def ytbdl(
    url: str, soundonly: str = '-f bestaudio',
    outdir: str = tempfile.gettempdir(),
    aria: int = None) -> list:
    r = ''# --restrict-filenames
    fname = None
    #./youtube-dl
    cmd = ['yt-dlp', url, '-o', os.path.join(
        outdir, "[%(uploader)s] %(title)s %(upload_date)s.%(ext)s")]
    cmd.extend(COOKIES_LOCATION)       
    if aria is not None: 
        cmd.append('--external-downloader')
        cmd.append('aria2c')
        cmd.append('--external-downloader-args')
        cmd.append('-x {} -s {} -k 1M'.format(str(aria), str(aria)))
    if len(soundonly.split(' ')) > 1:
        cmd.extend(soundonly.split(' '))
    logging.info(cmd)
    passed_download = False
    while not passed_download:
        passed_download = True
        with Popen(cmd, stdout=PIPE, 
                universal_newlines=True) as p:
            for line in p.stdout:
                logging.info(line)
                if '[download] Destination' in line:
                    fname = line[len('[download] Destination: '):-1]
                elif 'has already been downloaded' in line: 
                    fname = line[len('[download] ') : 
                    -len(' has already been downloaded') - 1]
                elif '[Merger]' in line: 
                    fname = line[len('[Merger] Merging formats into "'):-2]
                elif "error" in line.lower():
                    passed_download = False
            if not passed_download:
                time.sleep(10)
    if fname is None:
        raise Exception('no ytbdl resutls!')
    logging.info(['mathcing', fname])
    ext = fname[fname.rfind('.'):]
    ext = ext.split(' ')[0]
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
    return sorted(r, key = lambda x: x[1], reverse = True)[0][0]