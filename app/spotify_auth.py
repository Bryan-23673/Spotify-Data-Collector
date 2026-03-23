from spotipy import Spotify
from spotipy import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from dotenv import load_dotenv
from app.cache_handler import DBCacherHandler
import os

load_dotenv()

SCOPES = [
    "user-read-playback-state",  # lets app read user's current playback state
    "user-read-currently-playing",  # lets app see what song is playing right now
    "playlist-read-private",  # lets app read user's private playlists
    "user-top-read",  # lets app see user's top artists/tracks
    "user-read-recently-played",  # lets app see user's recently played tracks
    "user-read-email",  # lets app read user's email (for identification)
]

class SpotifyUser():
    def __init__(self, user_id: int | None = None):
        self.user_id = user_id

    # This object is used to request authorization from the user
    # Returns the required tokens
    # Can only give you certain data
    def get_oauth(self) -> SpotifyOAuth:
        oauth = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope=" ".join(SCOPES),
            show_dialog=True,
            open_browser=True,
            cache_handler=DBCacherHandler(self.user_id) if self.user_id else MemoryCacheHandler()
        )
        return oauth

    # This creates a full spotify client
    # Returns the spotify client
    # Lets you get any data you want
    def full_sp_client(self) -> Spotify:
        oauth = self.get_oauth()
        client = Spotify(oauth_manager=oauth)
        return client