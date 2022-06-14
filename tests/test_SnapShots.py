from zilean import SnapShots

import json, os

# Current file location:
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load in example timeline for testing
example_file = os.path.join(__location__, "example_timeline.json")
with open(example_file , "r") as example:
    example_timeline = json.load(example)

invalid_timeline = {"Nope": 0}


def test_load_dict():
    """Load an example Riot `MatchTimelineDto`"""
    SnapShots(example_timeline[0])


def test_load_json():
    """Load an example file with Riot `MatchTimelineDto`"""
    SnapShots(example_file)


def test_to_disk_and_load():
    """
    Load an example Riot `MatchTimelineDto`, save to csv using 
    to_disk(), and then load the csv file again.
    """
    # To disk
    snaps_1 = SnapShots(example_file)
    snaps_1.to_disk(path=__location__, verbose=False)
    # Load both files
    match_file = os.path.join(__location__, "match_8.csv")
    frame_file = os.path.join(__location__, "frame_8.csv")
    SnapShots(match_file)
    SnapShots(frame_file)
    # Delete files
    os.remove(match_file)
    os.remove(frame_file)


def test_load_invalid_dict():
    """Load a invalid Riot `MatchTimelineDto`"""
    try:
        SnapShots(invalid_timeline)
    except ValueError:
        pass;


def test_correct_summary():
    """Test the values from the summary is correct."""
    snaps = SnapShots(example_file)
    # Per match
    per_match = snaps.summary(per_frame=False)[0]
    assert per_match["level_0"] == -1
    assert per_match["xp_2"] == -767
    # Per frame
    per_frame = snaps.summary(per_frame=True)[0]
    assert per_frame["level_0"] == per_match["level_0"]
    assert per_frame["xp_2"] == per_match["xp_2"]


def test_summary_per_frame():
    """Test the per_frame option is working correctly"""
    snaps = SnapShots(example_file)

    per_match = snaps.summary(per_frame=False)[0]
    per_frame = snaps.summary(per_frame=True)[0]

    assert "frame" not in per_match.keys()
    assert "frame" in per_frame.keys()
    assert per_frame["frame"] == 8


def test_empty_get_lanes():
    """Test both options of empty get_lanes."""
    snaps = SnapShots(example_file)

    assert len(snaps.get_lanes([], per_frame=False)[0].keys()) == 2
    assert len(snaps.get_lanes([], per_frame=True)[0].keys()) == 3


def test_get_lanes_value():
    """Test values of both options of get_lanes"""
    snaps = SnapShots(example_file)
    
    per_match = snaps.get_lanes(["TOP", 2], per_frame=False)[0]
    per_frame = snaps.get_lanes([0, "MID"], per_frame=True)[0]

    assert per_frame["level_0"] == per_match["level_0"]
    assert per_frame["xp_2"] == per_match["xp_2"]

    assert "level_1" not in per_match.keys()
    assert "level_4" not in per_frame.keys()


def test_strange_lanes():
    """Test invalid lanes for both options of get_lanes"""
    snaps = SnapShots(example_file)

    assert len(snaps.get_lanes([5, 7], per_frame=False)[0].keys()) == 2
    assert len(snaps.get_lanes(["NO", "FOO"], per_frame=True)[0].keys()) == 3