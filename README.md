# Zilean

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6596322.svg)](https://doi.org/10.5281/zenodo.6596322)

This projects aims to predict [League of Legends](https://www.leagueoflegends.com) 5v5 Ranked Solo match results using snapshots of game stats before the 16 minute mark

Zilean is a League of Legends character that can drift through past, present and future. We are borrowing Zilean's temporal magic to foresee the result of a match.

## Introduction

Zilean is a data analysis project with an accompanying python package. The project aims to reach high accuracy prediciting the outcome of a League of Legends 5v5 Ranked Solo high elo match in KR server. From the prediciton, draw insights on the factors that have significant impacts on the result of a match.

Zilean have an accompanying package `zilean` (under construction) that aids the data analysis process.

## Data

The data is collected using the official [Riot API](https://developer.riotgames.com/apis) with the help from the python package [Riot-Watcher](https://github.com/pseudonym117/Riot-Watcher). To view the data, please visit [Zenodo](https://doi.org/10.5281/zenodo.6582781). 

The dataset contains information about all League of Legends KR server challengers (n=300) as of 2022-05-23. The account information is stored in `accounts.json`, whereas the information about the challenger league is in `kr_challenger_league.json`. 

Match data was retrieved from the 5 most recent 5v5 ranked solo matches for each challenger account. There are in total 811 unique matches, and the information is stored in `matches.json`. The matches are further cleaned only to include games that last more than 16 minutes (n=787), which are stored in `matches_cleaned.json`.