import logging
import glob
import os
import subprocess
import multiprocessing
from datetime import datetime

from network.cookieformatter import biliup_to_ytbdl_cookie_write2file
from network.download import ytbdl
from utils.filename import strip_medianame_out, put_medianame_backin
from utils.process import cell_stdout
from network.biliupload import bilibili_upload, BILIUP_ROUTE

class InaBiliup():

    def __init__(
        self,
        media: str,
        outdir: str = os.getcwd(),
        episode_limit: int = 180,
        shazam_thread: int = min(max(multiprocessing.cpu_count(), 1), 4),
        ignore_errors: bool = True,
        sound_only: str = '',
        route: str = BILIUP_ROUTE,
        cleanup: bool = True,
        no_biliup: bool = False,
    ):
        self.cleanup = True  # False
        self.outdir = outdir
        self.media = media
        self.episode_limit = episode_limit
        self.shazam_thread = shazam_thread
        self.ignore_errors = ignore_errors
        self.sound_only = sound_only
        self.route = route
        self.cleanup = cleanup
        self.no_biliup = no_biliup

    def run(self):
        try:
            media = self.media
            outdir = self.outdir
            if media == '':
                return
            logging.info(f'inaseging {media} at ' +
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            os.chdir(outdir)

            media_url = ''
            if 'https:' in media:
                media_url = media
                # use biliup to renew the cookie file, and write to ytdlp netscape format.
                subprocess.call(['biliup', 'renew'])
                biliup_to_ytbdl_cookie_write2file()
                # , outdir = outdir
                media = ytbdl(media, soundonly=self.sound_only, aria=16)
            if not cell_stdout([
                'python',
                'inaseg.py',
                '--media={}'.format(media),
                '--outdir={}'.format(outdir),
                '--soundonly', self.sound_only,
                '--shazam',
                    '--cleanup']) == 0:
                raise BaseException()
            # inaseg failed?
            logging.info(['inaseg completed on', media])
            stripped_media_names = strip_medianame_out(outdir, media)
            logging.info(['preparing to upload', stripped_media_names])

            bilibili_upload(
                stripped_media_names, os.path.basename(media),
                source=None, episode_limit=self.episode_limit)
            logging.info(['finished stripping and uploading', media])
            if self.cleanup:
                if os.path.isfile(media):
                    os.remove(media)
                for i in stripped_media_names:
                    os.remove(i)
            else:
                put_medianame_backin(
                    stripped_media_names, media,
                    shazamed=r'D:\tmp\ytd\convert2music',
                    nonshazamed=r'D:\tmp\ytd\extract')
        except KeyboardInterrupt:
            raise
        except BaseException:
            if self.ignore_errors:
                for i in glob.glob('*.mp4') + glob.glob('*.aria2') + \
                        glob.glob('*.part'):
                    os.remove(i)
                # if os.path.isfile(media): os.remove(media)
                logging.error(f'{media} failed. file is removed in\
                     automatic error ignore handler')
            else:
                raise


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument('--media', type=str, nargs='+',
                        help='file path or weblink')
    logging.basicConfig(level=logging.DEBUG, handlers=[
        logging.FileHandler('./inaseg.log'),
        logging.StreamHandler()
    ])
    args = parser.parse_args()
    for media in args.media:
        logging.info(
            f'inaseging {media} at ' +
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        InaBiliup(media=media).run()
