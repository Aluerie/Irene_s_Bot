from __future__ import annotations

import collections
import logging
import random
import time
from typing import TYPE_CHECKING, Any, override

import aiohttp
import orjson
from pulsefire.clients import BaseClient
from pulsefire.middlewares import http_error_middleware, json_response_middleware, rate_limiter_middleware
from pulsefire.ratelimiters import BaseRateLimiter

import config

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from pulsefire.invocation import Invocation

    from . import schemas

    type HeaderRateLimitInfo = Mapping[str, Sequence[tuple[int, int]]]


__all__ = (
    "OpenDotaClient",
    "SteamWebAPIClient",
)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class SteamWebAPIClient(BaseClient):
    """Pulsefire client to work with Steam Web API."""

    def __init__(self) -> None:
        super().__init__(
            base_url="https://api.steampowered.com/",
            default_params={},
            default_headers={},
            default_queries={"key": config.STEAM_WEB_API_KEY},
            middlewares=[
                json_response_middleware(orjson.loads),
                http_error_middleware(),
            ],
        )

    async def get_real_time_stats(self, server_steam_id: int) -> schemas.SteamWebAPI.RealtimeStats:
        """GET /IDOTA2Match_570/GetMatchDetails/v1/.

        https://steamapi.xpaw.me/#IDOTA2MatchStats_570/GetRealtimeStats.
        """
        queries = {"server_steam_id": server_steam_id}  # noqa F481
        return await self.invoke("GET", "/IDOTA2MatchStats_570/GetRealtimeStats/v1/")  # type: ignore


class DotaAPIsRateLimiter(BaseRateLimiter):
    """Dota 2 APIs rate limiter.

    This rate limiter can be served stand-alone for centralized rate limiting.
    """

    def __init__(self) -> None:
        self._track_syncs: dict[str, tuple[float, list[Any]]] = {}
        self.rate_limits_string: str = "Not Set Yet"
        self.rate_limits_ratio: float = 1.0
        self._index: dict[tuple[str, int, Any, Any, Any], tuple[int, int, float, float, float]] = (
            collections.defaultdict(lambda: (0, 0, 0, 0, 0))
        )

    @override
    async def acquire(self, invocation: Invocation) -> float:
        wait_for = 0
        pinging_targets = []
        requesting_targets = []
        request_time = time.time()
        for target in [
            ("app", 0, invocation.params.get("region", ""), invocation.method, invocation.urlformat),
            ("app", 1, invocation.params.get("region", ""), invocation.method, invocation.urlformat),
        ]:
            count, limit, expire, latency, pinged = self._index[target]
            pinging = pinged and request_time - pinged < 10
            if pinging:
                wait_for = max(wait_for, 0.1)
            elif request_time > expire:
                pinging_targets.append(target)
            elif request_time > expire - latency * 1.1 + 0.01 or count >= limit:
                wait_for = max(wait_for, expire - request_time)
            else:
                requesting_targets.append(target)
        if wait_for <= 0:
            if pinging_targets:
                self._track_syncs[invocation.uid] = (request_time, pinging_targets)
                for pinging_target in pinging_targets:
                    self._index[pinging_target] = (0, 0, 0, 0, time.time())
                wait_for = -1
            for requesting_target in requesting_targets:
                count, *values = self._index[requesting_target]
                self._index[requesting_target] = (count + 1, *values)  # type: ignore

        return wait_for

    @override
    async def synchronize(self, invocation: Invocation, headers: dict[str, str]) -> None:
        response_time = time.time()
        request_time, pinging_targets = self._track_syncs.pop(invocation.uid, [None, None])
        if request_time is None:
            return

        if random.random() < 0.1:
            for prev_uid, (prev_request_time, _) in self._track_syncs.items():
                if response_time - prev_request_time > 600:
                    self._track_syncs.pop(prev_uid, None)

        try:
            header_limits, header_counts = self.analyze_headers(headers)
        except KeyError:
            for pinging_target in pinging_targets:  # type: ignore
                self._index[pinging_target] = (0, 0, 0, 0, 0)
            return
        for scope, idx, *subscopes in pinging_targets:  # type: ignore
            if idx >= len(header_limits[scope]):
                self._index[(scope, idx, *subscopes)] = (0, 10**10, response_time + 3600, 0, 0)
                continue
            self._index[(scope, idx, *subscopes)] = (
                header_counts[scope][idx][0],
                header_limits[scope][idx][0],
                header_limits[scope][idx][1] + response_time,
                response_time - request_time,
                0,
            )

    def analyze_headers(self, headers: dict[str, str]) -> tuple[HeaderRateLimitInfo, HeaderRateLimitInfo]:
        raise NotImplementedError


