from app.database import get_connection
from datetime import datetime, timezone
from app.spotify_auth import *
import smtplib, ssl
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

def send_error_email(error_msg : str):
    sender = os.getenv("EMAIL")
    receiver = os.getenv("EMAIL")
    password = os.getenv("EMAIL_APP_PASSWORD")
    
    msg = MIMEText(error_msg)
    msg["Subject"] = "Spotify Schedule Error"
    msg["From"] = sender
    msg["To"] = receiver

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

# This file will run as a python to script
# It will actively store songs for each user into the database

def _parse_played_at(played_at_str: str) -> datetime:
    """Parse Spotify's played_at string into a UTC-aware datetime."""
    try:
        dt = datetime.strptime(played_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        dt = datetime.strptime(played_at_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.replace(tzinfo=timezone.utc)

# Execute query that will store songs
def store_songs(user_id: int = None) -> dict:
    """Sync recently played songs for all users into the database."""
    conn = get_connection()
    users = [{"user_id": user_id}] if user_id else get_users(conn)
    songs_stored = 0
    users_synced = 0

    for user in users:
        # DO NOT SEPARATE — client must be created together
        spotify_user = SpotifyUser(user["user_id"])
        full_client = spotify_user.full_sp_client()

        most_recent = get_most_recent_song_time(conn, user["user_id"])

        after_ms = int(most_recent.timestamp() * 1000) if most_recent else None
        songs = full_client.current_user_recently_played(limit=50, after=after_ms)
        user_songs_stored = 0

        for item in songs["items"]:
            played_at = _parse_played_at(item["played_at"])

            if most_recent and played_at <= most_recent:
                continue

            track = item["track"]
            artist = track["artists"][0]
            album = track["album"]

            release_date = album["release_date"]
            precision = album.get("release_date_precision", "day")
            if precision == "year":
                release_date = f"{release_date}-01-01"
            elif precision == "month":
                release_date = f"{release_date}-01"

            insert_artists(
                conn,
                spotify_artist_id=artist["id"],
                spotify_artist_url=artist["external_urls"]["spotify"],
                artist_name=artist["name"],
            )
            insert_albums(
                conn,
                spotify_album_id=album["id"],
                spotify_album_url=album["external_urls"]["spotify"],
                album_name=album["name"],
                total_tracks=album["total_tracks"],
                release_date=release_date,
                spotify_artist_id=artist["id"],
            )
            insert_tracks(
                conn,
                spotify_track_id=track["id"],
                spotify_track_url=track["external_urls"]["spotify"],
                track_name=track["name"],
                album_name=album["name"],
                spotify_artist_id=artist["id"],
                spotify_album_id=album["id"],
                release_date=release_date,
                duration_ms=int(track["duration_ms"]),
                popularity=track["popularity"],
                explicit=track["explicit"],
            )
            insert_recently_played(conn, user["user_id"], track["id"], played_at)
            user_songs_stored += 1

        if user_songs_stored > 0:
            users_synced += 1
            songs_stored += user_songs_stored
            conn.commit()

    conn.close()
    return {"songs_stored": songs_stored, "users_synced": users_synced}

def get_most_recent_song_time(conn, user_id: int):
    cursor = conn.cursor()
    query = """
    SELECT played_at FROM listened_history
    WHERE user_id = %s
    ORDER BY played_at DESC
    LIMIT 1
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    return result["played_at"] if result else None

def get_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    return cursor.fetchall()

def insert_artists(conn, spotify_artist_id: str, spotify_artist_url: str, artist_name: str = None, popularity: int = -1):
    query = """
    INSERT INTO artists (spotify_artist_id, spotify_artist_url, artist_name, popularity)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (spotify_artist_id) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(query, (spotify_artist_id, spotify_artist_url, artist_name, popularity))
    return spotify_artist_id


def insert_albums(conn, spotify_album_id: str, spotify_album_url: str, album_name: str, total_tracks: int, release_date, spotify_artist_id: str):
    query = """
    INSERT INTO albums (spotify_album_id, spotify_album_url, album_name, total_tracks, release_date, spotify_artist_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (spotify_album_id) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(query, (spotify_album_id, spotify_album_url, album_name, total_tracks, release_date, spotify_artist_id))
    return spotify_album_id


def insert_tracks(conn, spotify_track_id: str, spotify_track_url: str, track_name: str, album_name: str, spotify_artist_id: str, spotify_album_id: str, release_date, duration_ms: int, popularity: int, explicit: bool):
    query = """
    INSERT INTO tracks (spotify_track_id, spotify_track_url, track_name, album_name, spotify_artist_id, spotify_album_id, release_date, duration_ms, popularity, explicit)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (spotify_track_id) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(query, (spotify_track_id, spotify_track_url, track_name, album_name, spotify_artist_id, spotify_album_id, release_date, duration_ms, popularity, explicit))
    return spotify_track_id


def insert_recently_played(conn, user_id: int, spotify_track_id: str, played_at):
    query = """
    INSERT INTO listened_history (user_id, spotify_track_id, played_at)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id, spotify_track_id, played_at) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(query, (user_id, spotify_track_id, played_at))

if __name__ == "__main__":
    try:
        store_songs()
    except Exception as e:
        error_msg = traceback.format_exc()
        send_error_email(error_msg)
        raise