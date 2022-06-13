from zilean import SnapShots

import json, os

# Current file location:
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load in example timeline for testing
example_file = "example_timeline.json"
with open(os.path.join(__location__, example_file), "r") as example:
    example_timeline = json.load(example)


def test_load_dict():
    """Load an example Riot `MatchTimelineDto`"""
    SnapShots(example_timeline)

def test_load_json():
    """Load an example file with Riot `MatchTimelineDto`"""
    SnapShots(example_file)

def test_to_disk_and_load():
    """
    Load an example Riot `MatchTimelineDto`, save to csv using
    to_disk(), and then load the csv file again.
    """
    snaps_1 = SnapShots(example_timeline)
    snaps_1.to_disk(path=os.path.dirname(__file__))

print(os.path.join(os.path.dirname(__file__), "match.csv"))