class OpenDotaAPIRateLimiter(DotaAPIsRateLimiter):
    @override
    def analyze_headers(self, headers: dict[str, str]) -> tuple[HeaderRateLimitInfo, HeaderRateLimitInfo]:
        self.rate_limits_string = "\n".join(
            [f"{timeframe}: {headers[f'X-Rate-Limit-Remaining-{timeframe}']}" for timeframe in ("Minute", "Day")]
        )
        self.rate_limits_ratio = int(headers["X-Rate-Limit-Remaining-Day"]) / 2000

        header_limits = {
            "app": [(60, 60), (2000, 60 * 60 * 24)],
        }
        header_counts = {
            "app": [
                (int(headers[f"X-Rate-Limit-Remaining-{name}"]), period)
                for name, period in [("Minute", 60), ("Day", 60 * 60 * 24)]
            ]
        }
        return header_limits, header_counts


class OpenDotaClient(BaseClient):
    """Pulsefire client for OpenDota API."""

    def __init__(self) -> None:
        self.rate_limiter = OpenDotaAPIRateLimiter()
        super().__init__(
            base_url="https://api.opendota.com/api",
            default_params={},
            default_headers={},
            default_queries={},
            middlewares=[
                json_response_middleware(orjson.loads),
                http_error_middleware(),
                rate_limiter_middleware(self.rate_limiter),
            ],
        )

    # @overload
    # async def get_match(self, *, match_id: int, raise_exc: Literal[True]) -> schemas.OpenDotaAPI.GetMatch.Match: ...

    # @overload
    # async def get_match(
    #     self, *, match_id: int, raise_exc: Literal[False]
    # ) -> schemas.OpenDotaAPI.GetMatch.Match | None: ...

    async def get_match(self, *, match_id: int) -> schemas.OpenDotaAPI.GetMatch.Match | None:
        """GET matches/{match_id}."""
        try:
            match: schemas.OpenDotaAPI.GetMatch.Match = await self.invoke("GET", f"/matches/{match_id}")  # type: ignore
            return match
        except aiohttp.ClientResponseError as exc:
            log.debug("OpenDota API Response Not OK with status %s", exc.status)
            return None


class ODotaConstantsClient(BaseClient):
    """Pulsefire client to work with OpenDota constants.

    This client works with odota/dotaconstants repository.
    https://github.com/odota/dotaconstants
    """

    def __init__(self) -> None:
        self.rate_limiter = OpenDotaAPIRateLimiter()
        super().__init__(
            # could use `https://api.opendota.com/api/constants` but sometimes they update the repo first
            # and forget to update the site backend x_x
            base_url="https://raw.githubusercontent.com/odota/dotaconstants/master/build",
            default_params={},
            default_headers={},
            default_queries={},
            middlewares=[
                json_response_middleware(orjson.loads),
                http_error_middleware(),
            ],
        )

    async def get_heroes(self) -> schemas.ODotaConstantsJson.Heroes:
        """Get `heroes.json` data.

        https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json
        """
        return await self.invoke("GET", "/heroes.json")  # type: ignore

    async def get_ability_ids(self) -> schemas.ODotaConstantsJson.AbilityIDs:
        """Get `ability_ids.json` data.

        https://raw.githubusercontent.com/odota/dotaconstants/master/build/ability_ids.json
        """
        return await self.invoke("GET", "/ability_ids.json")  # type: ignore

    async def get_abilities(self) -> schemas.ODotaConstantsJson.Abilities:
        """Get `abilities.json` data.

        https://raw.githubusercontent.com/odota/dotaconstants/master/build/abilities.json
        """
        return await self.invoke("GET", "/abilities.json")  # type: ignore

    async def get_hero_abilities(self) -> schemas.ODotaConstantsJson.HeroAbilitiesData:
        """Get `hero_abilities.json` data.

        https://raw.githubusercontent.com/odota/dotaconstants/master/build/hero_abilities.json.
        """
        return await self.invoke("GET", "/hero_abilities.json")  # type: ignore

    async def get_items(self) -> schemas.ODotaConstantsJson.Items:
        """Get `items.json` data.

        https://raw.githubusercontent.com/odota/dotaconstants/master/build/items.json
        """
        return await self.invoke("GET", "/items.json")  # type: ignore
