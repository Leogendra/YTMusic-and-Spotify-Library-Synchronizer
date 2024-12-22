# YTMusic and Spotify Library Synchronizer

**YTMusic and Spotify Library Synchronizer** is a tool that allows you to sync your liked songs between Spotify and YouTube Music. It supports synchronization in both directions and automatically checks for duplicates.

## Disclaimer
This project is based on the [ytmusicapi](https://ytmusicapi.readthedocs.io/) and [Spotify Web API](https://developer.spotify.com/documentation/web-api).  
Due to the independent nature of the APIs used, the search functionality may not always be accurate. As a result, some songs might not be found or added during synchronization.

## **Installation and setup**

1. Clone this repository

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

1. Obtain your Spotify API credentials by creating an application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).

1. In your application settings, add `http://localhost:5500/callback` to your Redirect URIs (Settings > Edit > Redirect URIs).

1. Set up the environment variables for Spotify by creating `.env` file in the root directory:
   ```env
   SPOTIFY_CLIENT_ID=Your_Client_ID
   SPOTIFY_CLIENT_SECRET=Your_Client_Secret
   ```
   
1. To setup the connection to your YTMusic account, first run the script `python main.py`, it will generate a `browser.json` file in the `tokens/` directory.

1. To obtain your Cookie and Authorization, go to `https://music.youtube.com/` and log in with your account. Then press `F12` to open the Developer Tools, go to the `Network` tab, and filter (at the top) with `/browse`. Refresh the page and look for the `browse?ctoken=` request, click on it, and go to the `Request headers` section, and copy your `Cookie` and `Authorization` values into the `browser.json` file.

1. Run the script `python main.py` again to connetc to your Spotify account.

1. An URL is generated. Open the URL in your browser, copy the code after `?code=`, and paste it into the terminal. This token is valid for 1 hour.

1. You are now ready to (finally) use the synchronizer!

---

## **Usage**

1. **Run the script:**
    ```bash
    python main.py
    ```

1. **Available options:**
    - Choose an option when prompted:
        - **1**: Sync Spotify likes to YTMusic library
        - **2**: Sync YTMusic library to Spotify likes
        - **3**: Sync in both directions.
    - Missing songs will be added to the target platform. It will first search for the song by title and artist, and after all songs are processed, you will be asked to confirm the changes. Press `enter` to confirm, or anything else to cancel.

    - Choose an option for retrieving the liked songs:
        - **1**: Retrieve songs from Spotify/YTMusic likes/library.
        - **3**: Retrieve songs from `add_to_spotify.txt`/`add_to_ytmusic.txt` files.

1. **Generated files:**
    - `data/titles_spotify.txt`: List of liked songs on Spotify.
    - `data/titles_ytmusic.txt`: List of songs in your YouTube Music library.
    - `data/add_to_spotify.txt`: List of songs to be added to Spotify.
    - `data/add_to_ytmusic.txt`: List of songs to be added to YouTube Music.
    - `data/not_found_*.txt`: List of songs not found on each platform.

---

## **Troubleshooting**
If you encounter the following error:
```
ytmusicapi.exceptions.YTMusicServerError: Server returned HTTP 401: Unauthorized.
You must be signed in to perform this operation.
```
Your YTMusic token must be invalid or expired. To fix this, update the `browser.json` file with the new `Cookie` and `Authorization` values.

---

## **Contributions**
Contributions are welcome! Feel free to open an issue or submit a pull request.