from celery import Celery
import logging
from datetime import datetime
from biliup import InaBiliup


app = Celery('tasks', broker='sqla+sqlite:///bilicelerydb.sqlite')

@app.task
def add(media):
    logging.info(['calling biliupWrapper on', media, 'at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    InaBiliup(media=media, shazam_thread=1, sound_only="").run()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument('--media', type=str, nargs='+', help='file path or weblink')
    args = parser.parse_args()
    for media in args.media:
        add.delay(media)

