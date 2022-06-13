import pandas as pd

from .core import *

import re


class SnapShots:
    """
    SnapShots is used for extracting interesting player data from
    Riot `MatchTimelineDto`s. SnapShots is a helper object that
    facilitates data analysis on League of Legends matches.

    The reason for the name is because SnapShots can extract player 
    data from a match at specific time intervals, or `frames` (in minutes).
    Data at frames of interest can be used to, for 
    example, predict the result of a match.

    Arguments:

    - timelines: String, a file name where either the source data (json)
      are stored or the computed summary statistics (csv) is stored. 
      - The source data (json) should be a list of dictionaries, where
        each dictionary represent one unique match. The dictionaries
        will have two keys: 
        1. `id`: String, to indicate the unique match id of the match.
        2. `timeline`: a Riot `MatchTimelineDto`.
      - The computed summary statistics (csv) should be an earlier saved
        DataFrame using the SnapShots.to_disk() method.

    Keyword Arguments:
    
    - frames: List of integers, indicating the frames (in minutes) of
      interest. Default [8]. This argument does nothing if the specified
      input `timelines` file is a stored summary file in csv. 
    - creep_score: Boolean. If True (recommended), then compute the creep
      score for the players, then drop the `minionKilled` and 
      `jungleMinionKilled` feature of the players.
    - porportion: Boolean. If True, then add `goldPorportion` and 
      `xpPorportion` as features to the players.
    - verbose: Boolean, default False. If True, print out the progress 
      of loading the source data.
    """

    def __init__(self, timelines, frames=[8], creep_score=True, porportion=True, 
                 verbose=False) -> None:
        self.timelines = timelines
        self.frames = frames
        self.creep_score = creep_score
        self.porportion = porportion
        self.summary_ = []
        self.per_frame_summary_ = []

        if type(timelines) == dict:
            # Verify if its a MatchTimelineDto
            is_valid = False
            matchid = None
            if "metadata" in timelines.keys():
                if "matchId" in timelines["metadata"].keys():
                    matchid = timelines["metadata"]["matchId"]
            if "info" in timelines.keys():
                if "frames" in timelines["info"].keys():
                    if type(timelines["info"]["frames"]) == list:
                        is_valid = True
            if not is_valid:
                raise ValueError("The input dictionary is not a valid MatchTimelineDto")
            
            self.summary_ = [process_timeframe(timelines, frames=self.frames, 
                                               matchid=matchid, 
                                               creep_score=self.creep_score,
                                               porportion=self.porportion)]
            self.per_frame_summary_ = []
            for frame in self.frames:
                frame_dic = process_timeframe(timelines, frames=[frame], 
                                              matchid=matchid,
                                              creep_score=self.creep_score, 
                                              porportion=self.porportion)
                frame_dic['frame'] = frame
                self.per_frame_summary_ += [frame_dic]
        
        elif type(timelines) == str:
            # Detect the file type of timelines
            filetype = timelines.split(".")[-1]

            if filetype == "json":
                # Compute summary_ and per_frame_summary_ 
                # Load the timelines from source
                with open(self.timelines) as f:
                    if verbose:
                        print(f"Loading file {self.timelines}. \
                              It might take >5 min if file is large.")
                    matches = json.load(f)
                    if verbose:
                        print(f"There is in total {len(matches)} \
                              matches successfully loaded.")
                # Unpack file into dictionaries
                if verbose:
                    print(f"Unpacking matches into dictionaries.")
                for match in matches:
                    matchid = match['metadata']['matchId']
                    # Per match summary
                    self.summary_ += [process_timeframe(match, frames=self.frames,
                                                        matchid=matchid,
                                                        creep_score=self.creep_score, 
                                                        porportion=self.porportion)]
                    # Per frame summary
                    for frame in self.frames:
                        frame_dic = process_timeframe(match, frames=[frame], 
                                                      matchid=matchid,
                                                      creep_score=self.creep_score, 
                                                      porportion=self.porportion)
                        frame_dic['frame'] = frame
                        self.per_frame_summary_ += [frame_dic]
                del matches
            
            elif filetype == "csv":
                per_match_file = timelines.replace("frame", "match")
                per_frame_file = timelines.replace("match", "frame")
                self.summary_ = pd.read_csv(per_match_file, index_col=[0])\
                                .to_dict("records")
                self.per_frame_summary_ = pd.read_csv(per_frame_file, index_col=[0])\
                                          .to_dict("records")
        
        else:
            raise ValueError("Input is neither a valid file name (csv of json), \
                              nor is a valid MatchTimelineDto")


    def summary(self, per_frame=False) -> list:
        """
        Return the summary for all the matches (Riot MatchTimelineDtos).
        For each match, summary statistics of every time frame of interest
        is returned. The summary is ready for further data analysis.

        Keyword Arguments:
        
        - per_frame: Boolean. If False (default), each match
          (Riot MatchTimelineDto) is one dictionary. If True, each frame
          (in minutes) of a match is one dictionary.

        Return:
        
        - A list of dictionaries, ready for further data analysis. Each 
          dictionary is either a match or a frame (see `per_frame`). 
        """
        # Return the summary based on `per_frame`
        if per_frame:
            return self.per_frame_summary_
        else :
            return self.summary_


    def to_disk(self) -> None:
        """Save the summaries to disk as csv files using pandas.DataFrame.to_csv()"""
        path = "data/"
        file_name = '_'.join(str(e) for e in self.frames)

        pd.DataFrame(self.summary_).to_csv(path+"match_"+file_name+".csv")
        pd.DataFrame(self.per_frame_summary_).to_csv(path+"frame_"+file_name+".csv")

        print(f"Saved files to direcotry {path}.")
    

    def get_lanes(self, lanes, per_frame=None) -> list:
        """
        Return a slice of the summery statistics that represents specific
        lanes in the game. Statistics of a specific lane in the summary is 
        marked by an underscore and a number at the end of each feature.
        For example, `totalGold_0` represents the total gold difference 
        of the TOP lane. 

        Arguments:

        - lane: List. Position options are any of {"TOP", "JUG", "MID", "BOT",
          "SUP"} or their corresponding index {0, 1, 2, 3, 4}. 

        Keyword Arguments:

        - per_frame: Boolean, default None. If False, each match 
          (Riot MatchTimelineDto) is one dictionary. If True, each frame 
          (in minutes) of a match is one dictionary.

        Return:

        - A list of dictionaries including the statistics for the lanes
          of interest, the matchid, and the label (`win`).
        """
        if (per_frame is None) or (type(per_frame) is not bool):
            raise ValueError("You must specify per_frame to either `True` or `False`.")

        full_summary = self.per_frame_summary_ if per_frame else self.summary_
        str_convert = {"TOP":"0", "JUG":"1", "MID":"2", "BOT":"3", "SUP":"4"}
        keys_to_extract = []

        for lane in lanes:
            # Convert `lanes` to all number strings
            if lane in str_convert.keys():
                lane = str_convert[lane]
            elif type(lane) is int:
                lane = str(lane)
            # Add corresponding key for the lane to `keys_to_extract`
            keys_to_extract += [key for key in full_summary[0].keys() if \
                                re.findall(r'\w+_([0-4])', key) == [lane]]
        keys_to_extract += ["matchId", "win"]
        if per_frame:
            keys_to_extract += ["frame"]

        # Construct slice of summary using `keys_to_extract`
        summary_slice = []
        for row in full_summary:
            summary_slice += [{key: row[key] for key in keys_to_extract}]
        
        return summary_slice