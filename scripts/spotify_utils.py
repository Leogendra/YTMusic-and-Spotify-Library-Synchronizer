from scripts.utils import clean_name, write_to_file
import urllib.parse
import requests
import base64
import time
import json

SCOPE = "user-library-read user-library-modify playlist-read-private"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"




class SpotifyManager:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token = None
        self.fetch_access_token()


    def get_auth_url(self, scopes):
        scopes = urllib.parse.quote(scopes)
        return f"https://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&scope={scopes}"


    def fetch_access_token(self):
        # open token_auth file and check expiration date
        try:
            with open("tokens/spotify_token.json", "r", encoding="utf-8") as file:
                token = json.load(file)
                if (token["validity"] > time.time()):
                    print("Spotify token is still valid.")
                    self.token = token["token"]
                    return
                
        except FileNotFoundError:
            # create auth file if it doesn't exist
            blank_token = {"token": None, "validity": 0}
            with open("tokens/spotify_token.json", "w", encoding="utf-8") as file:
                json.dump(blank_token, file)

        token_url = self.get_auth_url(SCOPE)
        print(token_url)
        code = input("code=")

        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code.strip(),
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(
            "https://accounts.spotify.com/api/token", headers=headers, data=data
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            token = {
                "token": self.token,
                "validity": time.time() + 3600,
            }
            with open("tokens/spotify_token.json", "w", encoding="utf-8") as file:
                json.dump(token, file)
        else:
            print(f"Error while fetching access token: {response.status_code}")
            self.token = None


    def get_liked_songs(self):
        url = "https://api.spotify.com/v1/me/tracks"
        headers = {"Authorization": f"Bearer {self.token}"}
        liked_songs = []

        while url:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                liked_songs.extend(data["items"])
                url = data.get("next")
            else:
                print(f"Error while fetching liked songs: {response.status_code}")
                break

        return liked_songs
    

    def get_music_to_add(self, spotify_songs, ytmusic_songs):
        """
        Returns a list of (tuples) songs to add to Spotify: (title, artist)
        """
        songs_to_add = []

        for trackYT in ytmusic_songs:
            titleYT = clean_name(trackYT["title"]).lower()
            artistYT = trackYT["artists"][0]["name"].lower()

            if ((titleYT, artistYT) not in songs_to_add):
                # Check if the song is already liked on YTMusic
                isNotLiked = True
                for trackSpotify in spotify_songs:
                    titleSpotify = clean_name(trackSpotify["track"]["name"]).lower()
                    artistSpotify = trackSpotify["track"]["artists"][0]["name"].lower()

                    if (titleSpotify == titleYT) and (artistSpotify == artistYT):
                        isNotLiked = False
                        break

                if isNotLiked:
                    songs_to_add.append((titleYT, artistYT))

        return songs_to_add
    

    def search_on_spotify(self, track_name, artist_name):
        query = f"track:{track_name} artist:{artist_name}"
        url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(query)}&type=track&limit=1"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                results = response.json().get("tracks", {}).get("items", [])
                if results:
                    return results[0]["id"]
                
        except Exception as e:
            print(f"Error while searching on Spotify: {e}")

        return None


    def like_songs_on_spotify(self, track_ids):
        url = f"https://api.spotify.com/v1/me/tracks"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"ids": track_ids})

        response = requests.put(url, headers=headers, data=data)
        if response.status_code == 200:
            print(f"{len(track_ids)} songs liked on Spotify.")
        else:
            print(f"Error while liking song on Spotify: {response.status_code}")
    

    def search_and_add(self, liked_songs):
        not_found = []
        found_songs = []

        for i, song in enumerate(liked_songs):
            trackName, artistName = song
            print(f"[Spotify] {i+1}/{len(liked_songs)}: {trackName} - {artistName}", end=" ")
            track_id = self.search_on_spotify(trackName, artistName)
            if track_id:
                print(f"{GREEN}Found!{RESET}")
                found_songs.append(track_id)
            else:
                print(f"{RED}Not found{RESET}")
                not_found.append(song)

        confirm = input("Enter to add to Spotify")
        if found_songs and (confirm == ""):
            for i in range(0, len(found_songs), 50):
                self.like_songs_on_spotify(found_songs[i:i+50])

        if not_found:
            write_to_file("data/not_found_spotify.txt", not_found)