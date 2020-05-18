from SoundCloudDownloader import SoundCloudDownloader
import argparse

parser = argparse.ArgumentParser(description="download soundcloud songs")
parser.add_argument('-s', action="store", default=None, help="url to a soundcloud song", required=True)
parser.add_argument('-cid', action="store", default=None, help="your soundcloud api key", required=False)
args = parser.parse_args()

sc = SoundCloudDownloader(args.s, args.cid)

print("[~] attempting download of %s\n" % args.s)

try:
    sc.download()
    print("[*] download succeeded")
except Exception as e:
    print("[*] download failed")
    print(e)


