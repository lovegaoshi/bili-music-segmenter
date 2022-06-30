import os, time
from threading import Thread

def initialize() -> None:
    # 
    os.makedirs('out', exist_ok=True)
    os.makedirs(os.path.join('out','ytbdl'), exist_ok=True)
    os.makedirs(os.path.join('out','inaseg'), exist_ok=True)
    os.makedirs(os.path.join('out','shazams'), exist_ok=True)
    os.makedirs(os.path.join('out','shazamf'), exist_ok=True)
    if not os.path.isfile(os.path.join('out','ytbdl', 'urls.config')):
        with open(os.path.join('out','ytbdl', 'urls.config'), 'w') as f: pass


class taskThread(Thread):

    def __init__(self, config_path, func):
        #os.path.join('out','ytbdl', 'urls.config')
        self.config_path = config_path
        self.func = func

    def run(self):
        # runs indefinitely
        while True:
            url_lists = []
            # read and reset
            for i in open(self.config_path, 'r').readlines(): url_lists.append(i[:-1])
            with open(self.config_path, 'w') as f: pass
            for i in url_lists: self.func(i)
            # wait for 60 sec
            time.sleep(60)



if __name__ == '__main__': 
    initialize()