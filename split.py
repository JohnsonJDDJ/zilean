import json
import pandas as pd
from sklearn.model_selection import train_test_split
from zilean.snapshots import SnapShots

# Load cleaned matches
with open('data/matches_cleaned.json') as f:
    matches = json.load(f)

# Make DataFrame
snap_list = [SnapShots(match['timeline'], [8, 12], matchid=match['id']) for match in matches]
data = pd.DataFrame([snap.summary() for snap in snap_list])

# Split train test and save to disk
train, test = train_test_split(data, test_size=0.33, random_state=42)
train.to_csv("data/train.csv")
test.to_csv("data/test.csv")