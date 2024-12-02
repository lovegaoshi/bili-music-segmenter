# use GHactions to segment. segment only processes audio and let uploader handles the
# rest. only runs 1 to patronize on parallel gh runners.
import subprocess
import json

from ghsegment.constants import write_watched_URL, get_watched_URL, \
    write_biliup_data, get_biliup_data
from network.download import ytbdl
from utils.process import cell_stdout
from utils.logging import SAVE_YAML_PATH

def segment(media):
    downloaded_media = ytbdl(media, soundonly='-f bestaudio', aria=16)
    if not cell_stdout([
        'python',
        'inaseg.py',
        '--media={}'.format(downloaded_media),
        '--shazam',
            '--cleanup']) == 0:
        raise BaseException()
    with open(SAVE_YAML_PATH, 'r') as f:
        return downloaded_media, json.load(f)
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument(
        '--seg-index', type=int, default=0)
    args = parser.parse_args()
    old_urls = get_watched_URL()
    try:
        segment_biliup_data = segment(old_urls[args.seg_index])
        subprocess.call(['git', 'pull'])
        new_url = get_watched_URL()
        new_url.remove(old_urls[args.seg_index])
        write_watched_URL(new_url)
        biliup_data = get_biliup_data()
        biliup_data[segment_biliup_data[0]] = segment_biliup_data[1]
        write_biliup_data(biliup_data)
        # subprocess.call(['git', 'push'])
    except:
        pass

