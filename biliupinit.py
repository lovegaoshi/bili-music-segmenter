import subprocess
import tarfile
import glob
import os
import requests

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument(
        '--system', type=str, default=r'x86_64-linux-musl.tar.xz',
    )
    args = parser.parse_args()

    req = requests.get('https://api.github.com/repositories/437055168/releases/latest').json()
    targeted_download = list(filter(lambda x: args.system in x['name'], req['assets']))[0]
    subprocess.call(['wget', targeted_download['browser_download_url']])
    biliup_tar_path = glob.glob('biliupR*')[0]
    tarfile.open(biliup_tar_path).extractall()
    os.remove(biliup_tar_path)
    for file in glob.glob('biliupR*/*'):
        os.rename(file, os.path.join('/bin', os.path.basename(file)))
