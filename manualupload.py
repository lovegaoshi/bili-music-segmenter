import json, subprocess, os, logging, re, glob, time

CONFIG_DIREC = './configs/biliWrapper.json'
KEYSTAMPS = json.load(open(CONFIG_DIREC, encoding='utf-8'))
logging.debug('loaded upload configs.')

def retry(times: int, timeout: int, exceptions: tuple):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logging.warning(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt + 1, times)
                    )
                    attempt += 1
                    if attempt == times: raise MaxRetryReached()
                    time.sleep(timeout)
            return func(*args, **kwargs)
        return newfn
    return decorator


@retry(times=35, timeout=60, exceptions=(Exception))
def cell_stdout(cmd, silent=False, encoding=None):
    logging.info(['calling', cmd, 'in terminal:'])
    with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          universal_newlines=True, encoding=encoding) as p:
        if not silent:
            try:
                for i in p.stdout:  # .decode("utf-8"):
                    logging.debug(i)
            except UnicodeDecodeError:
                # 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷
                logging.warning('decode failed! but at least you have this eror message...')
        p.wait()
    if p.returncode != 0:
        raise Exception()
    return p.returncode

def generate_upload_command(path):
    route='qn'
    media_basename = os.path.basename(path)
    ripped_from = re.compile(r'\[(.+)\].+').match(media_basename).group(1)
    try:
        source = KEYSTAMPS[ripped_from][0]
    except KeyError:
        raise KeyError('cant determine source url for this repost')

    try:
        description = KEYSTAMPS[ripped_from][1]
    except IndexError:
        description = '关注{}：{}'.format(
            ripped_from,
            source,)

    try:
        tags = KEYSTAMPS[ripped_from][2]
    except IndexError:
        tags = [ripped_from]
    except KeyError:
        tags = [ripped_from]

    title = media_basename[:media_basename.rfind('.')][:60].replace(ripped_from, tags[0]).replace('【直播回放】','')
    globbed = glob.glob(os.path.join(glob.escape(path), f'*.flv')) # WTF?
    # print(globbed)
    for i in globbed:
        os.rename(i, i.replace(f'{media_basename}_', ''))
    globbed = glob.glob(os.path.join(glob.escape(path), f'*.flv')) # WTF?
    globbed = sorted(globbed)
    globbed_episode_limit = []
    episode_limit = 180
    for i in range(len(globbed) // episode_limit + 1):
        if globbed[i] == media_basename:
            continue
        globbed_episode_limit.append(
            globbed[i * episode_limit: (i + 1) * episode_limit])

    for i in range(len(globbed_episode_limit)):
        if i > 0:
            episode_limit_prefix = '_' + chr(97 + i)
        else:
            episode_limit_prefix = ''
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
        cmd.append('--title=[歌切]{}'.format(title[:60] + episode_limit_prefix))
        cmd.append('--source={}'.format(source))
        cmd.append('-l=' + route)
        logging.debug(cmd)
        return cmd

if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument('--media', type=str, nargs='+', help='file path or weblink')
    
    args = parser.parse_args()
    if args.media is None: 
        args.media = glob.glob('./inaupload/*')
    for media in args.media:
        logging.info(media)
        print(media)
        c = cell_stdout(generate_upload_command(media))
        logging.info(c)
        print('code: ', c)
