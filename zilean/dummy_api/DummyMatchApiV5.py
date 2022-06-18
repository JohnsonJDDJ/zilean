class DummyMatchApiV5:
    """
    A dummy MatchApiV5 with static method returns.
    """

    def __init__(self) -> None:
        pass

    def matchlist_by_puuid(self, region, id) -> list:
        dummy_return = [
            "dummy_1",
            "dummy_2"
        ]
        return dummy_return

    def timeline_by_match(self, region, matchId) -> dict:
        dummy_return = {
            "metadata": {
                "matchId": matchId,
            },
            "info": {
                "frameInterval": 60000,
                "frames": [
                    {
                        "participantFrames": {
                            "1": {"key": 1},
                            "2": {"key": 2},
                            "3": {"key": 3},
                            "4": {"key": 4},
                            "5": {"key": 5},
                            "6": {"key": 0},
                            "7": {"key": 0},
                            "8": {"key": 0},
                            "9": {"key": 0},
                            "10": {"key": 0},
                        },
                        "events": []
                    },
                    {
                        "events": [{"winningTeam": 100}]
                    }
                ]
            }
        }
        return dummy_return