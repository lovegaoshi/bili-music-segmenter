import time
import os
from inaConstant import WATCHER_CONFIG_DIR as CONFIG_DIREC
from inaConstant import EXTRACTORS, FILTERS, load_config, save_config
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
        if not item['extractor'] in EXTRACTORS:
            continue
        extractor = EXTRACTORS[item['extractor']]()
        new_urls = extractor.extract(
            url=item['url'],
            last_url=item['last_url']
        )
        if not item['last_url'] is True:
            r += FILTERS[item['filter']](new_urls)
        if len(new_urls) > 0:
            item['last_url'] = new_urls[0][1]
        time.sleep(1)
    #json.dump(watch_list, open(config_dir, 'w'), indent=4)
    save_config(config_dir, watch_list)
    return r

if __name__ == '__main__':
    from biliupWrapper import Biliup
    #print(watch())
    while True:
        for i in watch():
            print('calling biliupWrapper on', i)
            Biliup(media=i).run()
        time.sleep(3600)
        # p = subprocess.Popen(['python', 'biliupWrapper.py', '--media='+i])
        # p.wait()
    #url = r'https://space.bilibili.com/592726738/channel/seriesdetail?sid=2357741&ctype=0'
    #extractor = EXTRACTORS['biliseries']()
    #print(my_url_filter(extractor.extract_API(*re.compile(extractor._VALID_URL).match(url).group(*extractor._GROUPED_BY), stop_after = None)))