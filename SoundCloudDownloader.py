import re
import requests
import eyed3
from pathlib import Path
from bs4 import BeautifulSoup

API_V2 = "https://api-v2.soundcloud.com/"


class SoundCloudDownloader:
    ''' a soundcloud mp3 downloader '''
    def __init__(self, url, client_id=None):
        self.url = url
        self.sess = requests.Session()

        if not client_id:
            print("[*] client id not found")
            self.client_id = self.__get_client_id()
        else:
            print("[*] client id supplied")
            self.client_id = client_id

        self.data = self.__get_data().json()

    def __get_song_id(self):
        ''' navigates to the given song url and does a regex search for the song id '''
        try:
            html = self.sess.get(self.url).text

            if "sets" in self.url:
                id = re.search("soundcloud://playlists:(.*?)\"", html)
            else:
                id = re.search("soundcloud://sounds:(.*?)\"", html)
            return id.group(1)

        except KeyError:
            print("[*] the song id could not be found")

    def __get_client_id(self):
        ''' grab your soundcloud client id (api key) '''
        client_id = None

        print("[~] grabbing client id...")

        resp = self.sess.get("https://soundcloud.com/").text
        soup = BeautifulSoup(resp, "html.parser")
        scripts = soup.find_all("script", crossorigin=True)

        for script in scripts:
            if "src" in script.attrs:
                script_text = self.sess.get(script['src']).text
                if "?client_id=" in script_text:
                    client_id_search = re.search("\?client_id=(.*?)&", script_text)
                    client_id = str(client_id_search.group(1))

                    print("[*] client_id: %s\n" % client_id)

                    break

        return client_id

    def __get_data(self):
        ''' returns data from the soundcloud api '''
        if "sets" in self.url:
            data = self.sess.get(API_V2 + "playlists/" + self.__get_song_id() + "?client_id=" + self.client_id)
        else:
            data = self.sess.get(API_V2 + "tracks/" + self.__get_song_id() + "?client_id=" + self.client_id)
        return data

    def __get_song_mp3(self, data):
        ''' returns the mp3 given the json data '''
        resp = self.sess.get(data['media']['transcodings'][1]['url'] + "?client_id=" + self.client_id)
        return self.sess.get(resp.json()['url']).content

    def __tag_mp3(self, mp3_file, data):
        ''' tags a given mp3 given the data '''
        mp3 = eyed3.load(mp3_file)
        mp3.initTag()

        try:
            mp3.tag.artist = data['publisher_metadata']['artist']
        except KeyError:
            mp3.tag.artist = data['user']['username']

        mp3.tag.title = data['title']

        # set cover art
        image = self.sess.get(data['artwork_url'].replace('-large', '-t500x500')).content
        mp3.tag.images.set(3, image, 'image/jpeg')

        mp3.tag.save()

        return mp3_file

    def __write_file(self, file_name, data):
        ''' writes a file given the file name and the data '''
        with open(file_name, 'wb') as f:
            f.write(data)
        self.__tag_mp3(file_name, self.data)

    def download_song(self):
        ''' downloads, saves, and tags a single song '''

        # create the songs directory if it doesn't already exist
        Path("./songs").mkdir(parents=True, exist_ok=True)

        # get and write song to disk
        song = self.__get_song_mp3(self.data)
        file_name = "./songs/" + self.data['title'] + ".mp3"
        self.__write_file(file_name, song)

    def download_set(self):
        ''' downloads, saves, and tags a set '''
        file_path = "./songs/" + self.data['title']

        # create the songs directory if it doesn't already exist
        Path("./songs").mkdir(parents=True, exist_ok=True)

        # create the sub folder for the set
        Path(file_path).mkdir(parents=True, exist_ok=True)

        for track in self.data['tracks']:
            mp3_path = file_path + "/" + track['title'] + ".mp3"

            print("[~] \"%s\" downloading..." % track['title'])
            try:
                # write and tag song
                self.__write_file(mp3_path, self.__get_song_mp3(track))

                print("[*] \"%s\" downloaded\n" % track['title'])
            except Exception as e:
                print("[*] \"%s\" failed\n" % track['title'])
                print(e)

    def download(self):
        if "sets" in self.url:
            self.download_set()
        else:
            self.download_song()
