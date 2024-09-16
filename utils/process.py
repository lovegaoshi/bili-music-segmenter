import subprocess
import logging

def cell_stdout(cmd, silent=False, encoding=None):
    logging.info(['calling', cmd, 'in terminal:'])
    with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          universal_newlines=True, encoding=encoding) as p:
        if not silent:
            try:
                for i in p.stdout:  # .decode("utf-8"):
                    logging.debug(i)
            except UnicodeDecodeError:
                # 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷
                logging.warning('decode failed! \
                    but at least you have this eror message...')
        p.wait()
    return p.returncode
