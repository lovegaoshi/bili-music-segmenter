import requests
import json
import time
import logging

from network.constants import DEFAULT_UI

hangul_ranges = (
    range(0xAC00, 0xD7A4),  # Hangul Syllables (AC00–D7A3)
    range(0x1100, 0x1200),  # Hangul Jamo (1100–11FF)
    range(0x3130, 0x3190),  # Hangul Compatibility Jamo (3130-318F)
    range(0xA960, 0xA980),  # Hangul Jamo Extended-A (A960-A97F)
    range(0xD7B0, 0xD800),  # Hangul Jamo Extended-B (D7B0-D7FF)
)
is_hangul = lambda c: any(ord(c) in r for r in hangul_ranges)
is_str_hangul = lambda r: any([is_hangul(c) for c in r])

def load_cookies(fn="cookies.json"):
    with open(fn) as f:
        loaded_cookies = json.load(f)
    cookies = {}
    for cookie in loaded_cookies["cookie_info"]["cookies"]:
        cookies[cookie["name"]] = cookie["value"]
    return cookies


def get_bv_info(bvid, cookies=load_cookies()):
    url = (
        f"https://member.bilibili.com/x/vupre/web/archive/view?topic_grey=1&bvid={bvid}"
    )
    r = requests.get(
        url, cookies={"SESSDATA": cookies["SESSDATA"]}, headers=DEFAULT_UI, timeout=100)
    rjson = r.json()["data"]
    result = {
        "cover": rjson["archive"]["cover"],
        "title": rjson["archive"]["title"],
        "copyright": rjson["archive"]["copyright"],
        "source": rjson["archive"]["source"],
        "tid": rjson["archive"]["tid"],
        "tag": rjson["archive"]["tag"],
        "desc_format_id": rjson["archive"]["desc_format_id"],
        "desc": rjson["archive"]["desc"],
        "recreate": -1,
        "dynamic": rjson["archive"]["dynamic"],
        "interactive": rjson["archive"]["interactive"],
        "aid": rjson["archive"]["aid"],
        "new_web_edit": 1,
        "videos": [],
        "act_reserve_create": 0,  # false is 0? true is what?
        "handle_staff": False,
        "topic_grey": 1,
        "mission_id": 0,
        "subtitle": {"open": 0, "lan": ""},
        "is_360": -1,
        "web_os": 1,
        "csrf": cookies["bili_jct"],
    }

    for video in rjson["videos"]:
        result["videos"].append(
            {
                "filename": video["filename"],
                "title": video["title"],
                "desc": video["desc"],
                "cid": video["cid"],
            }
        )
    return result


def post_bvid_edit(payload, cookies=load_cookies()):
    return requests.post(
        f'https://member.bilibili.com/x/vu/web/edit?csrf={payload["csrf"]}',
        json=payload,
        cookies={"SESSDATA": cookies["SESSDATA"]},
        timeout=100,
        headers=DEFAULT_UI
    )

def fix_tags_json(old_dict):
    for bvid in old_dict:
        bvinfo = get_bv_info(bvid)
        logging.debug('POSTing to fix %s', bvid)
        for bvindex in old_dict[bvid]:
            if is_str_hangul(old_dict[bvid][bvindex]):
                logging.warn('skipping titles containing hangul...')
                continue
            bvinfo['videos'][int(bvindex) - 1]["title"] = old_dict[bvid][bvindex]
        logging.debug(post_bvid_edit(bvinfo).json())
        time.sleep(10)

def fix_tags(json_fn = 'bili_tag_fix_tags.json'):
    with open(json_fn) as f:
        old_dict = json.load(f)
    fix_tags_json(old_dict)
    with open(json_fn, 'w') as f:
        json.dump(
            {},
            f)

    
if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument(
        '--bvid',
        type=str,
        help='in seconds. 0 means no repeat.')

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG
        )
    fix_tags()