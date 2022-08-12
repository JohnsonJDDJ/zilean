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


def test_load_list():
    """Load an example Riot `MatchTimelineDto`"""
    SnapShots(example_timeline)


def test_load_dict():
    """Load an example Riot `MatchTimelineDto`"""
    SnapShots(example_timeline[0])


def test_load_json():
    """Load an example file with Riot `MatchTimelineDto`"""
    SnapShots(example_file, verbose=True)


def test_to_disk_and_load_csv():
    """
    Load an example Riot `MatchTimelineDto`, save to csv using 
    to_disk(), and then load the csv file again.
    """
    # To disk
    snaps_1 = SnapShots(example_file)
    snaps_1.to_disk(path=__location__, verbose=True)
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


def test_empty_subset():
    """Test empty get_lanes."""
    snaps = SnapShots(example_file)
    subset = snaps.subset()
    assert len(subset.summary()[0].keys()) == 52
    assert subset.summary()[0].keys() == snaps.summary()[0].keys()


def test_invalid_subset():
    """Test subset with invalid argument"""
    snaps = SnapShots(example_file)

    assert len(snaps.subset(frames=[9]).summary()[0].keys()) == 2
    assert len(snaps.subset(lanes=["FOO"]).summary()[0].keys()) == 2
    assert len(snaps.subset(features=["NOPE"]).summary()[0].keys()) == 2


def test_subset():
    """Test subset with valid argument"""
    snaps = SnapShots(example_file)

    assert len(snaps.subset(features=["totalGold"]).summary()[0].keys()) == 7
    assert len(snaps.subset(lanes=["TOP"]).summary()[0].keys()) == 12
    assert len(snaps.subset(frames=[8]).summary()[0].keys()) == 52


def test_invalid_agg():
    """Test agg with invalid argument"""
    snaps = SnapShots(example_file)

    try:
        snaps.agg("foo")
    except ValueError:
        pass


def test_agg_type():
    """Test different types of agg"""
    snaps = SnapShots(example_file, frames=[8, 12])

    # Test agg by frame
    by_frame = snaps.agg("frame")[0]
    assert "creepScore_3" in by_frame
    assert by_frame["creepScore_3"] == -26

    # Teat agg by team
    by_team = snaps.agg("team")[0]
    assert "totalDamageDone_frame12" in by_team
    assert by_team["totalDamageDone_frame12"] == -25846


def test_agg_func():
    """Test agg using different aggregation function"""
    snaps = SnapShots(example_file, frames=[8, 12])

    # Using max
    by_team = snaps.agg("team", max)[0]
    assert by_team["totalDamageTaken_frame8"] == 1246
    assert by_team["totalGold_frame12"] == 554

    # Custom function
    custom = snaps.agg("frame", lambda x: x[1])[0]
    assert custom["level_2"] == -2
    assert custom["xp_3"] == -203


def test_subset_agg():
    """Tets agg after subset"""
    snaps = SnapShots(example_file, frames=[8, 12])
    subset_agg_1 = snaps.subset(features=["xp"]).agg("team")[0]
    assert "xp_frame8" in subset_agg_1
    assert "totalGold_frame8" not in subset_agg_1
    assert subset_agg_1["xp_frame8"] == -1553
