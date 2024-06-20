from celery import Celery
import subprocess
import logging
import time
import json
import shutil
import os
app = Celery('tasks', broker='sqla+sqlite:///celerydb.sqlite')

class MaxRetryReached(BaseException):
    pass

def retry(times: int, timeout: int, exceptions: tuple):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logging.warning(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt + 1, times)
                    )
                    attempt += 1
                    if attempt == times:
                        raise MaxRetryReached()
                    time.sleep(timeout)
            return func(*args, **kwargs)
        return newfn
    return decorator


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
