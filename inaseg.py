# 媒体流最大时长处理（秒）；1G内存的进程推荐用10分钟/600秒，16G可以支持5小时，6GB VRAM可以支持5小时左右。
SEGMENT_THRES = 600
# 识歌分段最小阈值（秒），调大了会漏 调小了会多杂谈
EXTRACT_SEG_THRES = 60
# 最终识歌分段最小阈值（秒），调大了漏TV size 调小了多杂谈
EXTRACT_SEG_THRES_FINAL = 80
# 识歌分段连接的阈值（秒），调大了会两首歌分不开 调小了会碎
EXTRACT_SEG_CONNECT = 5
COOKIES_LOCATION = ['--cookies-from-browser', 'firefox']

# Load the API
from inaSpeechSegmenter import Segmenter
import subprocess, os, glob
from threading import Thread
from inaConstant import load_config, save_config
import gc
import logging
import math
import tempfile
import regex

SAVE_YAML_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'save.yaml')

class KoreanCharException(BaseException):
    pass

class TimestampMismatch(Exception):
    pass

# select a media to analyse
# any media supported by ffmpeg may be used (video, audio, urls)
import json, shutil

def segment(media, batch_size=32, energy_ratio=0.02, start_sec: int = None, stop_sec: int = None):
    logging.info(('segmenting', media.encode('utf-8')))
    segmenter = Segmenter(
        vad_engine='sm',
        detect_gender=False,
        energy_ratio=energy_ratio,
        batch_size=batch_size)
    segmentation = segmenter(media, start_sec=start_sec, stop_sec=stop_sec)
    return segmentation


def segment_wrapper(media: str, batch_size: int = 32, energy_ratio: float = 0.02, segment_length_thres:int = 0):
    ''''''
    result = []
    for i in get_segment_process_length_array(media, segment_length_thres):
        result += segment(media, batch_size, energy_ratio, start_sec=i[0], stop_sec=i[1])
        gc.collect()
        tf.keras.backend.clear_session()
    return result

def get_segment_process_length_array(filename: str, thres: int = 0):
    if not thres: return [[None, None]]
    file_length = timestamp2sec(get_length(filename))
    if thres > file_length: return [[None, None]]
    logging.debug((f'filelength {str(file_length)} is larger than thres {str(thres)}, triggering a segmentation.'))
    result = [[ x * thres, (x + 1) * thres ] for x in range(math.ceil(file_length / thres))]
    result[0][0] = None
    result[-1][1] = None
    return result

