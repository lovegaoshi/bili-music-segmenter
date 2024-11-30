import re
import logging
import json
import os

from inacelery.celery import add
from network.extractor import WRAPPER_CONFIG_DIR as CONFIG_DIREC
from utils.process import cell_stdout

DEFAULT_SETTINGS = {
    "biliup_routes": ['qn'],
}
BILIUP_ROUTE = 'qn'  # 'kodo'
RETRY_ROUTES = DEFAULT_SETTINGS['biliup_routes']

def bilibili_upload(
        globbed,
        media_basename,
        source=None,
        description=None,
        episode_limit=180,
        route='qn',
        useCelery=True):
    # because my ytbdl template is always "[uploader] title.mp4" I can extract
    # out uploader like this and use as a tag:
    keystamps = json.load(open(CONFIG_DIREC, encoding='utf-8'))
    try:
        ripped_from = re.compile(r'\[(.+)\].+').match(media_basename).group(1)
        # ripped_from = re.findall(r'\[.+\]', media_basename)[0][1:-1]
        if source is None:
            try:
                source = keystamps[ripped_from][0]
            except KeyError:
                raise KeyError('cant determine source url for this repost')
    except BaseException:
        ripped_from = source = description = 'n/a'
    if description is None:
        try:
            description = keystamps[ripped_from][1]
        except IndexError:
            description = f'关注{ripped_from}：{source}'
    try:
        tags = keystamps[ripped_from][2]
    except IndexError:
        tags = [ripped_from]
    except KeyError:
        tags = [ripped_from]
    title = media_basename[:media_basename.rfind('.')][:60]
    # title rework: [歌切][海德薇Hedvika] 20220608的直播歌曲
    title = f'[{ tags[0]}] {os.path.splitext(media_basename)[0][-8:]}的直播歌曲'
    title = media_basename[:media_basename.rfind('.')][:60].replace(
        ripped_from, tags[0]).replace('【直播回放】', '')
    globbed = sorted(globbed)
    globbed_episode_limit = []
    for i in range(len(globbed) // episode_limit + 1):
        if globbed[i] == media_basename:
            continue
        globbed_episode_limit.append(
            globbed[i * episode_limit: (i + 1) * episode_limit])

    def make_cmds(v):
        cmd = ['biliup', 'upload',]
        for x in v:
            cmd.append(x)
        cmd.extend([
            '--copyright=2',
            f'--desc={description}',
            '--tid=31',
            f'--tag={",".join(tags)}',
            f'--title=[歌切] {title[:60]}{episode_limit_prefix}',
            f'--source={source}',
            f'-l={route}',
        ])
        return cmd

    for i, v in enumerate(globbed_episode_limit):
        if i > 0:
            episode_limit_prefix = '_' + chr(97 + i)
        else:
            episode_limit_prefix = ''
        retry = 0
        cmd = make_cmds(v)
        if useCelery:
            # use inaCelery
            relocated_dir_on_fail = os.path.join(
                os.path.dirname(globbed_episode_limit[i][0]),
                'inaupload',
                f'{title.replace(" ", "_")}'
            )
            os.mkdir(relocated_dir_on_fail)
            for item in globbed_episode_limit[i]:
                os.rename(
                    item,
                    os.path.join(relocated_dir_on_fail, os.path.basename(item)))

            for index, item in enumerate(globbed_episode_limit[i]):
                globbed_episode_limit[i][index] = os.path.join(
                    relocated_dir_on_fail, os.path.basename(item))
            cmd = make_cmds(v)
            logging.info(['deferring', cmd, 'to celery:'])
            with open(os.path.join(relocated_dir_on_fail, 'cmd.txt'), 'w') as f:
                json.dump(cmd, f)
            add.delay(json.dumps(cmd))
            return

        while cell_stdout(cmd, encoding="utf-8") != 0:
            rescue = []
            for item in globbed_episode_limit[i]:
                if os.path.isfile(item):
                    rescue.append(item)
            globbed_episode_limit[i] = rescue
            retry += 1
            logging.warning(['upload failed, retry attempt', retry])
            route = RETRY_ROUTES[retry % len(RETRY_ROUTES)]
            if retry > 15:
                relocated_dir_on_fail = f'{title.replace(" ", "_")}'
                os.mkdir(relocated_dir_on_fail)
                for item in globbed_episode_limit[i]:
                    os.rename(item, os.path.join(
                        relocated_dir_on_fail, os.path.basename(item)))
                logging.warning(f'max retry of {retry} reached. \
                    files have been moved to {relocated_dir_on_fail}.')
                raise Exception(
                    'biliup failed for a total of {} times'.format(
                        str(retry)))