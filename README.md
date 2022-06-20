# Zilean

[![codecov](https://codecov.io/gh/JohnsonJDDJ/zilean/branch/main/graph/badge.svg?token=FF4RCILBK9)](https://codecov.io/gh/JohnsonJDDJ/zilean) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6636849.svg)](https://doi.org/10.5281/zenodo.6636849)

This projects aims to predict [League of Legends](https://www.leagueoflegends.com) 5v5 Ranked Solo match results using snapshots of game stats before the 16 minute mark

> _Zilean is a League of Legends character that can drift through past, present and future. The project is borrowing Zilean's temporal magic to foresee the result of a match._

**The project is open to all sorts of contribution and collaboration! Please feel free to clone, fork, PR...anything! If you are interested, contact me!**

Contact: Johnson Du <johnsondzh@gmail.com>

[Introduction](#Introduction)\
[Demo](#Demo)\
[Data](#Data)

## Introduction

Zilean is a data analysis project with an accompanying python package. **The project aims to reach high accuracy predicting the outcome of a League of Legends _5v5 Ranked Solo high elo match in KR server_**. From the prediciton, draw insights on the factors that have significant impacts on the result of a match.

Different from traditional sports, esports such as League of Legends has an innate advantage of collecting data from matches. Since every play was conducted digitally, it opened up a huge potential to explore and perform all kinds of data analysis. In this project, not only is it aimed at reaching high accuracy and drawing insights to the factors impacting the result of a match. **`zilean` wishes to create a tool that can ficilitate the process of communicating with the Riot API and perform data analytical techniques** on League of Legends matches related data. 

## Demo

Here is a quick look of how to do League of Legends data analysis with `zilean`

```python
from zilean import TimelineCrawler, SnapShots, read_api_key
import pandas as pd

# Use the TimelineCrawler to fetch `MatchTimelineDto`s 
# from Riot. The `MatchTimelineDto`s have game stats 
# at each minute mark.

# We need a API key to fetch data. See the Riot Developer
# Portal for more info.
api_key = read_api_key(you_api_key_here)
# Crawl 2000 Diamond RANKED_SOLO_5x5 timelines from the Korean server.
crawler = TimelineCrawler(api_key, region="kr", 
                          tier="DIAMOND", queue="RANKED_SOLO_5x5")
result = crawler.crawl(2000, match_per_id=30, file="results.json")
# This will take a long time!

# We will look at the player statistics at 10 and 15 minute mark.
snaps = SnapShots(result, frames=[10, 15])

# Store the player statistics using in a pandas DataFrame
player_stats = snaps.summary(per_frame=True)
data = pd.DataFrame(player_stats) 

# Look at the distribution of totalGold difference for `player 0` (TOP player)
# at 15 minutes mark.
sns.displot(x="totalGold_0", data=data[data['frame'] == 15], hue="win")
```

![demo_1.png](demo_1.png)

Here is an example of some quick modelling.

```python
# Do some simple modelling
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Define X and y for training data
train, test = train_test_split(player_stats, test_size=0.33)
X_train = train.drop(["matchId", "win"], axis=1)
y_train = train["win"].astype(int)

# Build a default random forest classifier
rf = RandomForestClassifier()
rf.fit(X_train, y_train)
y_fitted = rf.predict(X_train)
print(f"Training accuracy: {mean(y_train == y_fitted)}")
```

## Data

The data is collected using the official [Riot API](https://developer.riotgames.com/apis) with the help from the python package [Riot-Watcher](https://github.com/pseudonym117/Riot-Watcher). To view the data, please visit [Zenodo](https://doi.org/10.5281/zenodo.6596322). 

The dataset contains information about all League of Legends KR server challengers (n=300) as of 2022-05-23. The account information is stored in `accounts.json`, whereas the information about the challenger league is in `kr_challenger_league.json`. 

Match data was retrieved from the 5 most recent 5v5 ranked solo matches for each challenger account. There are in total 2166 unique matches. The matches are further cleaned only to include games that last more than 16 minutes (n=2078), which are stored in `matches.json`.
