import subprocess, shlex, time, logging
# sudo docker exec  ipynb-inasegcelery-1 python /inaseg/addInaCelery.py --docker --media 
# sudo docker exec bili-music-segmenter-inasegcelery-1 python /inaseg/addInaCelery.py --force --media https://www.bilibili.com/video/BV16S411w7dY/?spm_id_from=333.999.0.0

def scheduled_add_task(media, forced=False):
    from biliupCelery import add
    while True:
        c = subprocess.check_output(shlex.split('tail -n 1 inaseg_inst.log'))
        if 'successful' not in str(c) and not forced:
            logging.info('detected inaseg log did not end with successful. now waiting for 30min.')
            time.sleep(1800)
        else:
            logging.info(f'added {media}.')
            add.delay(media)
            time.sleep(1899)
            return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument('--media', type=str, nargs='+', help='file path or weblink')
    parser.add_argument('--force', action='store_true', default = False, help='run in docker')
    parser.add_argument('--docker', action='store_true', default = False, help='run in docker')
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    if args.docker:
        for media in args.media:
            while True:
                if args.force:
                    break
                last_output = str(subprocess.check_output(shlex.split('tail -n 1 inaseg_inst.log')))
                if 'successful' in last_output:
                    break
                logging.warning('system is busy that inaseg_inst.log did not end with success. now wait for 30min.')
                time.sleep(1800)
            subprocess.check_output(['sudo','docker', 'exec', 'bili-music-segmenter-inasegcelery-1', 'python', '/inaseg/addInaCelery.py', '--media', media])
            logging.info(f'{media} is added to inasegCelery queue.')
            time.sleep(1800)
    else:
        for media in args.media:
            scheduled_add_task(media, args.force)
