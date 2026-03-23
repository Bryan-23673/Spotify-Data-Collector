from spotipy import Spotify
from app.spotify_auth import SpotifyUser
import webbrowser

if __name__ == "__main__":
    user = SpotifyUser()
    oauth = user.get_oauth()
    url = oauth.get_authorize_url()
    webbrowser.open_new_tab(url=url)