from tqdm import tqdm
from riotwatcher import LolWatcher

from .core import *

class TimelineCrawler:
    """An automatic crawler for Riot ``MatchTimelineDto`` s. The Riot
    ``MatchTimelineDto`` s contain stats of a match at each minute mark.
    The crawler runs ``riotwatcher.LolWatcher`` under the hood.

    Attributes
    ----------
    api_key : str
        Your Riot API key. You must have a valid API key to access
        information through the Riot API. Defaults to None.
    region : str
        The region of interest, defaults to None.
    tier : str
        Tier level of the matches, defaults to None.
    queue : str
        The queue type of the matches, defaults to None.
    dummy_watcher : :class:`DummyWatcher`
        For testing purpose only, defaults to None.
    
    Notes
    -----
        The available options for ``region`` are

        >>> ["br1", "eun1", "euw1", "jp1", "kr", "la1", "la2",
        ...  "na1", "oc1", "ru", "tr1"]
        
        The available options for ``tier`` are

        >>> ["CHALLENGER", "GRANDMASTER", "MASTER",
        ...  "DIAMOND", "PLATINUM", "GOLD", "SILVER",
        ...  "BRONZE", "IRON"]
        
        The available options for ``queue`` are

        >>> ["RANKED_SOLO_5x5", "RANKED_FLEX_SR",
        ...  "RANKED_FLEX_TT"]
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
        

    def crawl(self, n:int, match_per_id:int=15, file:str=None, 
              cutoff:int=16) -> list:
        """Crawl ``MatchTimelineDto`` s and save results to disk as a
        json file. Also, return a list of unique ``MatchTimelineDto`` s.
        Each ``MatchTimelineDto`` is a dictionary that contains game
        statistics at each minute mark. To perform analysis, feed the
        returned list to a :class:`zilean.SnapShots` object. 

        Parameters
        ----------
        n : int
            The number of unique matches to be crawled. 
        march_per_id : int
            The number of matches to be crawled for each unique 
            account. Recommend to be a minimum of 15. Will handle
            the case if a player have played for less than the 
            specified number of matches. Defaults to 15.
        file : str
            The name of the file to write the crawled result. 
            If None, then result will not be saved to disk. Defaults
            to None.
        cutoff : int
            The mininum number of minutes required for a match to 
            be counted toward the final list. Defaults to 16.

        Returns
        -------
        list
            A list of ``MatchTimelineDto`` s. 
        """
        # Define variables
        to_disk = True if file else False
        file_path = file if to_disk else ".temp.json"

        # Error checking
        if os.path.exists(file_path) and to_disk:
            raise ValueError(f"File {file_path} already exist.")
        if n <= 0:
            raise ValueError("Invalid number of matched to be crawled.")
        if match_per_id <= 0:
            raise ValueError("Invalid number of match per account.")
        if cutoff < 0:
            raise ValueError("Invalid cutoff.")

        # Fetch a set of leagueIds
        # For highest tiers - LeagueLists
        if self.tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]: 
            # For challengers
            if self.tier == "CHALLENGER":
                league_list = self.watcher.league\
                              .challenger_by_queue(self.region,
                                                   self.queue)               
            # For grandmasters
            elif self.tier == "GRANDMASTER":
                league_list = self.watcher.league\
                              .grandmaster_by_queue(self.region,
                                                    self.queue)
            # For masters
            elif self.tier == "MASTER":
                league_list = self.watcher.league\
                              .masters_by_queue(self.region,
                                                self.queue)
            leagueIds = set([league_list["leagueId"]])
        # For all others - LeagueEntries
        else:
            league_entries_set = self.watcher.league\
                                 .entries(self.region, self.queue,
                                          self.tier, "I")
            leagueIds = set([entry["leagueId"] for entry in league_entries_set])
        leagueIds = list(leagueIds)
        leagueIds.sort() # For testing purposes

        # Start crawling                                 
        # Record matches that are already visited
        visited_matchIds = set()
        # Set tqdm progress bar
        pbar = tqdm(total=n)
        pbar.set_description("Crawling matches")
        # Iterate over the leagueIds to fetch leagueEntries
        for leagueId in leagueIds:
            entries = self.watcher.league.by_id(self.region, leagueId)['entries']
            # Then fetch summonerIds for each LeagueEntry
            for entry in entries:
                summonerId = entry['summonerId']
                # Then fetch puuid for that summonerIds
                puuid = self.watcher.summoner.by_id(self.region, summonerId)["puuid"]
                #Then fetch a list of matchIds for that puuid
                match_list = self.watcher.match.matchlist_by_puuid(self.region, puuid)
                # Lastly fetch MatchTimelines for each matchId
                for i in range(min(match_per_id, len(match_list))):
                    matchId = match_list[i]
                    if matchId in visited_matchIds: continue
                    timeline = self.watcher.match.timeline_by_match(self.region,
                                                                    matchId)
                    # Save to disk
                    write_messy_json(timeline, file_path)
                    visited_matchIds.add(matchId)
                    pbar.update(1)
                    if len(visited_matchIds) == n: break
                if len(visited_matchIds) == n: break
            if len(visited_matchIds) == n: break
        if len(visited_matchIds) < n:
            print(f"{n} unique matches cannot be met with match_per_id "+
                  f"= {match_per_id} (currently {len(visited_matchIds)} matches).")
        pbar.close()
        # Clean matches with specified cutoff
        result = clean_json(file_path, cutoff)
        
        # Clean temporary files if to_dick is False
        if not to_disk:
            os.remove(file_path)

        return result