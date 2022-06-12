# Welcome Collaborators

## Overview

This project was started as a ML data analysis project, but as it grew I developed an accompanying python package `zilean` that is designed to facilitate data analysis of League of Legends matches. 

## Package

The python package `zilean` is an important part of the project, as the ML models also uses the package to manipulate data. There is currently one important class `SnapShots`, which takes in raw json data and unpack them into tabular data. **TODO**: feel free to add more useful methods to this class.

Related files: `zilean/core.py`, `zilean/snapshots.py`

I haven’t had the chance to write any tests for these files. **TODO**: tests!

Related files: `zilean/tests`

## Data

The data we are working with are `Riot MatchTimelineDto`s. These objects record the per minute stats of a ranked match. `zilean` helps to unpack the messy json file into 2-dimensional tables that is ready to be fed into ML models. I have crawled 1.3GB of raw data, which can be unpacked to csv of ~2MB. **TODO**: We have about 2500 unique matches, feel free to help me out and crawl more matches!

Related files: `match_crawler.ipynb`

I am planning to create a new class called `TimelineCrawler`, which is a easier way to crawl `Riot MatchTimelineDto`s and store them for further data analysis. **TODO**: `TimelineCrawler` class.

Related files: `zilean/crawler.py`

## Model

Currently I am using a Random forest model and a XGBoost model to do the predictions. **TODO**: Feel free to explore and build more models to make our analysis more robust!

Related files: `models.ipynb`

I haven’t began the analysis part yet, which involves comparing models, comparing the results, drawing insights. **TODO**: do some exploration on the results of our model predictions.

Related files: `analysis.ipynb`