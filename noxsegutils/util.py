
import os
import subprocess
import tempfile
from threading import Thread
import logging
from datetime import timedelta
import math

from noxsegutils.timestamp import timestamp2sec

def get_length(filename):
    if not filename:
        return "0"
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            '-sexagesimal',
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return str(result.stdout)[2:-5] #float() without -sexagesimal

def get_length_using_copied_audio(filename: str):
    temp_audio_file = os.path.join(
            tempfile.gettempdir(),
            'get_length_acodec_temp.mp4'
        )
    try:
        os.remove(temp_audio_file)
    except OSError:
        pass
    subprocess.call([
        'ffmpeg',
        '-i',
        filename,
        '-reset_timestamps',
        '1',
        '-vn',
        '-acodec',
        'copy',
        temp_audio_file,
        ])
    result = get_length(temp_audio_file)
    os.remove(temp_audio_file)
    return result

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
    for i in k:
        i.start()
    k[-1].join()
    os.remove(filename)

def ffmpeg(cmd, wait = True):
    logging.info(('calling', cmd, 'in terminal:'))
    process = subprocess.Popen(cmd)
    if wait:
        process.wait()
    return 1


def sec2timestamp(sec):
    try:
        return str(timedelta(seconds=sec))
    except Exception:
        return "infinity"

def get_segment_process_length_array(filename: str, thres: int = 0):
    if not thres:
        return [[None, None]]
    try:
        file_length = timestamp2sec(get_length(filename))
    except Exception:
        file_length = 0
    if file_length == 0:
        logging.warning(f'ffprobe on {filename} length failed.\
            now extracting the audio and probing the resulting audio file.')
        file_length = timestamp2sec(get_length_using_copied_audio(filename))
        # something is wrong; happens with DDrecorder's raw streams.
        # i just copy the audio segment and probe that one instead.
    logging.info((filename, 'total seconds', sec2timestamp(file_length)))
    if thres > file_length:
        return [[None, None]]
    logging.debug((f'filelength {str(file_length)} is \
        larger than thres {str(thres)}, triggering a segmentation.'))
    result = [[ x * thres, (x + 1) * thres ] for x in \
        range(math.ceil(file_length / thres))]
    result[0][0] = None
    result[-1][1] = None
    return result