from scripts.utils import create_folder, write_to_file
from scripts.spotify_utils import SpotifyManager
from scripts.ytmusic_utils import YTMusicManager
from dotenv import load_dotenv
import os

load_dotenv()
UNDERLINED = "\033[4m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"




if __name__ == "__main__":

    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = "http://localhost:5500/callback"

    create_folder("data/")
    create_folder("tokens/")

    spotify = SpotifyManager(client_id, client_secret, redirect_uri)
    ytmusic = YTMusicManager()
    
    toYTMusic = False
    toSpotify = False

    print("\nChoose an option:")
    print("1. Synchronise Spotify -> YTMusic")
    print("2. Synchronise YTMusic -> Spotify")
    print("3. Synchronise both")
    
    choice = input("Enter your choice: ")
    if (choice not in ["1", "2", "3"]):
        print("Invalid choice.")
        exit(0)

    print()
    if (choice in ["1", "3"]):
        toYTMusic = True

    if (choice in ["2", "3"]):
        toSpotify = True

    print("\nChoose an option:")
    print("1. Retrieve from your librairies/likes")
    print(f"2. Use the {UNDERLINED}add_to_spotify.txt{RESET} and {UNDERLINED}add_to_ytmusic.txt{RESET} files")
    
    choice = input("Enter your choice: ")
    if (choice not in ["1", "2"]):
        print("Invalid choice.")
        exit(0)

    print()
    if (choice == "1"):
        print("Fetching library songs from YTMusic...")
        ytmusic_library_songs = ytmusic.get_library_songs()

        print("Fetching liked songs from Spotify...")
        spotify_liked_songs = spotify.get_liked_songs()

    if (choice == "2"):
        print(f"Reading from {UNDERLINED}add_to_ytmusic.txt{RESET} and {UNDERLINED}add_to_spotify.txt{RESET} files...")
        ytmusic_library_songs = []
        spotify_liked_songs = []

        with open("data/add_to_ytmusic.txt", "r", encoding="utf-8") as file:
            for line in file:
                title, artist = line.strip().split(" - ")
                ytmusic_library_songs.append((title, artist))

        with open("data/add_to_spotify.txt", "r", encoding="utf-8") as file:
            for line in file:
                title, artist = line.strip().split(" - ")
                spotify_liked_songs.append((title, artist))


    ytmusic_to_add = ytmusic.get_music_to_add(ytmusic_library_songs, spotify_liked_songs)
    spotify_to_add = spotify.get_music_to_add(spotify_liked_songs, ytmusic_library_songs)
    
    if (toYTMusic):
        if ytmusic_to_add:
            print(f"Adding {len(ytmusic_to_add)} songs to YTMusic...")
            write_to_file("data/add_to_ytmusic.txt", ytmusic_to_add)
            ytmusic.search_and_add(ytmusic_to_add)

    if (toSpotify):
        if spotify_to_add:
            print(f"Adding {len(spotify_to_add)} songs to Spotify...")
            write_to_file("data/add_to_spotify.txt", spotify_to_add)
            spotify.search_and_add(spotify_to_add)