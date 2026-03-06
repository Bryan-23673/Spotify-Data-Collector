from app.database import get_connection
from datetime import datetime, timezone
from app.spotify_auth import *

# This file will run as a python to script
# It will actively store songs for each user into the database

conn = get_connection()
cursor = conn.cursor()

# Execute query that will store songs
def store_songs():
    insert_query = (
        'INSERT INTO listened_songs (user_id, track_name, track_id, artist_name, played_at, duration_ms) '
        'VALUES (%s, %s, %s, %s, %s, %s)'
    )
    # we went to loop through all users in the DB
    all_users = get_users()
    for user in all_users:
        # DO NOT MESS WITH THIS
        spotify_user = SpotifyUser(user["user_id"])
        full_client = spotify_user.full_sp_client()
        # KEEP TOGETHER

        # This is the most recent song
        most_recent_song = get_most_recent_song_time(user["user_id"])

        # Make the call to get the songs
        songs = full_client.current_user_recently_played(limit=50, after=1800000)
        items = songs["items"]
        for item in items:
            # Before comparing most_recent_song and played_at, make sure to convert played_at to datetime object since it is currently a string
            track_name = item["track"]["name"]
            track_id = item["track"]["id"]
            artist_name = item["track"]["artists"][0]["name"]
            try:
                played_at = datetime.strptime(item["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                played_at = datetime.strptime(item["played_at"], "%Y-%m-%dT%H:%M:%SZ")
            duration_ms = int(item["track"]["duration_ms"])

            if most_recent_song and played_at <= most_recent_song:
                continue

            played_at = played_at.replace(tzinfo=timezone.utc)
            values = (user["user_id"], track_name, track_id, artist_name, played_at, duration_ms)
            cursor.execute(insert_query, values)

    conn.commit()
    conn.close()

# This function will organize the songs for a user by on played_at in descending order
def get_most_recent_song_time(user_id : str):
    organize_query = (
        f"SELECT DISTINCT user_id, track_name, track_id, artist_name, played_at, duration_ms "
        f"FROM listened_songs "
        f"WHERE user_id = '{user_id}' "
        f"ORDER BY played_at DESC LIMIT 1"
    )
    cursor.execute(organize_query)
    results = cursor.fetchone()
    return results["played_at"] if results else None

def get_users():
    get_user_query = (
        'SELECT user_id FROM spotify_tokens'
    )
    cursor.execute(get_user_query)
    results = cursor.fetchall()
    return results

if __name__ == "__main__":
    store_songs()