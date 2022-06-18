class DummyLeagueApiV4:
    """
    A dummy LeagueApiV4 with static method returns.
    """
    dummyLeagueList = {
        "entries": [
            {"summonerId": "dummy"}
        ]
    }
    dummyLeagueEntry = [
        {"summonerId": "dummy"}
    ]

    def __init__(self) -> None:
        pass
    
    def challenger_by_queue(self, region, queue) -> dict:
        return self.dummyLeagueList

    def grandmaster_by_queue(self, region, queue) -> dict:
        return self.dummyLeagueList

    def masters_by_queue(self, region, queue) -> dict:
        return self.dummyLeagueList

    def entries(self, region, queue, tier, division) -> list:
        return self.dummyLeagueEntry