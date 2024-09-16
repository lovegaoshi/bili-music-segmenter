import time
import os
from network.extractor import WATCHER_CONFIG_DIR as CONFIG_DIREC, EXTRACTORS, FILTERS,\
    load_config, save_config
import logging
from datetime import datetime

DEFAULT_CONFIG = [{
    'url': 'example',
    'extractor': None,
    'last_url': True,
    'filter': None,
    'hinter': ""
}, {
    'url': 'example2',
    'extractor': None,
    'last_url': True,
    'filter': None,
    'hinter': ""
}]


def watch(config_dir=CONFIG_DIREC):
    r = []
    watch_list = load_config(config_dir, default=DEFAULT_CONFIG)
    os.replace(config_dir, config_dir + '.old', )
    for item in watch_list:
        if item['extractor'] not in EXTRACTORS:
            continue
        extractor = EXTRACTORS[item['extractor']]()
        new_urls = extractor.extract(
            url=item['url'],
            last_url=item['last_url']
        )
        if item['last_url'] is not True:
            r += FILTERS[item['filter']](new_urls)
        if len(new_urls) > 0:
            item['last_url'] = new_urls[0][1]
        time.sleep(1)
    # json.dump(watch_list, open(config_dir, 'w'), indent=4)
    save_config(config_dir, watch_list)
    return r


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
