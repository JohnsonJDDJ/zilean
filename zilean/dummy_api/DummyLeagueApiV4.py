class DummyLeagueApiV4:
    """
    A dummy LeagueApiV4 with static method returns.
    """

    def make_dummy_league_list(self, id):
        dummyLeagueList = {
            "leagueId": id,
            "entries": [
                {"summonerId": id}
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
        dummy_league_entries_set = [
            {"leagueId": tier + "_1"},
            {"leagueId": tier + "_2"}
        ]
        return dummy_league_entries_set
    
    def by_id(self, region, id) -> dict:
        return self.make_dummy_league_list(id)