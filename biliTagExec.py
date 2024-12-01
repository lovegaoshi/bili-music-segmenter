from biliTagFixer import get_bilitag_cycle
from biliCookiedTagFixer import fix_tags_json
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG
    )

fix_tags_json(get_bilitag_cycle(bvids = ['https://www.bilibili.com/video/BV1aQ4y177FE']))