from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    pass


async def refresh_access_token(refresh_token: str, client_id: str, secret: str):
    params = {
        "client_id": client_id,
        "client_secret": secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://id.twitch.tv/oauth2/token", params=params) as response:
            token = await response.json()
            return token.get("access_token")


async def verify_token(token):
    headers = {"Authorization": "Bearer " + token}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://id.twitch.tv/oauth2/validate", headers=headers) as response:
            content = await response.json()
            return False if "status" in content and content["status"] == 401 else content


async def validate(access_token):
    valid = await verify_token(access_token)
    if valid:
        print("Access token is valid.")
    else:
        print("Access token is invalid. Refresh or generate new one.")
