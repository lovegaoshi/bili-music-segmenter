# Load the API
from inaSpeechSegmenter import Segmenter  # noqa: E402
import os
import glob
from threading import Thread
import gc
import logging
import tempfile

from noxsegutils.shazam import shazaming
from noxsegutils.util import get_segment_process_length_array, ffmpeg
from noxsegutils.timestamp import fix_missing_stamps, sec2timestamp
from noxsegutils.download import ytbdl
from inaConstant import load_config, save_config

# 媒体流最大时长处理（秒）；1G内存的进程推荐用10分钟/600秒，16G可以支持5小时，6GB VRAM可以支持5小时左右。
SEGMENT_THRES = 800
# 识歌分段最小阈值（秒），调大了会漏 调小了会多杂谈
EXTRACT_SEG_THRES = 60
# 最终识歌分段最小阈值（秒），调大了漏TV size 调小了多杂谈
EXTRACT_SEG_THRES_FINAL = 80
# 识歌分段连接的阈值（秒），调大了会两首歌分不开 调小了会碎
EXTRACT_SEG_CONNECT = 5
# 大了会碎 小了会两首歌分不开
ENERGY_RATIO = 0.03
# 8GB VRAM 推荐 256
BATCH_SIZE = 32

SAVE_YAML_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'save.yaml')

class TimestampMismatch(Exception):
    pass

# select a media to analyse
# any media supported by ffmpeg may be used (video, audio, urls)
def segment(
    media, batch_size = BATCH_SIZE, energy_ratio = ENERGY_RATIO,
    start_sec: int = None, stop_sec: int = None):
    segmenter = Segmenter(
        vad_engine='sm',
        detect_gender=False,
        energy_ratio=energy_ratio,
        batch_size=batch_size)
    segmentation = segmenter(media, start_sec=start_sec, stop_sec=stop_sec)
    return segmentation


def segment_wrapper(
    media: str, batch_size: int = BATCH_SIZE,
    energy_ratio: float = ENERGY_RATIO, segment_length_thres:int = 0):
    ''''''
    result = []
    for i in get_segment_process_length_array(media, segment_length_thres):
        logging.info([
            'segmenting', media, 'from',
            sec2timestamp(i[0]), 'to', sec2timestamp(i[1])])
        result += segment(
            media, batch_size, energy_ratio,
            start_sec=i[0], stop_sec=i[1])
        gc.collect()
        tf.keras.backend.clear_session()
    return result

