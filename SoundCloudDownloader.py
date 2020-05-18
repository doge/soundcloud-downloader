import re
import utils
import eyed3
import requests
import exceptions
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse

API_V2 = "https://api-v2.soundcloud.com/"


class SoundCloudDownloader:
    ''' a soundcloud mp3 downloader '''
    def __init__(self, url, client_id=None):
        self.url = url
        self.sess = requests.Session()
        self.url_type = self.__url_parse(self.url)

        if not client_id:
            print("[*] client id not found")
            self.client_id = self.__get_client_id()
        else:
            print("[*] client id supplied")
            self.client_id = client_id

        self.data = self.__get_data().json()

    def __get_song_id(self):
        ''' navigates to the given song url and does a regex search for the song id '''
        html = self.sess.get(self.url).text

        if self.url_type == "set":
            id = re.search("soundcloud://playlists:(.*?)\"", html)
        elif self.url_type == "song":
            id = re.search("soundcloud://sounds:(.*?)\"", html)
        else:
            raise exceptions.InvalidSongID("The song id could not be found.")

        return id.group(1)

    def __url_parse(self, url):
        ''' returns "song" or "set" based on if the url is a song or a set '''
        parsed = urlparse(url)

        # check if the url is from soundcloud
        if parsed.netloc != "soundcloud.com":
            raise exceptions.InvalidURL("The url is not from SoundCloud.")

        # check if the url is a set or a song and return the result
        items = parsed.path.split("/")
        if len(items) == 3 and items[2] != "" and (items[2] != "sets" and items[0] == ''):
            return "song"
        elif len(items) == 4 and items[2] != "" and (items[2] == "sets" and items[0] == ''):
            return "set"
        else:
            raise exceptions.InvalidURL("The URL provided is not a song or a set.")

    def __get_client_id(self):
        ''' grab your soundcloud client id (api key) '''
        client_id = None

        print("[~] grabbing client id...")

        resp = self.sess.get("https://soundcloud.com/").text
        soup = BeautifulSoup(resp, "html.parser")
        scripts = soup.find_all("script", crossorigin=True)

        # go to each script on soundcloud and look for the client_id variable
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
        if self.url_type == "set":
            data = self.sess.get(API_V2 + "playlists/" + self.__get_song_id() + "?client_id=" + self.client_id)
        elif self.url_type == "song":
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

        print("[~] \"%s\" downloading..." % self.data['title'])

        # get and write song to disk
        try:
            song = self.__get_song_mp3(self.data)
            file_name = "./songs/" + utils.remove_forbidden_chars(self.data['title']) + ".mp3"
            self.__write_file(file_name, song)

            print("[*] \"%s\" downloaded\n" % self.data['title'])
        except Exception as e:
            print(e)
            print("[*] \"%s\" failed\n" % self.data['title'])

    def download_set(self):
        ''' downloads, saves, and tags a set '''
        file_path = "./songs/" + utils.remove_forbidden_chars(self.data['title'])

        # create the songs directory if it doesn't already exist
        Path("./songs").mkdir(parents=True, exist_ok=True)

        # create the sub folder for the set
        Path(file_path).mkdir(parents=True, exist_ok=True)

        for track in self.data['tracks']:
            mp3_path = file_path + "/" + utils.remove_forbidden_chars(track['title']) + ".mp3"

            print("[~] \"%s\" downloading..." % track['title'])
            try:
                # write and tag song
                self.__write_file(mp3_path, self.__get_song_mp3(track))

                print("[*] \"%s\" downloaded\n" % track['title'])
            except Exception as e:
                print(e)
                print("[*] \"%s\" failed\n" % self.data['title'])

    def download(self):
        if self.url_type == "set":
            self.download_set()
        elif self.url_type == "song":
            self.download_song()
