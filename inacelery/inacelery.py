from celery import Celery
import subprocess
import logging
import json
import shutil
import os

from utils.util import retry

app = Celery('tasks', broker='sqla+sqlite:///celerydb.sqlite')


@retry(times=15, timeout=60, exceptions=(Exception))
def retry_upload(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        logging.warning('biliup failed... retrying.')
        raise Exception('upload failed.')
    

@app.task
def add(cmd):
    cmd = json.loads(cmd)
    retry_upload(cmd)
    logging.info([cmd, 'completed.'])
    logging.info(['removing', cmd[2]])
    shutil.rmtree(os.path.dirname(cmd[2]))
