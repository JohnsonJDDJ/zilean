from msilib.schema import Error
from xml.dom import InvalidAccessErr
from yaml import KeyToken
from riotwatcher import LolWatcher

from .core import *

class SnapShots:

    def __init__(self, timeline, frames=[8], matchid=None) -> None:
        self.summary = process_timeframe(timeline, frames, matchid)
        self.matchid = matchid
        self.frames = frames
        self.win = self.summary['win']

    def fetch_lolwatcher(self, api_key=None) -> LolWatcher:
        """Fetch LolWatcher with API key"""
        key = read_api_key(api_key)
        self.watcher = LolWatcher(api_key=key)
        return self.watcher

    def fetch_match_summary(self, region) -> dict:
        if not self.watcher:
            raise NameError("LolWatcher does not exist. Please connect with Riot API with `.fetch_lolwatcher()` with your api key")
        return self.watcher.match.by_id(region, self.matchid)