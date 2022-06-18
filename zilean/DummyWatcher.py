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
        self.league = DummyLeagueApiV4()
        self.summoner = DummySummonerApiV4()
        self.match = DummyMatchApiV5()