from riotwatcher import LolWatcher

from .core import *

class SnapShots:
    """
    SnapShots is used for extracting interesting player data from Riot `MatchTimelineDto`s.
    SnapShots is a helper object that facilitates data analysis on League of Legends matches.

    The reason for the name is because SnapShots can extract player data from a match at specific
    time intervals, or `frames` (in minutes). Data at frames of interest can be used to, for 
    example, predict the result of a match.

    Arguments:

    - timelines: String, a file name where the source data are stored. The source data should
      be a list of dictionaries, where each dictionary represent one unique match. The
      dictionaries will have two keys: 
      - `id`: String, to indicate the unique match id of the match.
      - `timeline`: a Riot `MatchTimelineDto`.

    Keyword Arguments:
    
    - frames: List of integers, indicating the frames (in minutes) of interest. Default [8].
    - creep_score: Boolean. If True (recommended), then compute the creep score for the players, then
      drop the `minionKilled` and `jungleMinionKilled` feature of the players.
    - porportion: Boolean. If True, then add `goldPorportion` and `xpPorportion` as features to the players.
    """

    def __init__(self, timelines, frames=[8], creep_score=True, porportion=True) -> None:
        self.timelines = timelines
        self.frames = frames
        self.creep_score = creep_score
        self.porportion = porportion
        self.summary_ = None;
        self.frame_independent_summary_ = None;

    def summary(self, frame_independent=False, verbose=False) -> list:
        """
        Return the summary for all the matches (Riot MatchTimelineDtos). For each match,
        summary statistics of every time frame of interest is computed. The summary is ready
        for further data analysis.

        Keyword Arguments:
        
        - frame_independent: Boolean. If False (default), each match (Riot MatchTimelineDto) is
        one dictionary. If True, each frame (in minutes) of a match is one dictionary.
        - verbose: Boolean, default False. If True, print out the progress.

        Return:
        
        - A list of dictionaries, ready for further data analysis. Each dictionary is either
        a match or a frame (see `frame_independent`). 
        """
        # Load the timelines from source
        with open(self.timelines) as f:
            if verbose:
                print(f"Loading file {self.timelines}. It might take >5 min if file is large.")
            matches = json.load(f)

        # Compute summary_ and frame_independent_summary_ if they are not already cached
        if (not self.summary_) or (not self.frame_independent_summary_):
            self.summary_ = []
            self.frame_independent_summary_ = []

            for match in matches:
                matchid = match['id']
                timeline = match['timeline']
                # Frame dependent summary
                self.summary_ += [process_timeframe(timeline, frames=self.frames, matchid=matchid,
                                                    creep_score=self.creep_score, porportion=self.porportion)]
                # Frame independent summary
                for frame in self.frames:
                    frame_dic = process_timeframe(self.timeline, frames=[frame], matchid=self.matchid,
                                                  creep_score=self.creep_score, porportion=self.porportion)
                    frame_dic['frame'] = frame
                    self.frame_independent_summary_ += [frame_dic]
        
        # Return the summary based on `frame_independent`
        if frame_independent:
            return self.frame_independent_summary_
        else :
            return self.summary_
    
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