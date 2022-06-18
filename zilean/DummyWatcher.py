from .dummy_api import (
    DummyLeagueApiV4,
    DummySummonerApiV4,
    DummyMatchApiV5,
)

class DummyWatcher:
    """
    A dummy riotwatcher.LolWatcher for testing purpose. The dummy
    Watcher does not need an api key and have methods of static returns.
    """
    def __init__(self) -> None:
        self.league_ = DummyLeagueApiV4()
        self.summoner_ = DummySummonerApiV4()
        self.match_ = DummyMatchApiV5()

    def league(self) -> DummyLeagueApiV4:
        return self.league_
    
    def summoner(self) -> DummySummonerApiV4:
        return self.summoner_

    def match(self) -> DummyMatchApiV5:
        return self.match_