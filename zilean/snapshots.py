from riotwatcher import LolWatcher

from .core import *

class SnapShots:

    def __init__(self, timeline, frames=[8], matchid=None) -> None:
        self.timeline = timeline
        self.matchid = matchid
        self.frames = frames
        self.win = timeline['info']['frames'][-1]['events'][-1]['winningTeam'] == 100

    def summary(self) -> dict:
        """Return summary statistics of all the timeframes of interest as one dictionary."""
        return process_timeframe(self.timeline, self.frames, self.matchid)

    def frame_independent_summary(self) -> list:
        """
        Return multiple summaries of statistics, where each summary is only responsible for
        a single timeframe of interst.
        """
        result_list = []
        for frame in self.frames:
            frame_dic = process_timeframe(self.timeline, [frame], self.matchid)
            frame_dic['frame'] = frame
            result_list += [frame_dic]
        return result_list
    
    def fetch_lolwatcher(self, api_key=None) -> LolWatcher:
        """Fetch LolWatcher with API key"""
        key = read_api_key(api_key)
        self.watcher = LolWatcher(api_key=key)
        return self.watcher

    def fetch_match_info(self, region) -> dict:
        """
        Fetch the corresponding match info (Riot MatchDto) through lolwatcher.
        You must have the LolWatcher object fetched before hand.
        """
        if not self.watcher:
            raise NameError("LolWatcher does not exist. Please connect with Riot API with `.fetch_lolwatcher()` with your api key")
        return self.watcher.match.by_id(region, self.matchid)