import subprocess
import tarfile
import glob
import os


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ina music segment')
    parser.add_argument(
        '--system', type=str, default=r'x86_64-linux-musl\.tar\.xz',
    )
    args = parser.parse_args()
    subprocess.call(
        r'curl -s https://api.github.com/repositories/437055168/releases/latest \
    | grep "browser_download_url.*"' + args.system + \
    r'| cut -d : -f 2,3 | tr -d \"  | wget -qi -', shell=True)
    biliup_tar_path = glob.glob('biliupR*')[0]
    tarfile.open(biliup_tar_path).extractall()0
    os.remove(biliup_tar_path)
    for file in glob.glob('biliupR*/*'):
        os.rename(file, os.path.join('/bin', os.path.basename(file)))
