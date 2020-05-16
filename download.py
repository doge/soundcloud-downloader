from SoundCloudDownloader import SoundCloudDownloader
import argparse

parser = argparse.ArgumentParser(description="download soundcloud songs")
parser.add_argument('-s', action="store", default=None, help="url to a soundcloud song", required=True)
args = parser.parse_args()


sc = SoundCloudDownloader(args.s)

print("[~] attempting download of %s" % args.s)
try:
    sc.download_song()
    print("[*] download succeeded")
except Exception as e:
    print("[*] download failed")
    print(e)


