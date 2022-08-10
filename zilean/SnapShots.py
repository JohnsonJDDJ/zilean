from collections import defaultdict
from copy import deepcopy
import pandas as pd

from .core import *


class SnapShots:
    """SnapShots is used for extracting interesting player data from
    Riot ``MatchTimelineDto`` s. SnapShots is a helper object that
    facilitates data analysis on League of Legends matches.

    The reason for the name is because SnapShots can extract player 
    data from a match at specific time intervals, or ``frames`` 
    (in minutes). Data at frames of interest can be used to, for 
    example, predict the result of a match.

    Attributes
    ----------
    timelines : str | list | dict
        The source data. It can be either a: 
            - String, a file name where either a list of ``MatchTimelineDto`` s 
              (in JSON format) or the computed summary statistics (csv) is 
              stored.  The computed summary statistics (csv) should be an
              earlier saved DataFrame using the SnapShots.to_disk() method.
            - List. A list of ``MatchTimelineDto`` s.
            - Dict. A single ``MatchTimelineDto``.
    frames : list
        Integers indicating the frames (in minutes) of
        interest. Default [8]. This argument does nothing if the 
        specified input ``timelines`` file is a stored summary file
        in csv. 
    creep_score: bool
        Compute the creep score for the players, then drop the
        ``minionKilled`` and ``jungleMinionKilled`` feature of the 
        players. Defaults to True.
    porportion: bool 
        Add ``goldPorportion`` and ``xpPorportion`` as features to 
        the players. Defaults to True.
    verbose: bool 
        Print out the progress of loading the source data, defaults
        to False.
    """

    def __init__(self, timelines, frames=[8], creep_score=True, porportion=True,
                 verbose=False) -> None:
        self.timelines = timelines
        self.frames = frames
        self.creep_score = creep_score
        self.porportion = porportion
        self.summary_ = []
        self.per_frame_summary_ = []
        self.feature_info_ = []

        # Dict, a single `MatchTimelineDto`
        if type(timelines) == dict:
            # Verify if its a MatchTimelineDto
            matchid = validate_timeline(timelines)
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
        # List, multiple `MatchTimelineDto`s
        elif type(timelines) == list:
            for match in timelines:
                matchid = validate_timeline(match)
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
        # String, a file
        elif type(timelines) == str:
            # Detect the file type
            filetype = timelines.split(".")[-1]
            # JSON, a list of `MatchTimelineDto`s
            if filetype == "json":
                # Compute summary_ and per_frame_summary_
                # Load the timelines from source
                with open(self.timelines) as f:
                    if verbose:
                        print(f"Loading file {self.timelines}." +
                              "It might take >5 min if file is large.")
                    matches = json.load(f)
                    if verbose:
                        print(f"There is in total {len(matches)} " +
                              "matches successfully loaded.")
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
            # CSV, a previously saved summary using to_disk()
            elif filetype == "csv":
                per_match_file = timelines.replace("frame", "match")
                per_frame_file = timelines.replace("match", "frame")
                self.summary_ = pd.read_csv(per_match_file, index_col=[0])\
                    .to_dict("records")
                self.per_frame_summary_ = pd.read_csv(per_frame_file, index_col=[0])\
                    .to_dict("records")
        # None of above
        else:
            raise ValueError("Input is neither a valid file name (csv of json), " +
                             "nor is a valid MatchTimelineDto")

        # Construct feature info
        for key in self.summary_[0].keys():
            # Split the feature name where there is a "_"
            feature_info = key.split("_")
            if len(feature_info) == 3:
                self.feature_info_.append({
                    "name" : key, 
                    "feature" : feature_info[0], 
                    "lane" : int(feature_info[1]), 
                    "frame" : int(feature_info[2].split('e')[1])
                })
            elif len(feature_info) == 2 and len(self.frames) == 1:
                self.feature_info_.append({
                    "name": key, 
                    "feature": feature_info[0],
                    "lane": int(feature_info[1]),
                    "frame": self.frames[0]
                })
            else:
                self.feature_info_.append({
                    "name": key, 
                    "feature": None,
                    "lane": None,
                    "frame": None
                })
                
            

    def summary(self, per_frame=False) -> list:
        """Return the summary for all the matches (``MatchTimelineDto``).
        For each match, summary statistics of every time frame of interest
        is returned. The summary is ready for further data analysis.

        Parameters
        ----------
        per_frame: bool
            If False (default), each match (``MatchTimelineDto``)
            is one dictionary. If True, each frame (in minutes) of a
            match is one dictionary. Defaults to False.

        Returns
        -------
        list
            A list of dictionaries, ready for further data analysis. 
            Each dictionary is either a match or a frame 
            (see `per_frame`). 
        """
        # Return the summary based on `per_frame`
        if per_frame:
            return self.per_frame_summary_
        else:
            return self.summary_


    def to_disk(self, path="data/", verbose=True) -> None:
        """Save the summaries to disk as csv files using 
        pandas.DataFrame.to_csv()

        Parameters
        ----------
        path : str
            Path name relative to your working directory. Defaults 
            to ``data/``
        verbose : bool 
            Print the directory where of the saved file. Defaults to
            True
        """
        file_name = '_'.join(str(e) for e in self.frames)
        per_match_path = os.path.join(path, "match_"+file_name+".csv")
        per_frame_path = os.path.join(path, "frame_"+file_name+".csv")
        pd.DataFrame(self.summary_).to_csv(per_match_path)
        pd.DataFrame(self.per_frame_summary_).to_csv(per_frame_path)
        if verbose:
            print(f"Saved files to direcotry {os.path.join(os.getcwd(), path)}.")


    def subset(self, features=[], lanes=[], frames=[]):
        """Return a new SnapShots with only a subset of the 
        original summary statistics. Features
        of the original summary statistics contain information that
        is seperated by underscores. The generic format of a
        feature is "FEATURE_LANE_frame#". For example, 
        ``totalGold_0_frame8`` is the total gold difference 
        between the TOP players at 8 minutes mark.

        Parameters
        ----------
        features : :obj:`list`, optional 
            Features of interest. For available options, please
            refer to the ``.feature_info_`` variable.
        lanes : :obj:`list`, optional 
            Lane options are any of {"TOP", "JUG", "MID", "BOT",
            "SUP"} or their corresponding index {0, 1, 2, 3, 4}. 
        frames : :obj:`list`, optional
            Frames options can only be chosen from the frames
            specified during the initiation of this SnapShots 
            instance.

        Returns
        -------
        zilean.SnapShots 
            A new SnapShots with only a subset of the 
            original summary statistics.
        
        Notes
        -----
            The method will return a copy of the original
            summary statistics if no argument were provided.
        """
        duplicate = deepcopy(self)
        lane_str_convert = {"TOP": 0, "JUG": 1,
                            "MID": 2, "BOT": 3, "SUP": 4}
        keys_to_extract = []

        # Convert `lanes` to all integers
        for i, lane in enumerate(lanes):
            if lane in lane_str_convert.keys():
                lanes[i] = lane_str_convert[lane]

        # Add key matching the criteria to `keys_to_extract`
        keys_to_extract += []
        # Construct a new feature_info_
        new_feature_info = []
        for col in self.feature_info_:
            if ((not lanes or col["lane"] in lanes) and 
                (not features or col["feature"] in features) and
                (not frames or col["frame"] in frames)):
                keys_to_extract += [col["name"]]
                new_feature_info += [col]

        new_feature_info += self.feature_info_[-2:]
        duplicate.feature_info_ = new_feature_info

        # Construct the new summary_ using keys_to_extract
        keys_to_extract += ["matchId", "win"]
        new_summary_ = []
        for row in self.summary_:
            new_summary_ += [{key: row[key] for key in keys_to_extract}]
        duplicate.summary_ = new_summary_

        # Construct the new per_frame_summary_ using keys_to_extract
        keys_to_extract += ["frame"]
        new_per_frame_summary_ = []
        for row in self.per_frame_summary_:
            new_per_frame_summary_ += [{key: row[key] for key in keys_to_extract}]
        duplicate.per_frame_summary_ = new_per_frame_summary_
        
        return duplicate


    def agg(self, type, func=sum) -> list:
        """Aggregate summary statistics either by
        team or by frame. If by team, the statistics
        across all five lanes are aggregated. If by
        frame, the statistics across all frames are
        aggregated. The default aggregate function
        is the summation.

        Parameters
        ----------
        type : str
            Either "team" or "frame". 
            - "team": Aggregate summary statistics
              by team. A team consist of five lanes, 
              marked by number 0 to 4 in the feature
              names. For example: ``totalGold_0_frame8`` ,
              ``totalGold_1_frame8`` , ..., 
              ``totalGold_4_frame8`` will be aggregated
              into a single feature ``totalGold_frame8`` .
            - "frame": Aggregate summary statistics
              by frame. Frames are usually marked by a number 
              after "frame" the feature names. For example: 
              ``totalGold_0_frame8`` and
              ``totalGold_0_frame12`` will be aggregated
              into a single feature ``totalGold_0`` .

        func : function
            A function to perform the aggregation. Defaults
            to sum (the summation function).
        
        Returns
        -------
        list
            Summary statistics after aggregation.

        Notes
        -----
            This method is not compatible with per frame
            summary. This feature may deploy in  feature 
            versions.
        """
        mapping = defaultdict(list)
        for col in self.feature_info_:
            # None value means its a special feature
            if not col["feature"]:
                continue
            if type == "team":
                new_feature_name = col["feature"] + "_frame" + str(col["frame"])
            elif type == "frame":
                new_feature_name = col["feature"] + "_" + str(col["lane"])
            mapping[new_feature_name].append(col["name"])
        
        print(mapping)

        agg_summary = []
        
        for match in self.summary_:
            row = {}
            for k, v in mapping.items():
                row[k] = func([match[vv] for vv in v])
            agg_summary.append(row)

        return agg_summary