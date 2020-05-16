import re
import requests
import eyed3
from pathlib import Path

API_V2 = "https://api-v2.soundcloud.com/tracks/"
CLIENT_ID = "your-client-id"


class SoundCloudDownloader:
    ''' a soundcloud mp3 downloader '''
    def __init__(self, url):
        self.url = url
        self.data = self.__get_song_data().json()

    def __scrape_id(self):
        '''
            navigates to the given song url and does a regex search for the song id
         '''
        try:
            html = requests.get(self.url).text
            id = re.findall('soundcloud://sounds:(.*?)"', html)[0]
            return id
        except KeyError:
            print("[*] the song id could not be found")

    def __get_song_data(self):
        ''' returns data from the soundcloud api '''
        data = requests.get(API_V2 + self.__scrape_id() + "?client_id=" + CLIENT_ID)
        return data

    def __get_song_mp3(self):
        ''' returns the songs url '''
        url_json = requests.get(self.data['media']['transcodings'][1]['url'] + "?client_id=" + CLIENT_ID)
        return url_json.json()['url']

    def download_song(self):
        ''' downloads, saves, and tags a single song '''

        # create the songs directory if it doesn't already exist
        Path("./songs").mkdir(parents=True, exist_ok=True)

        # get and write song to disk
        song = requests.get(self.__get_song_mp3()).content
        # self.data['user']['username'] + ' - '
        file_name = "./songs/" + self.data['title'] + '.mp3'
        with open(file_name, 'wb') as f:
            f.write(song)

        # tagging!
        mp3 = eyed3.load(file_name)
        mp3.initTag()

        try:
            mp3.tag.artist = self.data['publisher_metadata']['artist']
        except KeyError:
            mp3.tag.artist = self.data['user']['username']

        mp3.tag.title = self.data['title']

        # set cover art
        image = requests.get(self.data['artwork_url'].replace('-large', '-t500x500')).content
        mp3.tag.images.set(3, image, 'image/jpeg')

        mp3.tag.save()