def extract_music(
    segmentation, segment_thres = EXTRACT_SEG_THRES,
    segment_thres_final = EXTRACT_SEG_THRES_FINAL,
    segment_connect = EXTRACT_SEG_CONNECT, start_padding = 1, end_padding = 4):
    r = []
    #bridges noEnergy segments that are likely fragmented
    for i in range(len(segmentation)-2, 0, -1):
        if segmentation[i][0] == 'noEnergy' and \
            segmentation[i][2] - segmentation[i][1] < 4 and \
        segmentation[i-1][0] == segmentation[i+1][0]:
            segmentation[i-1] = (
                segmentation[i-1][0],
                segmentation[i-1][1],
                segmentation[i+1][2])
    for i in segmentation: 
        if i[0] == 'music' and i[2]-i[1] > segment_thres:
            r.append(['',i[1] - start_padding, i[2] + end_padding])    
    for i in range(len(r)-1, 0, -1):
        if r[i][1] - r[i-1][2] < segment_connect:
            r[i-1][2] = r[i][2]
            r[i][1] = r[i][2] + 1    
    rf = []
    for i in r:
        if i[1] < 5:
            continue
        if i[2]-i[1] > segment_thres_final:
            rf.append(i)
    return [['{}:{}:{}'.format(str(int(x[1]//3600)), 
                               str(int(x[1] % 3600 //60)), 
                               str(int(x[1] % 60)).zfill(2)), 
             '{}:{}:{}'.format(str(int(x[2]//3600)), 
                               str(int(x[2]  % 3600  //60)), 
                               str(int(x[2] % 60)).zfill(2))] for x in rf]


def extract_mah_stuff(
    media, segmented_stamps, outdir = None, rev = False,
    delimited = '/', timestamps = [], soundonly = True):
    nameswitch = False
    timestamps_ext = segmented_stamps
    try:
        if len(timestamps) > 0:
            raise FileNotFoundError()
        for i in open(r"D:\tmp\ytd\timstamp.ini", 'r', encoding='UTF-8'):
            for k in [
                ['\n',''],['」', ''],['~「',' '],['「', ' '],
                ['『', ' '],['』', ' '],['　', ' '],['	', ' '],['\'',''],]:
                i = i.replace(k[0], k[1])
            if ' （' in i:
                i = i[:i.find(' （')]
            if ':' in i:
                timestamps.append([i[:i.find(' ')], i[i.find(' ')+1:]])
                #timestamps[-1][1] = timestamps[-1][1][1:]
                if delimited in timestamps[-1][1]:
                    timestamps[-1][1] = [
                        timestamps[-1][1][:timestamps[-1][1].find('/')],
                        timestamps[-1][1][timestamps[-1][1].find('/')+1:]]
                    if rev:
                        timestamps[-1][1].reverse()
                    timestamps[-1][1] = ' by '.join(timestamps[-1][1])
                #timestamps[-1][1].replace('/', ' by ')
                #timestamps[-1][1] = ' by '.join(timestamps[-1][1].split('/'))
                #timestamps[-1][1] = timestamps[-1][1].replace('-', 'by')
                while timestamps[-1][1][0] == ' ':
                    timestamps[-1][1] = timestamps[-1][1][1:]
                while timestamps[-1][1][-1] == ' ':
                    timestamps[-1][1] = timestamps[-1][1][:-1]
        #        nameswitch = True
            elif nameswitch:
                nameswitch = False
                timestamps[-1].append(i)
        if len(timestamps) > 0:# and len(timestamps) != len(timestamps_ext): 
            logging.info('checking timestamp correspondence and removing\
                mismatched ones (come on, are you really gonna do this manually)')
            timestamps = fix_missing_stamps(timestamps, timestamps_ext)
            timestamps_ext = fix_missing_stamps(timestamps_ext, timestamps)
            if len(timestamps) != len(timestamps_ext): 
                raise TimestampMismatch(
                    'check timestamp assist', timestamps, timestamps_ext)
        with open(r"D:\tmp\ytd\timstamp.ini", 'w') as f:  # noqa: F841
            pass
    except FileNotFoundError:
        pass
    if len(timestamps) > 0:
        logging.info([
            'timestamp assist', 
            [[timestamps[x][0],
            timestamps_ext[x][1], timestamps[x][1], ] for x in range(len(timestamps))]])
    else:
        logging.info([
            'extracted timestamps',
            ['{} - {}'.format(x[0], x[1]) for x in timestamps_ext]])
    try:
        for count, x in enumerate(timestamps_ext):
            logging.info(f'{str(count).zfill(2)}: {x[0]} - {x[1]}')
    except Exception:
        pass
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
                '-ss',
                timestamps[i][0],
                '-to',
                timestamps_ext[i][1],
                '-i',
                file,
                '-reset_timestamps', '1',
                ] + encoding + [                
                os.path.join(
                    oud, filename + f'_{str(i).zfill(2)}_{prefix}' + fileext),

            ] + encoding)
        except Exception:
            prefix = str(i).zfill(2)
            cmds.append([
                'ffmpeg',
                '-ss',
                timestamps_ext[i][0],
                '-to',
                timestamps_ext[i][1],
                '-i',
                "{}".format(file),
            ] + encoding + [
                "{}".format(os.path.join(oud, filename + '_' + prefix + fileext)),
            ])
    k = [Thread(target=ffmpeg, args=(x,)) for x in cmds]
    for i in k: 
        i.start()
        i.join()
    #k[-1].join()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument('--media', type=str, help = 'file path or weblink')
    parser.add_argument(
        '--outdir', type=str, default = tempfile.gettempdir(),
        help = 'directory media will be downloaded into (if url) and extracted into;\
             if docker, use as the mounted folder! and make sure -u is you!')
    parser.add_argument(
        '--shazam', action='store_true', default = False,
        help = 'shazam the extracted files')
    parser.add_argument(
        '--shazam_coverart', type=str, default = '',
        help = 'save shazam cover art too')
    parser.add_argument(
        '--aria', type=int, default = None,
        help = 'use aria, specifying the number of threads')
    parser.add_argument(
        '--shazam_multithread', type=int, default = 1,
        help = 'use multithreaded shazam')
    parser.add_argument(
        '--soundonly', type=str, default = r'-f bestaudio',
        help = 'specify an empty string to extract both video and audio')
    parser.add_argument(
        '--seg_connect', type=int, default = 5,
        help = 'max seconds for 2 music segments to be considered \
            the same (takes care of random miss-detection/small rap segments)')
    parser.add_argument(
        '--cleanup', action='store_true', default = False,
        help = 'delete the original media file once completed.')
    parser.add_argument(
        '--max_segment_length',
        type=int,
        default=SEGMENT_THRES,
        help='for computers with limited RAM (eg a 5 hrs stream \
            requires ~6GB VRAM), set this to process streams in \
                this speficied segments to avoid ram overflow. in seconds.')
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s %(levelname)-8s %(message)s',
        handlers=[
            logging.FileHandler('./inaseg_inst.log'),
            logging.StreamHandler()
        ])
    args = parser.parse_args()
    #media = ytbdl('')
    if args.media is not None:
        media = args.media
    else:
        raise Exception('no media')
    if 'https:' in media:
        media = ytbdl(
            media, soundonly = args.soundonly,
            aria = args.aria, outdir = args.outdir)
    #media = r"D:\tmp\ytd\[莉犬くん【すとぷり】] 【激レア歌枠】とんでもないお知らせがあります。。。【莉犬】 20220607.webm"
    if len(glob.glob(os.path.join(
        args.outdir, f'*{os.path.splitext(os.path.basename(media))[0][1:]}_*'))) == 0:
        import tensorflow as tf
        gpus = tf.config.experimental.list_physical_devices('GPU')
        logging.info(gpus)
        tf.get_logger().setLevel(logging.WARNING)
        if False and gpus:
        # Restrict TensorFlow to only allocate 1GB of memory on the first GPU: noope.
            try:
                tf.config.experimental.set_virtual_device_configuration(
                    gpus[0],
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=5424)])
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                logging.info([len(gpus), "Physical GPUs,",
                len(logical_gpus), "Logical GPUs"])
                os.environ["TF_GPU_ALLOCATOR"]="cuda_malloc_async"
            except RuntimeError as e:
                # Virtual devices must be set before GPUs have been initialized
                logging.error(e)
                raise 
        try:
            timestamps = []
            #timestamps = mus1ca_timestamp(media[:media.rfind('.')] + '.description')
            saved_timestamp = extract_music(segment_wrapper(
                media, segment_length_thres=args.max_segment_length),
                segment_connect = args.seg_connect)
            extract_mah_stuff(
                media, segmented_stamps=saved_timestamp,
                outdir=args.outdir, rev=False,
                timestamps=timestamps,
                soundonly=(args.soundonly != ''))
            saved_timestamp = None
        except TimestampMismatch:
            raise
    else:
        logging.warning((
            'segmentation', media, 'stopped to prevent posssible duplication'))
    logging.info(['segmentation', media, 'successful'])
    if args.cleanup and os.path.isfile(media):
        os.remove(media)
    if args.shazam: 
        shazaming(
            args.outdir, media, args.shazam_coverart,
            threads = args.shazam_multithread)
    import sys
    sys.exit(0)
