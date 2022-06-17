from pygments import highlight
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
    
    tier_options_ = ["CHALLENGER",
                     "GRANDMASTER",
                     "MASTER",
                     "DIAMOND",
                     "PLATINUM",
                     "GOLD",
                     "SILVER",
                     "BRONZE",
                     "IRON"]
    
    queue_options_ = ["RANKED_SOLO_5x5",
                      "RANKED_FLEX_SR",
                      "RANKED_FLEX_TT"]


    def __init__(self, api_key:str=None, region:str=None, tier:str=None, 
                 queue:str=None, dummy_watcher=None) -> None:
        # Error checking
        # api_key
        if type(api_key) != str:
            raise TypeError("Invalid API key.")
        else:
            self.api_key = api_key
        # region
        if type(region) != str:
            raise TypeError("Invalid type for region.")
        elif region not in self.region_options_:
            raise ValueError("Invalid value for region. Must be one of " + 
                              f"{self.region_options_} (case sensitive).")
        else:
            self.region = region
        # tier
        if type(tier) != str:
            raise TypeError("Invalid type for tier.")
        elif tier not in self.tier_options_:
            raise ValueError("Invalid value for tier. Must be one of " + 
                              f"{self.tier_options_} (case sensitive).")
        else:
            self.tier = tier
        # queue
        if type(queue) != str:
            raise TypeError("Invalid type for queue.")
        elif queue not in self.queue_options_:
            raise ValueError("Invalid value for queue. Must be one of " + 
                              f"{self.queue_options_} (case sensitive).")
        else:
            self.queue = queue

        # Initiat the LolWatcher
        self.watcher = LolWatcher(api_key=self.api_key)
        if dummy_watcher:
            self.watcher = dummy_watcher
        

    def crawl(self, n:int, match_per_id:int=3, cutoff:int=16, file:str=None,
              verbose:int=0) -> list:
        """
        Crawl `MatchTimelineDto`s and save results to disk as json file.
        Also, return a list of unique `MatchTimelineDto`s.
        Each `MatchTimelineDto` is a dictionary that contains game
        statistics at each minute mark. To perform analysis, feed the
        returned list to a `zilean.SnapShots` object. 
        """
        # For challengers
        if self.tier == "challenger":
            league_entries = self.watcher.league\
                              .challenger_by_queue(self.region,
                                                   self.queue)['entries']
        # For grandmasters
        elif self.tier == "grandmaster":
            league_entries = self.watcher.league\
                              .grandmaster_by_queue(self.region,
                                                    self.queue)['entries']
        # For masters
        elif self.tier == "master":
            league_entries = self.watcher.league\
                              .masters_by_queue(self.region,
                                                self.queue)['entries']
        # For all others
        else:
            league_entries = self.watcher.league\
                                 .entries(self.region, self.queue,
                                          self.tier, "I")
        visited_matchIds = set()
        # Iterate over the league entries to fetch summonerIds
        for entry in league_entries:
            summonerId = entry['summonerId']
            # Then fetch puuid for that summonerIds
            puuid = self.watcher.summoner.by_id(self.region, summonerId)["puuid"]
            #Then fetch a list of matchIds for that puuid
            match_list = self.watcher.match.matchlist_by_puuid(self.region,
                                                               puuid)
            # Lastly fetch MatchTimelines for each matchId
            for i in range(min(match_per_id, len(match_list))):
                matchId = match_list[i]
                if matchId in visited_matchIds: continue
                timeline = self.watcher.match.timeline_by_match(self.region,
                                                                matchId)
                # Save to disk
                write_messy_json(timeline, file)
                visited_matchIds.add(matchId)
                if len(visited_matchIds) == n: break
            if len(visited_matchIds) == n: break
        # Clean matches with specified cutoff
        clean_json(file, cutoff)

