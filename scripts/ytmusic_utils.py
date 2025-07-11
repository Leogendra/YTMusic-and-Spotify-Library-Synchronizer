from scripts.utils import write_to_file, remove_parentesis, clean_name, are_strings_similar
from ytmusicapi import YTMusic
import json
import re

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"




class YTMusicManager:
    def __init__(self, auth_file="tokens/browser.json"):
        self.ytmusic = None
        self.get_browser_auth(auth_file)


    def get_browser_auth(self, auth_file):
        try:
            with open(auth_file, "r", encoding="utf-8") as file:
                browser_token = json.load(file)
                if (browser_token["Cookie"] != "YOUR_COOKIE") and (browser_token["Authorization"] != ""):
                    print("YTMusic token is still valid.")
                    self.ytmusic = YTMusic(auth_file)
                    return

        except FileNotFoundError:
            default_browser_settings = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/json",
                "X-Goog-AuthUser": "0",
                "x-origin": "https://music.youtube.com",
                "Authorization": "YOUR_AUTHORIZATION",
                "Cookie" : "YOUR_COOKIE"
            }
            with open(auth_file, "w", encoding="utf-8") as file:
                json.dump(default_browser_settings, file, indent=4)

        print(f"Please fill in the {auth_file} file with your cookie.")
        exit(0)


    def get_library_songs(self, limit=None):
        cleaned_songs = []
        seen = set()
        raw_library = self.ytmusic.get_library_songs(limit=limit)

        for song in raw_library:
            title = song["title"]
            artists = [artist["name"] for artist in song["artists"]]
            key = (title, tuple(artists))

            if (key not in seen):
                seen.add(key)
                cleaned_songs.append({
                    "name": title,
                    "artists": artists,
                })

        return cleaned_songs
    

    def get_music_to_add(self, ytmusic_songs, spotify_songs):
        """
        Returns a list of (tuples) songs to add to YTMusic: (title, artist)
        """
        all_songs = []
        songs_to_add = []

        for trackSpotify in spotify_songs:
            titleSpotify = clean_name(remove_parentesis(trackSpotify["name"]).lower())
            artists_spotify = [clean_name(artist.lower()) for artist in trackSpotify["artists"]]
            all_songs.append((titleSpotify, ", ".join(artists_spotify)))

            if ((titleSpotify, artists_spotify) not in songs_to_add):
                # Check if the song is already liked on YTMusic
                isNotLiked = True
                for trackYT in ytmusic_songs:
                    titleYT = clean_name(remove_parentesis(trackYT["name"]).lower())
                    artists_YT = [clean_name(artist.lower()) for artist in trackYT["artists"]]

                    if are_strings_similar(f"{titleSpotify} - {' '.join(artists_spotify)}".lower(), f"{titleYT} - {' '.join(artists_YT)}".lower()):
                        isNotLiked = False
                        break

                if isNotLiked:
                    songs_to_add.append((titleSpotify, artists_spotify))

        write_to_file("data/tracks_spotify.txt", all_songs)

        return songs_to_add


    def search_and_add(self, liked_songs):
        feedback_tokens = []
        not_found = []

        for i, song in enumerate(liked_songs):
            trackName, track_artists = song
            print(f"[YTMusic] {i+1}/{len(liked_songs)}: {trackName} - {", ".join(track_artists)}", end=" ")

            query = f"{trackName} {" ".join(track_artists)}"
            search_results = self.ytmusic.search(query, filter="songs")
            if search_results:
                try:
                    first_result = search_results[0]
                    feedback_tokens.append(first_result["feedbackTokens"]["add"])
                    print(f"{GREEN}Found!{RESET}")
                except:
                    not_found.append(song)
                    print(f"{RED}Not found{RESET}")
            else:
                not_found.append(song)
                print(f"{RED}Not found{RESET}")

        confirm = input("Press enter to add to YTMusic: ")
        if feedback_tokens and (confirm == ""):
            self.ytmusic.edit_song_library_status(feedbackTokens=feedback_tokens)
            print(f"{len(feedback_tokens)} songs added to YTMusic.")

        if not_found:
            write_to_file("data/not_found_ytmusic.txt", not_found)