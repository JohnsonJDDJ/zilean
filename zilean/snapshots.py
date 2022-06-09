from riotwatcher import LolWatcher
import pandas as pd

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
        self.per_frame_summary_ = None;


    def summary(self, per_frame=False, verbose=False) -> list:
        """
        Return the summary for all the matches (Riot MatchTimelineDtos). For each match,
        summary statistics of every time frame of interest is computed. The summary is ready
        for further data analysis.

        Keyword Arguments:
        
        - per_frame: Boolean. If False (default), each match (Riot MatchTimelineDto) is
        one dictionary. If True, each frame (in minutes) of a match is one dictionary.
        - verbose: Boolean, default False. If True, print out the progress.

        Return:
        
        - A list of dictionaries, ready for further data analysis. Each dictionary is either
        a match or a frame (see `per_frame`). 
        """

        # Compute summary_ and per_frame_summary_ if they are not already cached
        if (not self.summary_) or (not self.per_frame_summary_):
            # Load the timelines from source
            with open(self.timelines) as f:
                if verbose:
                    print(f"Loading file {self.timelines}. It might take >5 min if file is large.")
                matches = json.load(f)
                if verbose:
                    print(f"There is in total {len(matches)} matches successfully loaded.")

            if verbose:
                    print(f"Unpacking matches into dictionaries.")
            self.summary_ = []
            self.per_frame_summary_ = []

            for match in matches:
                matchid = match['id']
                timeline = match['timeline']
                # Match summary
                self.summary_ += [process_timeframe(timeline, frames=self.frames, matchid=matchid,
                                                    creep_score=self.creep_score, porportion=self.porportion)]
                # Per frame summary
                for frame in self.frames:
                    frame_dic = process_timeframe(timeline, frames=[frame], matchid=matchid,
                                                  creep_score=self.creep_score, porportion=self.porportion)
                    frame_dic['frame'] = frame
                    self.per_frame_summary_ += [frame_dic]
            del matches

        # Return the summary based on `per_frame`
        if per_frame:
            return self.per_frame_summary_
        else :
            return self.summary_


    def to_disk(self) -> None:
        """Save the summaries to disk as csv files using pandas.DataFrame.to_csv()"""
        if not self.summary_ or not self.per_frame_summary_:
            raise ValueError("Summary statistics are yet to be computed. Please run `summary()` first.")

        path = "data/"
        file_name = '_'.join(str(e) for e in self.frames)

        pd.DataFrame(self.summary_).to_csv(path+"match_"+file_name+".csv")
        pd.DataFrame(self.per_frame_summary_).to_csv(path+"frame_"+file_name+".csv")

        print(f"Saved files to direcotry {path}.")
    

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