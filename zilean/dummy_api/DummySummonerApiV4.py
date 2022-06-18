class DummySummonerApiV4:
    """
    A dummy SummonerApiV4 with static method returns.
    """
    def __init__(self) -> None:
        pass

    def by_id(self, region, id) -> dict:
        dummy_return = {
            "summonerId": id,
            "puuid": id
        }
        return dummy_return