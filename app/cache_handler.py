from spotipy import CacheHandler
from app.database import get_connection

class DBCacherHandler(CacheHandler):
    def __init__(self, user_id : str):
        self.user_id = user_id

    def get_cached_token(self):
        conn = get_connection()
        cur = conn.cursor()
        query = 'SELECT * FROM spotify_tokens WHERE user_id = %s'
        value = self.user_id
        with conn, cur:
            cur.execute(query, (value,))
            row = cur.fetchone()
            return {
                "access_token": row["access_token"],
                "token_type": row["token_type"],
                "expires_in": row["expires_in"],
                "scope": row["scope"],
                "refresh_token": row["refresh_token"],
                "expires_at": row["expires_at"],
                "updated_at": row["updated_at"]
            }
    
    def save_token_to_cache(self, token_info):
        query = """
            INSERT INTO spotify_tokens (user_id, access_token, token_type, expires_in, scope, refresh_token, expires_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (user_id) 
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                token_type = EXCLUDED.token_type,
                expires_in = EXCLUDED.expires_in,
                scope = EXCLUDED.scope,
                refresh_token = EXCLUDED.refresh_token,
                expires_at = EXCLUDED.expires_at,
                updated_at = NOW()
            """
        values = (self.user_id, token_info["access_token"], token_info["token_type"], int(token_info["expires_in"]), token_info["scope"], token_info["refresh_token"], token_info["expires_at"])
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, values)