def extract_music(segmentation, segment_thres = EXTRACT_SEG_THRES, segment_thres_final = EXTRACT_SEG_THRES_FINAL, 
                  segment_connect = EXTRACT_SEG_CONNECT, start_padding = 1, end_padding = 2):
    r = []
    #bridges noEnergy segments that are likely fragmented
    for i in range(len(segmentation)-2, 0, -1):
        if segmentation[i][0] == 'noEnergy' and segmentation[i][2] - segmentation[i][1] < 2 and \
        segmentation[i-1][0] == segmentation[i+1][0]:
            segmentation[i-1] = (segmentation[i-1][0], segmentation[i-1][1], segmentation[i+1][2])
    for i in segmentation: 
        if i[0] == 'music' and i[2]-i[1] > segment_thres: r.append(['',i[1] - start_padding, i[2] + end_padding])    
    for i in range(len(r)-1, 0, -1):
        if r[i][1] - r[i-1][2] < segment_connect:
            r[i-1][2] = r[i][2]
            r[i][1] = r[i][2] + 1    
    rf = []
    for i in r:
        if i[1] < 5: continue
        if i[2]-i[1] > segment_thres_final: rf.append(i)
    return [['{}:{}:{}'.format(str(int(x[1]//3600)), 
                               str(int(x[1] % 3600 //60)), 
                               str(int(x[1] % 60)).zfill(2)), 
             '{}:{}:{}'.format(str(int(x[2]//3600)), 
                               str(int(x[2]  % 3600  //60)), 
                               str(int(x[2] % 60)).zfill(2))] for x in rf]


def extract_mah_stuff(media, segmented_stamps, outdir = None, rev = False, delimited = '/', timestamps = [], soundonly = True):
    nameswitch = False
    timestamps_ext = segmented_stamps#extract_music(segmentation)#[['{}:{}:{}'.format(str(int(x[1]//3600)), str(int(x[1] % 3600 //60)), str(int(x[1] % 60)).zfill(2)),  '{}:{}:{}'.format(str(int(x[2]//3600)), str(int(x[2]  % 3600  //60)), str(int(x[2] % 60)).zfill(2))] for x in r]
    try:
        if len(timestamps) > 0: raise FileNotFoundError()
        for i in open(r"D:\tmp\ytd\timstamp.ini", 'r', encoding='UTF-8'):
            for k in [['\n',''],['」', ''],['~「',' '],['「', ' '],['『', ' '],['』', ' '],['　', ' '],['	', ' '],['\'',''],]:
                i = i.replace(k[0], k[1])
            if ' （' in i: i = i[:i.find(' （')]
            if ':' in i:
                timestamps.append([i[:i.find(' ')], i[i.find(' ')+1:]])
                #timestamps[-1][1] = timestamps[-1][1][1:]
                if delimited in timestamps[-1][1]:
                    timestamps[-1][1] = [timestamps[-1][1][:timestamps[-1][1].find('/')],
                                         timestamps[-1][1][timestamps[-1][1].find('/')+1:], ]
                    if rev: timestamps[-1][1].reverse()
                    timestamps[-1][1] = ' by '.join(timestamps[-1][1])
                #timestamps[-1][1].replace('/', ' by ')
                #timestamps[-1][1] = ' by '.join(timestamps[-1][1].split('/'))
                #timestamps[-1][1] = timestamps[-1][1].replace('-', 'by')
                while timestamps[-1][1][0] == ' ': timestamps[-1][1] = timestamps[-1][1][1:]
                while timestamps[-1][1][-1] == ' ': timestamps[-1][1] = timestamps[-1][1][:-1]
        #        nameswitch = True
            elif nameswitch:
                nameswitch = False
                timestamps[-1].append(i)
        if len(timestamps) > 0:# and len(timestamps) != len(timestamps_ext): 
            #raise TimestampMismatch('check timestamp assist', timestamps, timestamps_ext)
            #print('timestamp mismatch, removing missing ones...(come on, are you really gonna do this manually)')
            print('checking timestamp correspondence and removing mismatched ones (come on, are you really gonna do this manually)')
            timestamps = fix_missing_stamps(timestamps, timestamps_ext)
            timestamps_ext = fix_missing_stamps(timestamps_ext, timestamps)
            if len(timestamps) != len(timestamps_ext): 
                raise TimestampMismatch('check timestamp assist', timestamps, timestamps_ext)
        with open(r"D:\tmp\ytd\timstamp.ini", 'w') as f:
            pass
    except FileNotFoundError:
        pass
    if len(timestamps) > 0: print('timestamp assist', [ [timestamps[x][0], timestamps_ext[x][1], timestamps[x][1], ] for x in range(len(timestamps))])
    else: print('extracted timestamps', ['{} - {}'.format(x[0], x[1]) for x in timestamps_ext])
    
    save = load_config(SAVE_YAML_PATH)
    save[os.path.basename(media)] = timestamps_ext
    save_config(SAVE_YAML_PATH, save)
    nameswitch = False
    file = media
    filename = file[:file.rfind('.')]
    fileext = file[len(filename):]
    filename = os.path.basename(filename)
    cmds = []
    for i in range(len(timestamps_ext)):
        oud = outdir if outdir else os.path.dirname(file)
        encoding = ['-c:v','copy','-c:a', 'copy']#'-c:v copy -c:a copy'
        if soundonly:
            encoding = ['-vn','-ab','320k']#'-vn -ab 320k'
            fileext = '.mp3'
        try:
            prefix = timestamps[i][1].zfill(2)
            cmds.append([
                'ffmpeg',
                '-i',
                "{}".format(file),
                ] + encoding + [
                '-ss',
                timestamps[i][0],
                '-to',
                timestamps_ext[i][1],
                "{}".format(os.path.join(oud, filename + '_{}_{}'.format(str(i), prefix) + fileext)),

            ] + encoding)
        except:
            prefix = str(i).zfill(2)
            cmds.append([
                'ffmpeg',
                '-i',
                "{}".format(file),
            ] + encoding + [
                '-ss',
                timestamps_ext[i][0],
                '-to',
                timestamps_ext[i][1],
                "{}".format(os.path.join(oud, filename + '_' + prefix + fileext)),

            ])
    k = [Thread(target=ffmpeg, args=(x,)) for x in cmds]
    for i in k: i.start()
    k[-1].join()
    
from ShazamAPI import Shazam
import time, json
def shazam(mp3, stop_at_first_match = 1, force_sleep = 5):
    mp3_file_content_to_recognize = open(mp3, 'rb').read()
    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()
    matches = []
    try:
        while True:
            match = next(recognize_generator)
            if len(match[1]['matches']) > 0: 
                matches.append(match)
                if len(matches) > stop_at_first_match: raise StopIteration()
    except StopIteration:
        pass
    return matches

def legalize_filename(fn):
    if regex.search(r'\p{IsHangul}',fn) is not None:
        raise KoreanCharException(fn)
    illegal_list = [
        [':', ' '],
        ['"', ''],
        [r'/', ''],
        [r'?', ''],
        [r'*', ''],
        ['\'',''],
        ['<',''],
        ['>',''],
    ]
    for i in illegal_list: fn = fn.replace(i[0],i[1])
    return fn

def shazam_title(match):
    title = legalize_filename(match[1]['track']['title'])
    if 'in the style of' in title.lower():
        artist = title[title.lower().index('in the style of ') + len('in the style of '):]
        artist = artist[:artist.index(')')]
    else: artist = legalize_filename(match[1]['track']['subtitle'])

    return [
    legalize_filename(match[1]['track']['title']),
    legalize_filename(match[1]['track']['subtitle']),    
    ]

import requests
def shazam_coverart(match, fn, outdir):
    try:
        albumart = match[1]['track']['images']['coverarthq']
        req = requests.get(albumart)
        with open(os.path.join(outdir, os.path.basename(fn) + albumart[albumart.rfind('.'):]), 'wb') as f:
            f.write(req.content)
    except:
        pass

import os, subprocess, time, multiprocessing

def concurrent_ffmpeg(target = 'ffmpeg'):
    return 0
    # windows powershell only!
    lists = str(subprocess.check_output('pslist')).split('\\n')
    r = 0
    for i in lists:
        if target in i: r += 1
    return r

def ffmpeg(cmd, concurrent_limit = multiprocessing.cpu_count(), wait = True):
    process = subprocess.Popen(cmd)
    if wait: process.wait()
    return 1


from subprocess import Popen, PIPE
from difflib import SequenceMatcher as SM
#fuzzy match! 
def ytbdl(url: str, soundonly: str = '-f bestaudio', outdir: str = tempfile.gettempdir(), aria: int = None) -> list:
    r = ''# --restrict-filenames
    fname = None
    #./youtube-dl
    cmd = ['yt-dlp', url, '-o', os.path.join(outdir, "[%(uploader)s] %(title)s %(upload_date)s.%(ext)s")]
    cmd.extend(COOKIES_LOCATION)       
    if aria is not None: 
        cmd.append('--external-downloader')
        cmd.append('aria2c')
        cmd.append('--external-downloader-args')
        cmd.append('-x {} -s {} -k 1M'.format(str(aria), str(aria)))
    if len(soundonly.split(' ')) > 1:
        cmd.extend(soundonly.split(' '))
    print(cmd)
    with Popen(cmd, stdout=PIPE, 
               universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')
            if '[download] Destination' in line: fname = line[len('[download] Destination: '):-1]
            elif 'has already been downloaded' in line: fname = line[len('[download] '):-len(' has already been downloaded') - 1]
            elif '[Merger]' in line: fname = line[len('[Merger] Merging formats into "'):-2]
    if fname is None: raise Exception('no ytbdl resutls!')
    print('mathcing', fname)
    ext = fname[fname.rfind('.'):]
    ext = ext.split(' ')[0]
    r = []
    for i in glob.glob(os.path.join(
        os.path.dirname(fname),
        '*' + ext
    )):
        r.append([
            i,
            SM(isjunk=None, a = os.path.basename(fname), b = os.path.basename(i)).ratio()
        ])
    return sorted(r, key = lambda x: x[1], reverse = True)[0][0]

from difflib import SequenceMatcher as SM
def fuzzy_match_my_file(fname):
    ext = fname[fname.rfind('.'):]
    r = []
    for i in glob.glob(os.path.join(
        os.path.dirname(fname),
        '*' + ext
    )):
        r.append([
            i,
            SM(isjunk=None, a = os.path.basename(fname), b = os.path.basename(i)).ratio()
        ])
    return r
    pass

saved_timestamp = None

    
def timestamp2sec(timestamp):
    # hurr durr...
    timestamp = timestamp.split(':')
    timestamp.reverse()
    seconds = 0
    for i in range(len(timestamp)): seconds += int(float(timestamp[i])) * pow(60, i)
    return seconds

def is_stamp_missing(stamp, stamps, secrange = 40):
    stamp_sec = timestamp2sec(stamp[0])
    for i in stamps:
        i_sec = timestamp2sec(i[0])
        if i_sec > stamp_sec + secrange: return True
        if abs(i_sec-stamp_sec) < secrange: return False
    return True

def fix_missing_stamps(stamps, stamps2):
    r = []
    for i in stamps:
        if not is_stamp_missing(i, stamps2): r.append(i)
        else: print(i, 'is missing and gone(puff)')
    return r

import re

def mus1ca_timestamp(description, delimited = ' /'):
    timestamps = []
    for i in open(description, 'r', encoding='UTF-8'):
        if len(re.findall('\d+:\d+', i)) == 0: continue
        i = i.replace('\n','').replace('」', '').replace('~',' ').replace('「', ' ').replace('『', ' ').replace('』', ' ')
        if ':' in i:
            timestamps.append([i[:i.find(' ')], i[i.find(' ')+1:]])
            #timestamps[-1][1] = timestamps[-1][1][1:]
            if delimited in timestamps[-1][1]:
                timestamps[-1][1] = [timestamps[-1][1][:timestamps[-1][1].find('/')],
                                     timestamps[-1][1][timestamps[-1][1].find('/')+1:], ]
                timestamps[-1][1] = ' by '.join(timestamps[-1][1])
            #timestamps[-1][1].replace('/', ' by ')
            #timestamps[-1][1] = ' by '.join(timestamps[-1][1].split('/'))
            #timestamps[-1][1] = timestamps[-1][1].replace('-', 'by')
            while timestamps[-1][1][0] == ' ': timestamps[-1][1] = timestamps[-1][1][1:]
            while timestamps[-1][1][-1] == ' ': timestamps[-1][1] = timestamps[-1][1][:-1]

    return timestamps

def get_length(filename):
    if not filename:
        return "0"
    result = subprocess.run(["ffprobe", "-v", "error",  '-sexagesimal', "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return str(result.stdout)[2:-5] #float() without -sexagesimal

def split_in_half(filename, ):
    length = timestamp2sec(get_length(filename))/2
    cmds = [
        'ffmpeg -i "{}" {} -c:v copy -c:a copy "{}"'.format(
            filename, 
            '-to {}'.format(str(length)),
            filename[:filename.rfind('.')] + "_a" + filename[filename.rfind('.'):]),
        'ffmpeg -i "{}" {} -c:v copy -c:a copy "{}"'.format(
            filename, 
            '-ss {} '.format(str(length)),
            filename[:filename.rfind('.')] + "_b" + filename[filename.rfind('.'):]),
        
            ]
    k = [Thread(target=ffmpeg, args=(x,)) for x in cmds]
    for i in k: i.start()
    k[-1].join()
    os.remove(filename)

def bili_name_trim(fn, base, char_lim = 75):
    file = fn[len(base) - 3:]
    filename = file[:file.rfind('.')]
    fileext = file[len(filename):]
    return filename[:char_lim] + fileext

def strip_medianame_out(outdir, media):
    mediab = os.path.basename(media)
    r = []
    for file in glob.glob(os.path.join(
            outdir, '*' + mediab[1:mediab.rfind('.')]+ '*'
        )):
        if file == media: continue
        outfile = os.path.join(
                os.path.dirname(file),
                bili_name_trim(os.path.basename(file), mediab)
            )
        shutil.move(
            file, 
            outfile
        )
        r.append(outfile)
    return r


def put_medianame_backin(filelists, media, shazamed = '', nonshazamed = ''):
    mediab = os.path.basename(media)
    mediab = mediab[:mediab.rfind('.')]
    r = []
    for file in filelists:
        if ' by ' in os.path.basename(file):
            outdir = shazamed if os.path.isdir(shazamed) else os.path.dirname(file)
        else:
            outdir = nonshazamed if os.path.isdir(nonshazamed) else os.path.dirname(file)            
        outfile = os.path.join(
                outdir,
                mediab + '_' + os.path.basename(file))
        shutil.move(
            file, 
            outfile
        )
        r.append(outfile)
    return r

def shazam_orig(file, **kwargs):
    match = shazam(file, stop_at_first_match = 1)[-1]
    return shazam_title(match), match


def shazaming(outdir, media, shazam_coverart_path = '', shazam_func = shazam_orig, ignore_fails = False, threads = 1):
    results = {}
    files = glob.glob(os.path.join(
            outdir, '*' + os.path.splitext(os.path.basename(media))[0][1:] + '_*'
        ))
    if threads > 1 and len(files) > 1:
        p = multiprocessing.Pool(min(threads, len(files)))
        from functools import partial
        p.map(partial(shazam_threaded, shazam_coverart_path = '', shazam_func = shazam_orig, ignore_fails = True),
        files)
        p.close()
        p.join()
    else: 
        for file in files:
            shazam_threaded(file, shazam_coverart_path = shazam_coverart_path, shazam_func = shazam_func, ignore_fails = ignore_fails)

    save = load_config(SAVE_YAML_PATH)
    mediab = os.path.basename(media)
    save[os.path.basename(media) + "shazam"] = glob.glob(os.path.join(
        outdir, '*' + mediab[1:mediab.rfind('.')] + '*'
    ))
    save_config(SAVE_YAML_PATH, save)
    
def shazam_threaded(file, shazam_coverart_path = '', shazam_func = shazam_orig, ignore_fails = True):
    results = {}
    if ' by ' in file: return
    filename = file[:file.rfind('.')]
    fileext = file[len(filename):]
    fn = os.path.basename(filename)
    print('shazaming', fn)
    try:
        #match = shazam(file, stop_at_first_match = 1)[-1]
        #results[fn] = shazam_title(match)
        results[fn], match = shazam_func(file)
        try:
            print(fn, 'shazam found to be', results[fn])
        except UnicodeEncodeError:
                print(fn, 'shazam found but cant show unicode burr durr')
        renamed_file = os.path.join(
            os.path.dirname(file),
            #    r'D:\tmp\ytd\convert2music',
            (fn + "_{} by {}".format(results[fn][0].replace(':', ' '), results[fn][1].replace(r'/', ''))) + fileext
        )
        shutil.move(file, renamed_file)
        if os.path.isdir(shazam_coverart_path): shazam_coverart(match, renamed_file, shazam_coverart_path)
    except IndexError:
        print(fn, 'shazam failed')
    except:
        if not ignore_fails: raise

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument('--media', type=str, help = 'file path or weblink')
    parser.add_argument('--outdir', type=str, default = tempfile.gettempdir(), help = 'directory media will be downloaded into (if url) and extracted into; if docker, use as the mounted folder! and make sure -u is you!')
    parser.add_argument('--shazam', action='store_true', default = False, help = 'shazam the extracted files')
    parser.add_argument('--shazam_coverart', type=str, default = '', help = 'save shazam cover art too')
    parser.add_argument('--aria', type=int, default = None, help = 'use aria, specifying the number of threads')
    parser.add_argument('--shazam_multithread', type=int, default = 1, help = 'use multithreaded shazam')
    parser.add_argument('--soundonly', type=str, default = r'-f bestaudio', help = 'specify an empty string to extract both video and audio')
    parser.add_argument('--seg_connect', type=int, default = 5, help = 'max seconds for 2 music segments to be considered the same (takes care of random miss-detection/small rap segments)')
    parser.add_argument('--cleanup', action='store_true', default = False, help = 'delete the original media file once completed.')
    parser.add_argument(
        '--max_segment_length',
        type=int,
        default=SEGMENT_THRES,
        help='for computers with limited RAM (eg a 5 hrs stream requires ~6GB VRAM), set this to process streams in this speficied segments to avoid ram overflow. in seconds.')

    args = parser.parse_args()
    #media = ytbdl('')
    if not args.media is None: media = args.media
    else: raise Exception('no media')
    if 'https:' in media: media = ytbdl(media, soundonly = args.soundonly, aria = args.aria, outdir = args.outdir)
    #media = r"D:\tmp\ytd\[莉犬くん【すとぷり】] 【激レア歌枠】とんでもないお知らせがあります。。。【莉犬】 20220607.webm"
    if len(glob.glob(os.path.join(args.outdir, '*' + os.path.splitext(os.path.basename(media))[0][1:] + '_*'))) == 0:
        import tensorflow as tf
        gpus = tf.config.experimental.list_physical_devices('GPU')
        print(gpus)
        if False and gpus:
        # Restrict TensorFlow to only allocate 1GB of memory on the first GPU: noope.
            try:
                tf.config.experimental.set_virtual_device_configuration(
                    gpus[0],
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=5424)])
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
                os.environ["TF_GPU_ALLOCATOR"]="cuda_malloc_async"
            except RuntimeError as e:
                # Virtual devices must be set before GPUs have been initialized
                print(e)
                raise 
        try:
            timestamps = []
            #timestamps = mus1ca_timestamp(media[:media.rfind('.')] + '.description')
            saved_timestamp = extract_music(segment_wrapper(media, segment_length_thres=args.max_segment_length), segment_connect = args.seg_connect)
            extract_mah_stuff(media, segmented_stamps=saved_timestamp, outdir = args.outdir, rev=False, timestamps = timestamps, soundonly = (args.soundonly != ''))
            saved_timestamp = None
        except TimestampMismatch:
            raise
    else: print('segmentation', media, 'stopped to prevent posssible duplication')
    print('segmentation', media, 'successful')
    if args.shazam: 
        shazaming(args.outdir, media, args.shazam_coverart, threads = args.shazam_multithread)
    if args.cleanup: os.remove(media)
    import sys
    sys.exit(0)
