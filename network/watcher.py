import time
import os
from network.extractor import WATCHER_CONFIG_DIR as CONFIG_DIREC, EXTRACTORS, FILTERS,\
    load_config, save_config

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