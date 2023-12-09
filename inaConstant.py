import os.path
import requests
import yaml
import time
import glob
import re
from datetime import datetime
import logging
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs

from wbi import get_query
from constants import DEFAULT_UI

'''
from inaConstant import EXTRACTORS
EXTRACTORS['glob']().extract(r'D:\tmp\ytd\convert2music\*.mp3')
EXTRACTORS['biliepisode']().extract('https://www.bilibili.com/video/BV1zP411V7ap')

'''
DEFAULT_OUTDIR = r'D:\tmp\ytd\convert2music'
TIMESTAMP_ASSIST_DIR = r"D:\tmp\ytd\timstamp.ini"
RAM_LIMIT = 15000
DEFAULT_BILIUP_LINE = 'kodo'

WATCHER_CONFIG_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'configs',
    'biliWatcher.yaml')
DLWATCHER_CONFIG_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'configs',
    'biliDLWatcher.yaml')
NOUPWATCHER_CONFIG_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'configs',
    'noupWatcher.yaml')
WRAPPER_CONFIG_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'configs',
    'biliWrapper.json')
INASEGED_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'inaseged.yaml')


def initialize_config(
        config_dir: str,
        default: dict = {},
        reset: bool = False) -> dict:
    if not os.path.isfile(config_dir) or reset:
        save_config(config_dir, default)
        return default


def load_config(config_dir: str, default: dict = {}, encoding: str = 'utf-8') -> dict:
    try:
        try:
            return yaml.safe_load(open(config_dir, 'r', encoding=encoding))
        except FileNotFoundError:
            return yaml.safe_load(open(config_dir + '.old', 'r', encoding=encoding))
    except BaseException:
        return initialize_config(config_dir, default, reset=True)


def save_config(config_dir: str, default: dict = {}) -> None:
    try:
        os.replace(config_dir, config_dir + '.old', )
    except FileNotFoundError:
        pass
    yaml.dump(default, open(config_dir, 'w'),)


def bkup_config(config_dir: str, encoding: str = 'utf-8', backup_day: int = 7) -> None:
    try:
        c = yaml.safe_load(open(config_dir, 'r', encoding=encoding))
        if not 'created-time' in c:
            c['created-time'] = datetime.now().strftime(r'%Y-%m-%d')
            save_config(config_dir, c)
        elif (datetime.now() - datetime.strptime(c['created-time'], '%Y-%m-%d')).days > backup_day:
            os.makedirs('backup', exist_ok=True)
            save_config(
                f"{os.path.splitext(config_dir)[0]}_{c['created-time']}.{os.path.splitext(config_dir)[1]}",
                c
            )
            os.remove(config_dir)
            os.remove(config_dir + '.old')
    except:
        pass


class Extractor():
    _VALID_URL = r'(?P<some_name>.+)'
    _GROUPED_BY = ['some_name']
    _API = r'some_url{}'

    def extract_API(self, *args, **kwargs):
        raise Exception('not defined!')

    def extract(self, url: str, last_url: str = None):
        try:
            matched = re.compile(self._VALID_URL).match(
                url).group(*self._GROUPED_BY)
        except AttributeError:
            logging.error((self._VALID_URL, url, 'does not match!'))
            raise
        if not self.url_valid(last_url):
            last_url = True
        if type(matched) is str:
            matched = [matched]
        return self.extract_API(
            *matched,
            stop_after=last_url,
        )

    def url_valid(self, *args, **kwargs):
        return True


class InfoExtractor(Extractor):
    '''
    copied from ytdlp 
    '''

    def extract_API(
            self,
            *args,
            stop_after: str = None,
            time_wait=0.5,
            headers: dict = DEFAULT_UI) -> list:
        r = []
        for i in range(999):
            logging.debug(
                ['extract API', self._API.format(*args, page=str(i + 1))])
            k = requests.get(self._API.format(
                *args, page=str(i + 1)), headers=headers)
            parsed, return_signal = self.parse_json(
                json_obj=k, stop_after=stop_after)
            r += parsed
            if return_signal:
                return r
            time.sleep(time_wait)
        return r

    def parse_json(self, json_obj, **kwargs):
        raise Exception()


