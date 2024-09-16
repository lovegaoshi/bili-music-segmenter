
import time
import json
import sys
import logging

from bilitag.cookiedfixer import fix_tags_json
from bilitag.fixer import get_bilitag_bvid, get_bilitag_cycle
from utils.timestamp import sec2timestamp

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument(
        '--watch_interval',
        type=int,
        default=0,
        help='in seconds. 0 means no repeat.')
    parser.add_argument(
        '--log_level',
        type=int,
        default=logging.INFO,
        help='in seconds. 0 means no repeat.')
    parser.add_argument(
        '--bvid',
        type=str,
        default="",
        help='in seconds. 0 means no repeat.')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=args.log_level
        )
    
    if args.bvid != "":
        old_dict = json.load(open('bili_tag_fix_tags.json'))
        json.dump(
            get_bilitag_bvid(args.bvid, old_dict),
            open('bili_tag_fix_tags.json', 'w'),
            indent=4
        )
        sys.exit(0)

    from datetime import datetime
    while True:
        current_time = datetime.now()
        logging.info(['biliWatcher loop has started on ',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        try: 
            with open('bili_tag_fix_tags.json') as f:
                old_dict = json.load(f)
        except:
            old_dict = {}
        fix_tags_json(get_bilitag_cycle(old_dict))
        
        '''
        json.dump(
            get_bilitag_cycle(old_dict),
            open('bili_tag_fix_tags.json', 'w'),
            indent=4)
        '''

        if args.watch_interval < 1:
            sys.exit(0)
        logging.info([
            'biliWatcher loop is now waiting for ', sec2timestamp(args.watch_interval)])
        time.sleep(max(args.watch_interval, (datetime.now() - current_time).seconds))