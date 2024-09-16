import time
import logging
from datetime import datetime

from network.watcher import watch


if __name__ == '__main__':
    from biliup import InaBiliup
    # print(watch())
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument(
        '--watch_interval',
        type=int,
        default=0,
        help='in seconds. 0 means no repeat.')
    parser.add_argument(
        '--log_level',
        type=int,
        default=logging.DEBUG,
        help='in seconds. 0 means no repeat.')
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, handlers=[
        logging.FileHandler('./inaseg.log'),
        logging.StreamHandler()
    ])
    while True:
        logging.info([
            'biliWatcher loop has started on ',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        for i in reversed(watch()):
            logging.info([
                'calling biliupWrapper on', i, 'at',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            InaBiliup(media=i).run()
        logging.info([
            'biliWatcher loop has completed on ',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        if args.watch_interval < 1:
            sys.exit(0)
        logging.debug(
            ['biliWatcher loop is now waiting for ', args.watch_interval])
        time.sleep(args.watch_interval)
