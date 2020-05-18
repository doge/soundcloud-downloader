from SoundCloudDownloader import SoundCloudDownloader
import argparse


def main():
    parser = argparse.ArgumentParser(description="download soundcloud songs")
    parser.add_argument('-s', action="store", default=None, help="url to a soundcloud song or set", required=True)
    parser.add_argument('-cid', action="store", default=None, help="soundcloud api key", required=False)
    args = parser.parse_args()

    sc = SoundCloudDownloader(args.s, args.cid)
    sc.download()


if __name__ == "__main__":
    main()