class BiliInfoExtractor(InfoExtractor):

    def url_valid(self, stop_after):
        try:
            bvid = re.compile(
                r'https?://www.bilibili\.com/video/(?P<bvid>BV.+)\?*.*').match(str(stop_after)).group('bvid')
            logging.debug(['extracted bvid', bvid, 'from', stop_after])
            if -404 == requests.get(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp').json()['code']:
                logging.warning(
                    f'{bvid} is not a valid URL; setting extractor to prime to the most recent URL.')
                return False
            return True
        except AttributeError:
            return True


class BilibiliChannelSeriesIE(BiliInfoExtractor):
    # https://space.bilibili.com/592726738/channel/seriesdetail?sid=2357741&ctype=0
    _VALID_URL = r'https?://space.bilibili\.com/(?P<userid>\d+)/channel/seriesdetail.+sid=(?P<listid>\d+)'
    _GROUPED_BY = ['userid', 'listid']
    _API = r'https://api.bilibili.com/x/series/archives?mid={}&series_id={}&only_normal=true&sort=desc&pn={page}&ps=30'

    def parse_json(self, json_obj: dict, stop_after: bool = None) -> tuple:
        r = []
        for i in json_obj.json()['data']['archives']:
            if r'https://www.bilibili.com/video/{}'.format(
                    i['bvid']) == stop_after:
                return r, True
            r.append(
                [i['title'], r'https://www.bilibili.com/video/{}'.format(i['bvid'])])
            if stop_after is True:
                return r, True
        return r, len(r) == 0


class BilibiliEpisodesIE(BiliInfoExtractor):
    # https://www.bilibili.com/video/BV1zP411V7ap
    _VALID_URL = r'https?://www.bilibili\.com/video/(?P<bvid>BV.+)\?*.*'
    _GROUPED_BY = ['bvid']
    _API = r'https://api.bilibili.com/x/player/pagelist?bvid={}&jsonp=jsonp'

    def extract_API(
            self,
            *args,
            stop_after: str = None,
            time_wait=0.5) -> list:
        r = []
        k = requests.get(self._API.format(*args))
        try:
            parsed, return_signal = self.parse_json(
                json_obj=k, stop_after=stop_after, bvid=args[0])
        except:
            logging.error([self._API.format(*args),
                          'extractor parsing JSON failed'])
            raise
        r += parsed
        if return_signal:
            return r
        time.sleep(time_wait)
        return r

    def parse_json(self, json_obj: dict, bvid: str, stop_after: bool = None) -> tuple:
        r = []
        for i in reversed(json_obj.json()['data']):
            if r'https://www.bilibili.com/video/{}?p={}'.format(
                    bvid,
                    i['page']) == stop_after:
                return r, True
            r.append(
                [i['part'], r'https://www.bilibili.com/video/{}?p={}'.format(bvid, i['page'])])
            if stop_after is True:
                return r, True
        return r, len(r) == 0


class BilibiliChannelCollectionsIE(BiliInfoExtractor):
    _VALID_URL = r'https?://space.bilibili\.com/(?P<userid>\d+)/channel/collectiondetail.+sid=(?P<listid>\d+)'
    _GROUPED_BY = ['userid', 'listid']
    _API = r'https://api.bilibili.com/x/polymer/space/seasons_archives_list?mid={}&season_id={}&sort_reverse=false&page_num={page}&page_size=30'


class BilibiliChannelIE(BiliInfoExtractor):

    # r'https?://space.bilibili\.com/(?P<userid>\d+)/'
    _VALID_URL = 'https:\/\/space\.bilibili\.com\/(?P<userid>\d+)'
    _GROUPED_BY = ['userid']
    _API = r'https://api.bilibili.com/x/space/wbi/arc/search?mid={}&pn={page}&jsonp=jsonp&ps=50'

    def extract_API(
            self,
            *args,
            stop_after: str = None,
            time_wait=10,
            headers: dict = DEFAULT_UI) -> list:
        r = []
        for i in range(999):
            apiurl = self._API.format(*args, page=str(i + 1))
            parsed_url = urlparse(apiurl)
            logging.debug(['extract API', apiurl])
            print(parse_qs(parsed_url.query))
            qs = parse_qs(parsed_url.query)
            qs2 = {key: qs[key][0] for key in qs}
            newapiurl = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{get_query(qs2)}'
            print(['extract API', newapiurl])
            k = requests.get(newapiurl, headers=headers)
            parsed, return_signal = self.parse_json(
                json_obj=k, stop_after=stop_after)
            r += parsed
            if return_signal:
                return r
            time.sleep(time_wait)
        return r

    def parse_json(self, json_obj: dict, stop_after: bool = None) -> tuple:
        r = []
        try:
            if hasattr(json_obj, 'json'):
                jsonified_json = json_obj.json()
            else:
                jsonified_json = json_obj
            for i in jsonified_json['data']['list']['vlist']:
                if r'https://www.bilibili.com/video/{}'.format(
                        i['bvid']) == stop_after:
                    return r, True
                r.append(
                    [i['title'], r'https://www.bilibili.com/video/{}'.format(i['bvid'])])
                if stop_after is True:
                    return r, True
            return r, len(r) == 0
        except requests.exceptions.JSONDecodeError:
            json_txt = json_obj.text
            if '"code":-509,' in json_txt:
                logging.warn('triggered code -509')
                return self.parse_json(
                    json.loads(json_txt[json_txt.index('}') + 1:]),
                    stop_after
                )
            raise


class localGlob(Extractor):
    '''
    '''
    _VALID_URL = r'(?P<dirname>.+)'
    _GROUPED_BY = []

    def extract_API(
            self,
            *args,
            stop_after: str = None,
            time_wait=0.5) -> list:
        return [['', x] for x in glob.glob(args[0])]


def url_filter(r: list, or_keywords: list = [], no_keywords: list = []) -> list:
    '''
    keep item in r if item has one of the or keywords
    '''
    r2 = []
    for i in r:
        # if selecting by containing a keyword: then if that word doesnt appear, skip
        if len(or_keywords) > 0 and not (True in [x in i[0] for x in or_keywords]):
            continue
        # if selecting by not including a keyword; if that word does appera, skip
        if (True in [x in i[0] for x in no_keywords]):
            continue
        r2.append(i[1])
    return r2


EXTRACTORS = {
    'biliseries': BilibiliChannelSeriesIE,
    'bilicolle': BilibiliChannelCollectionsIE,
    'biliepisode': BilibiliEpisodesIE,
    'bilichannel': BilibiliChannelIE,
    'glob': localGlob,
}

FILTERS = {
    None: lambda r: [x[1] for x in r],
    'karaoke': lambda r: url_filter(r, or_keywords=['歌', '唱', '黑听']),
    'moonlight': lambda r: url_filter(r, or_keywords=['歌', '唱', '黑听', '猫猫头播放器']),
    'nopart': lambda r: url_filter(r, no_keywords=['part',]),
    'nogame': lambda r: url_filter(r, no_keywords=['游戏',]),
    'song_from_stream': lambda r: url_filter(r, or_keywords=['歌切',]),
    'hachi': lambda r: url_filter(r, or_keywords=['歌回合集',]),
}


def extract_wrapper(url, extractor=EXTRACTORS['biliepisode'](), filter=FILTERS[None]):
    return filter(extractor.extract(url))
