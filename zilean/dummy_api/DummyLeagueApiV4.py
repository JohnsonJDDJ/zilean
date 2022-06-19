class DummyLeagueApiV4:
    """
    A dummy LeagueApiV4 with static method returns.
    """

    def make_dummy_league_list(self, tier):
        dummyLeagueList = {
            "entries": [
                {"summonerId": tier}
            ]
        }
        return dummyLeagueList

    def __init__(self) -> None:
        pass
    
    def challenger_by_queue(self, region, queue) -> dict:
        return self.make_dummy_league_list("CHALLENGER")

    def grandmaster_by_queue(self, region, queue) -> dict:
        return self.make_dummy_league_list("GRANDMASTER")

    def masters_by_queue(self, region, queue) -> dict:
        return self.make_dummy_league_list("MASTER")

    def entries(self, region, queue, tier, division) -> list:
        return self.make_dummy_league_list(tier)["entries"]