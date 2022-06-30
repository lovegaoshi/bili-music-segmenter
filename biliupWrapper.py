import re

def cell_stdout(cmd, silent = False, encoding=None):
    print('calling', cmd, 'in terminal:')
    with subprocess.Popen(cmd) as p:
        p.wait()
    return p.returncode

def bilibili_upload(globbed, media_basename, source = None, description = None, episode_limit=10):
    ripped_from = re.findall('\[.+\]', media_basename)[0][1:-1]
    if source is None:
        try:
            source = keystamps[ripped_from][0]
        except KeyError:
            raise KeyError('cant determine source url for this repost')
            source = ' '
    if description is None:
        try:
            description = keystamps[ripped_from][1]
        except:
            description = '关注{}：{}'.format(
                                           ripped_from,
                                           source,)
    try:
        tags = keystamps[ripped_from][2]
    except:
        tags = [ripped_from]
    title = media_basename[:media_basename.rfind('.')][:60]
    # title rework: [歌切][海德薇Hedvika] 20220608
    title = tags[0] + ' ' + os.path.splitext(media_basename)[0][-8:]
    globbed = sorted(globbed)
    globbed_episode_limit = []
    for i in range(len(globbed) // episode_limit + 1):
        globbed_episode_limit.append(globbed[i * episode_limit : (i + 1) * episode_limit])
    
    for i in range(len(globbed_episode_limit)):
        if i > 0: episode_limit_prefix = '_' + chr(97 + i)
        else: episode_limit_prefix = ''
        retry = 0
        cmd = [
                './biliup',
                'upload',
            ]
        for x in globbed_episode_limit[i]: cmd.append(x)
        cmd.append('--copyright=2')
        cmd.append('--desc={}'.format(description))
        cmd.append('--tid=31')
        cmd.append('--tag={}'.format(','.join(tags)))
        cmd.append('--title=[歌切]{}'.format(media_basename[:media_basename.rfind('.')][:60] + episode_limit_prefix))
        cmd.append('--source={}'.format(source))
        while cell_stdout(cmd) != 0:
            retry += 1
            if retry > 10: raise Exception('biliup failed for a total of {} times'.format(str(retry)))
#=================================================================================================================    
#AIO 一键url to b站上传
#=================================================================================================================
import glob, json, os
from inaseg import ytbdl, strip_medianame_out, shazaming, put_medianame_backin
keystring = ''
import json
try:
    keystamps = json.load(open('keystamps.json', 'r'))
except:

    keystamps = {
        '贝萨Bessa':[r'https://live.bilibili.com/22288476',
                    r'关注贝萨贝老师：https://space.bilibili.com/592726738/'],
        '海德薇的录播组':[r'https://live.bilibili.com/24088644',
                    r'关注海德薇海老师：https://space.bilibili.com/1285890335/',
                ['海德薇Hedvika']],
        '末莱Moonlight':[
            r'https://live.bilibili.com/24463489',
            '关注末莱Moonlight木老师：https://space.bilibili.com/476185026'
        ],
        '范塞尼尔录播组':[
            r'https://live.bilibili.com/24963677',
            '关注范塞尼尔_VamSenior喵，关注范塞尼尔_VamSenior谢谢喵：https://space.bilibili.com/2042629175',
            ['范塞尼尔_VamSenior']
        ],
        '盖乃希亞Galaxy':[
            r'https://live.bilibili.com/22864117',
            '关注盖乃希亞Galaxy盖老师：https://space.bilibili.com/1846208014',
        ],
        '莱妮娅_Rynia':[
            r'https://live.bilibili.com/22605289',
            '关注莱妮娅_Rynia莱老师：https://space.bilibili.com/703018634/channel/series',
        ],
    }
    json.dump(open('keystamps.json','w'), keystamps)
                #https://www.bilibili.com/video/BV12v4y1M7Vy

cleanup = True#False
import subprocess
outdir = '/tf/out' #os.getcwd()#r'D:\tmp\ytd\hedvika'
from inaseg import extract_music, segment, extract_mah_stuff
import os
import argparse
parser = argparse.ArgumentParser(description='ina music segment')
parser.add_argument('--media', type=str, nargs='+', help = 'file path or weblink')
if __name__ == '__main__':
    args = parser.parse_args()
    rs = args.media
    for media in rs:
        if media == '': continue
        os.chdir('/tf/out')
        if 'https:' in media: media = ytbdl(media, soundonly = '', aria = 16)#, outdir = outdir
        if not cell_stdout(['python','inaseg.py', '--media={}'.format(media), '--outdir={}'.format(outdir), '--soundonly', '']) == 0: continue
        #extract_mah_stuff(media, extract_music(segment(media)), outdir = outdir, rev=False, soundonly = False)    
        print('inaseg completed on', media)
        shazaming(outdir, media, threads = 4)
        stripped_media_names = strip_medianame_out(outdir, media)
        print('preparing to upload', stripped_media_names)
        #b站大小姐只想让我上传10p？？
        #well apparently biliup checks json at current DIR instead of its dir
        bilibili_upload(stripped_media_names, os.path.basename(media), source = None, episode_limit=180)
        if cleanup:
            os.remove(media)
            for i in stripped_media_names: os.remove(i)
        print('finished stripping and uploading', media)
        if not cleanup: put_medianame_backin(stripped_media_names, media, shazamed = r'D:\tmp\ytd\convert2music', nonshazamed = r'D:\tmp\ytd\extract')

