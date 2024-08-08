from subprocess import Popen, PIPE, check_output
import os
import glob
import logging
import tempfile
import time
import uuid


COOKIES_LOCATION = ['--cookies', 'ytdlp_cookies.txt']

#fuzzy match! 
def ytbdl(
    url: str, soundonly: str = '-f bestaudio',
    outdir: str = tempfile.gettempdir(),
    aria: int = None) -> str:
    r = ''# --restrict-filenames
    fname = None
    uid = uuid.uuid4()
    #./youtube-dl
    cmd = ['yt-dlp', url, '-o', os.path.join(
        outdir, f"[%(uploader)s] %(title)s %(upload_date)s.{uid}.%(ext)s")]
    cmd.extend(COOKIES_LOCATION)       
    if aria is not None: 
        cmd.append('--external-downloader')
        cmd.append('aria2c')
        cmd.append('--external-downloader-args')
        cmd.append('-x {} -s {} -k 1M'.format(str(aria), str(aria)))
    if len(soundonly.split(' ')) > 1:
        cmd.extend(soundonly.split(' '))
    logging.info(cmd)
    passed_download = False
    while not passed_download:
        passed_download = True
        with Popen(cmd, stdout=PIPE, 
                universal_newlines=True) as p:
            for line in p.stdout:
                logging.info(line)
                if '[download] Destination' in line:
                    fname = line[len('[download] Destination: '):-1]
                elif 'has already been downloaded' in line: 
                    fname = line[len('[download] ') : 
                    -len(' has already been downloaded') - 1]
                elif '[Merger]' in line: 
                    fname = line[len('[Merger] Merging formats into "'):-2]
                elif "error" in line.lower():
                    passed_download = False
            if not passed_download:
                time.sleep(10)
    if fname is None:
        raise Exception('no ytbdl resutls!')
    logging.info(['mathcing', fname])
    ext = fname[fname.rfind('.'):]
    ext = ext.split(' ')[0]
    downloaded_files = glob.glob(os.path.join(outdir, f'*{uid}*'))
    downloaded_files.sort(key=os.path.getctime)
    if len(downloaded_files) > 1:
        with open(os.path.join(outdir, 'merge.txt'), 'w', encoding='UTF-8') as f:
            for i in downloaded_files:
                f.write(f'file \'{i}\'\n')
        merged_path = os.path.join(outdir, fname.replace(str(uid), ''))
        ffmpeg_merge_cmd = [
            'ffmpeg',
            '-f', 'concat', '-safe', '0', '-i',
            os.path.join(outdir, 'merge.txt'), '-c', 'copy', '-y', merged_path]
        check_output(ffmpeg_merge_cmd)
        for i in downloaded_files:
            os.remove(i)
        return merged_path
    final_name = downloaded_files[0].replace(str(uid), '')
    os.rename(downloaded_files[0], final_name)
    return final_name

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(ytbdl('https://www.bilibili.com/video/BV11DY4ebE4B/?spm_id_from=333.337.search-card.all.click', aria=8))