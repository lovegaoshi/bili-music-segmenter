import requests
import time
import logging
import re
import os
import shutil


from network.watcher import watch
from network.constants import DEFAULT_UI

GET_CID_URL = "https://api.bilibili.com/x/web-interface/view?bvid={}"
GET_TAG_URL = "https://api.bilibili.com/x/web-interface/view/detail/tag?bvid={}&cid={}"
BILI_SHAZAM_TAG_TYPE = 'bgm'
BVID_RE_STR = 'BV[^\/]+'

def get_cid_list_from_bvid(bvid: str = 'BV1A24y1s7r7') -> list:
    time.sleep(0.2)
    r = requests.get(GET_CID_URL.format(bvid), headers=DEFAULT_UI)
    res = r.json()
    return [[res['data']['bvid'], str(page['cid']), str(page['page'])]
    for page in res['data']['pages']]

def get_cid_list_from_bvids(bvids: list = []) -> list:
    result = []
    for bvid in bvids:
        try:
            result.extend(get_cid_list_from_bvid(re.search(BVID_RE_STR, bvid).group(0)))
        except AttributeError:
            logging.error(f'is {bvid} a vaid bvid?')
    return result

def get_tag_from_cid_bvid(bvid: str, cid: str, timeout: float = 1.0) -> str|None:
    time.sleep(timeout)
    try:
        r = requests.get(GET_TAG_URL.format(bvid, cid), headers=DEFAULT_UI).json()
        tag = r['data'][0]
        if tag['tag_type'] == BILI_SHAZAM_TAG_TYPE: 
            return tag['tag_name'][3:-1]
    except:
        logging.error(f'bvid:{bvid} cid:{cid} failed to fetch bili get tag.')
    return None

def get_bilitag_bvid(bvid, tag_dict = None):
    if tag_dict is None: tag_dict = {}
    reqs = get_cid_list_from_bvid(bvid)
    for index, bvid_cid_pair in enumerate(reqs):
        if bvid_cid_pair[0] not in tag_dict:
            tag_dict[bvid_cid_pair[0]] = {}
        val = get_tag_from_cid_bvid( 
            bvid_cid_pair[0],
            str(bvid_cid_pair[1]),
        )
        if val is not None:
            tag_dict[bvid_cid_pair[0]][bvid_cid_pair[2]] = val
    return tag_dict


def get_bilitag_cycle(tag_dict = None, bvids = None):
    if tag_dict is None:
        tag_dict = {}
    # json.load(open('bili_tag_fix_data1.json'))#
    try:
        if bvids is None:
            bvids = watch(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                'configs',
                'biliTag.yaml')
            )
        reqs = get_cid_list_from_bvids(bvids)
    except Exception as e:
        logging.error(e)
        time.sleep(100)
        if not os.path.isfile(os.path.join(os.path.dirname(
                    os.path.abspath(__file__)),
                'configs',
                'biliTag.yaml')):
            shutil.copy2(os.path.join(os.path.dirname(
                    os.path.abspath(__file__)),
                'configs',
                'biliTag.yaml.old'),os.path.join(os.path.dirname(
                    os.path.abspath(__file__)),
                'configs',
                'biliTag.yaml'))
        reqs = []
    reqlen = str(len(reqs))
    for index, bvid_cid_pair in enumerate(reqs):
        logging.info(f'now processing {str(index)}/{reqlen}: bvid:{bvid_cid_pair[0]}, cid:{str(bvid_cid_pair[1])}')
        if bvid_cid_pair[0] not in tag_dict:
            tag_dict[bvid_cid_pair[0]] = {}
        val = get_tag_from_cid_bvid( 
            bvid_cid_pair[0],
            str(bvid_cid_pair[1]),
        )
        if val is not None:
            tag_dict[bvid_cid_pair[0]][bvid_cid_pair[2]] = val
    return tag_dict
