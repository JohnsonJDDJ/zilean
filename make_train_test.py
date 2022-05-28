import sys
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from zilean.snapshots import SnapShots


def main():
    # Parse input: choice of frames
    args = sys.argv[1:]
    frames = [int(arg) for arg in args]
    print(f"Producing game snapshots at frames: {frames}.")
    file_name = '_'.join(str(e) for e in frames)

    # Load cleaned matches
    with open('data/matches_cleaned.json') as f:
        matches = json.load(f)

    # Make DataFrame
    snap_list = [SnapShots(match['timeline'], frames, matchid=match['id']) for match in matches]
    data = pd.DataFrame([snap.summary() for snap in snap_list])

    # Split train test and save to disk
    train, test = train_test_split(data, test_size=0.33, random_state=42)
    train.to_csv("data/train_"+file_name+".csv")
    test.to_csv("data/test_"+file_name+".csv")

if __name__ == "__main__":
    main()
