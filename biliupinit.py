import subprocess
import tarfile
import glob
import os

subprocess.call(
    r'curl -s https://api.github.com/repositories/437055168/releases/latest \
| grep "browser_download_url.*x86_64-linux-musl\.tar\.xz" \
| cut -d : -f 2,3 | tr -d \"  | wget -qi -', shell=True)
biliup_tar_path = glob.glob('biliupR*')[0]
tarfile.open(biliup_tar_path).extractall()
os.remove(biliup_tar_path)
for file in glob.glob('biliupR*/*'):
    os.rename(file, os.path.join('/bin', os.path.basename(file)))
