from dataclasses import dataclass
from typing import Optional, Tuple
import tekore as spot
from tekore._auth.scope import Scope
from modules.maria import MariaDB as db


@dataclass
class CallbackObject:
    code: str
    state: str


class SpotifyUserObject:
    def __init__(
        self, discord_user_id: str, user_token: Optional[spot.RefreshingToken] = None
    ) -> None:
        self.scopes = Scope(
            spot.scope.user_read_currently_playing,
            spot.scope.user_modify_playback_state,
            spot.scope.user_read_playback_state,
        )
        self.CLIENT_ID = "2aa04ebf6b1c4ee3a120ddf4b4d19ddb"
        self.CLIENT_SECRET = "4321bb638fb74c7b91a27ad8dc6e9798"
        self.REDIRECT_URI = "https://rival.rocks/"
        self.default_device_id = None
        self.discord_user_id = discord_user_id
        self.cred = spot.RefreshingCredentials(
            self.CLIENT_ID, self.CLIENT_SECRET, self.REDIRECT_URI
        )
        self.auth = spot.UserAuth(self.cred, scope=self.scopes)
        self.client_token = spot.request_client_token(
            self.CLIENT_ID, self.CLIENT_SECRET
        )
        self.user_token = user_token
        self.session = spot.Spotify(
            token=self.user_token or self.client_token, asynchronous=False
        )
        self.session_type = "user" if self.user_token else "client"
        if not self.user_token:
            self.check_for_existing_user()

    async def check_for_existing_user(self) -> None:
        data=await db.execute("""SELECT * FROM spotify""")
        for user_id,access_token,refresh_token,expires_at,default_device_id in data:
            if user_id == self.discord_user_id:
                await bot.db.execute("""DELETE FROM spotify WHERE user_id = %s""", self.discord_user_id)

    def authorize_user(
        self, callback: CallbackObject
    ) -> Tuple[bool, Optional[Exception]]:
        """Authorize a User object with given callback details. Sets self.user_token.

        Returns:
            tuple:
                - bool - True if successful, False if error thrown
                - Optional - Exception object, if thrown
        """
        try:
            _token = self.auth.request_token(code=callback.code, state=callback.state)
            try:
                assert isinstance(
                    _token, spot.RefreshingToken
                )  # this should always return a RefreshingToken, but just in case
            except AssertionError:
                return (
                    False,
                    f"Tekore authenticator did not return RefreshingToken (rtype: {_token.__class__.__name__}). This should **never** happen, and is *probably* not an astrobot issue. Please try your request again. If the issue persists, file a bug report.",
                )
            self.user_token = _token
        except Exception as err:
            return (False, err)
        return (True, None)

    def refresh_token(self):
        try:
            self.user_token = self.cred.refresh_user_token(
                self.user_token.refresh_token
            )
            return True
        except Exception:
            return False

    async def store_to_db(self):
        await db.execute("""INSERT INTO spotify VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id) AND access_token = VALUES(access_token) AND refresh_token = VALUES(refresh_token) AND expires_at = VALUES(expires_at) AND default_device_id = VALUES(default_device_id)""",self.discord_user_id,self.user_token.access_token,self.user_token.refresh_token,self.user_token._token.expires_at,self.default_device_id)
        return True

    async def update_db(self):
        await db.execute("""INSERT INTO spotify VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id) AND access_token = VALUES(access_token) AND refresh_token = VALUES(refresh_token) AND expires_at = VALUES(expires_at) AND default_device_id = VALUES(default_device_id)""",self.discord_user_id,self.user_token.access_token,self.user_token.refresh_token,self.user_token._token.expires_at,self.default_device_id)

    async def pop_from_db(self):
        import time

        _db_tok = None
        data=await db.execute("""SELECT * FROM spotify""")
        for user_id,access_token,refresh_token,expires_at,default_device_id in data:
            obj=(user_id,access_token,refresh_token,expires_at,default_device_id)
            if user_id == self.discord_user_id:
                _db_tok = obj
                break

        if not _db_tok:
            return False

        _tok = spot.Token(
            token_info={
                "token_type": "Bearer",
                "access_token": _db_tok.access_token,
                "refresh_token": _db_tok.refresh_token,
                "expires_in": int(_db_tok.expires_at) - int(time.time()),
            },
            uses_pkce=False,
        )
        _tok._scope = self.scopes
        self.user_token = spot.RefreshingToken(_tok, self.cred._client)
        self.session.token = self.user_token
        self.session_type = "user"
        self.default_device_id = _db_tok.default_device_id
        return True


def __login(user: SpotifyUserObject):
    """for testing only, do not this function anywhere besides the REPL!"""
    import webbrowser
    from urllib.parse import urlparse
    from urllib.parse import parse_qs

    webbrowser.open(user.auth.url)
    _redirurl = input("URL: ")
    _params = parse_qs(urlparse(_redirurl).query)
    callback = CallbackObject(_params["code"][0], _params["state"][0])
    if user.authorize_user(callback)[0]:
        return True
    return False
