from riotwatcher import LolWatcher

from .core import *

class TimelineCrawler:
    """
    An automatic crawler for Riot `MatchTimelineDto`s. The Riot
     `MatchTimelineDto`s contain stats of a match at each minute mark.
    The crawler runs `riotwatcher.LolWatcher` under the hood.

    Keyword Arguments:

    - api_key: String. Default None. Your Riot API key. You must have 
      a valid API key to access information through the Riot API. 
    - region: String. Deafult None. The region of interest. 
    """

    region_options_ = ["br1", 
                       "eun1", "euw1", 
                       "jp1", "kr",
                       "la1", "la2",
                       "na1",
                       "oc1",
                       "ru",
                       "tr1"]
    
    tier_options_ = ["challenger",
                     "grandmaster",
                     "master",
                     "diamond",
                     "platinum",
                     "gold",
                     "silver",
                     "bronze",
                     "iron"]

    high_tiers_ = ["challenger",
                   "grandmaster",
                   "master"]
    
    queue_options_ = ["ranked_solo_5x5",
                      "ranked_flex_sr",
                      "ranked_flex_tt"]

    def __init__(self, api_key=None, region=None, tier=None, queue=None) -> None:
        # Error checking
        # api_key
        if type(api_key) != str:
            raise TypeError("Invalid API key.")
        else:
            self.api_key = api_key
        # region
        if type(region) != str:
            raise TypeError("Invalid type for region.")
        elif region.lower() not in self.region_options_:
            raise ValueError(f"Invalid value for region. Must be one of {self.region_options_} (case non-sensitive)")
        else:
            self.region = region.lower()
        # tier
        if type(tier) != str:
            raise TypeError("Invalid type for tier.")
        elif tier.lower() not in self.tier_options_:
            raise ValueError(f"Invalid value for tier. Must be one of {self.tier_options_} (case non-sensitive)")
        else:
            self.tier = tier.lower()
        # queue
        if type(queue) != str:
            raise TypeError("Invalid type for queue.")
        elif queue.lower() not in self.queue_options_:
            raise ValueError(f"Invalid value for queue. Must be one of {self.queue_options_} (case non-sensitive)")
        else:
            self.queue = queue.lower()
