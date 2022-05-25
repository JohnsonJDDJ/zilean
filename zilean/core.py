import os
import json
from tqdm.notebook import tqdm


def read_api_key(api_key=None):
    """
    Fetch the Riot Development API key.
    Keyword arguments:
     - api_key: A string representing the api Key. If None (default), it will try to read the
        file `apikey` in the current directory.
    Return:
     - String, the api_key.
    """
    if not api_key:
        if not os.path.exists('apikey'):
            raise ValueError("Please provide valid Riot API key.")
        else:
            with open('apikey', 'r') as f:
                return f.read()
    else:
        return api_key


def write_messy_json(dic, file):
    """
    Append a dictionary to a file. The file are organized line-by-line (each dic is a line).
    Arguments:
     - dic: Any dictionary.
     - dile: String, representing a file name.
    """
    with open(file, 'a') as f:
        json.dump(dic, f)
        f.write('\n')


def clean_json(file):
    """
    Clean a messy file into a propoer dictionary and rewrite the file as proper JSON.
    Arguments:
     - file: messy file produced by write_messy_json(dic, file).
    """
    with open(file, 'r') as f:
        large_dic = []
        for i, line in enumerate(tqdm(f)):
            large_dic += [json.loads(line)]
    with open(file, 'w') as f:  
        json.dump(large_dic, f)


def json_data_mask(dic):
    """
    Construct a list of keys that have dictionary as their corresponding value pair. The list
    acts as a mask for further cleaning.
    Arguments:
     - dic: Any dictionary.
    Return:
     - List. Containing keys of `dic` which have dictionary as value. 
    """
    keys_to_remove = []
    for k,v in dic.items():
        if type(v) is dict:
            keys_to_remove = keys_to_remove + [k]
    return keys_to_remove


def clean_timeframe(timeline, frame=8):
    """
    Clean unwanted features of a specific frame from a Riot MatchTimelineDto and fetch player data. 
    Arguments:
     - timeline: A Riot MatchTimelineDto. More info at (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)
    Keyword arguments:
     - frame: A integer representing the frame of interest. The function does not handle cases where
        `frame` is larger than the total number of frames of `timeline`.
    Return:
     - List of dictionaries. Each dictionary represent a player at `frame` of `timeline`
    """
    players_list = list(timeline['info']['frames'][frame]['participantFrames'].values())
    keys_to_remove = json_data_mask(players_list[0])
    keys_to_remove += ['currentGold', 'goldPerSecond', 'participantId', 'totalDamageDone', 'totalDamageDoneToChampions', 'totalDamageTaken']
    for player in players_list:
        if 'damageStats' in player.keys():
            damage_stat = player['damageStats']
            player.update(damage_stat)
        for key in keys_to_remove:
            if key in player.keys():
                player.pop(key)
    return players_list


def add_creep_score(timeframe):
    """
    Compute and append the creep score as a feature for a specific timeframe.
    Arguments:
     - timeframe: A list of dictionaries. Each dictionary represent a player at this timeframe.
    Return:
     - `timeframe` with creep score computed.
    """
    if type(timeframe) is not list:
        raise TypeError("Input timeframe must be a list")
    elif type(timeframe[0]) is not dict:
        raise TypeError("Elements of inputted timeframe are not dicts.")
    
    for player in timeframe:
        if 'jungleMinionsKilled' in player.keys() and 'minionsKilled' in player.keys():
            player['creepScore'] = player['jungleMinionsKilled'] +player['minionsKilled']
            player.pop('jungleMinionsKilled')
            player.pop('minionsKilled')
        elif 'jungleMinionsKilled' not in player.keys() and 'minionsKilled' not in player.keys():
            if 'creepScore' not in player.keys():
                raise ValueError("Missing information to construct creep score for a player.")
        else:
            raise ValueError("Missing information to construct creep score for a player.")
    
    return timeframe


def process_timeframe(timeline, win, frame=8, matchid=None):
    """
    Return a single dictionary with cleaned and processed data for a specific frame of
    a Riot MatchTimelineDto.
    Arguments:
     - timeline: A Riot MatchTimelineDto. More info at (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)
     - win: Boolean. Whether the blue side won this match.
    Keyword arguments:
     - frame: A integer representing the frame of interest. The function does not handle cases where
        `frame` is larger than the total number of frames of `timeline`.
     - matchid: The u ique matchid corresponding to `timeline`.
    Return:
     - Dictionary containing cleaned and processed data for `frame` in `timeline`. Ready for further data analysis.
    """
    cleaned = clean_timeframe(timeline, frame)
    cleaned = add_creep_score(cleaned)
    final_dict = {}
    for i in range(5):
        for key in list(cleaned[0].keys()):
            final_dict[key+'_'+str(i)] = cleaned[i][key] - cleaned[i+5][key]
    final_dict['matchId'] = matchid if matchid else 'UNKNOWN'
    final_dict['win'] = bool(win)
    return final_dict