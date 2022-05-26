from inspect import FrameInfo
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


def clean_timeframe(timeline, frames=[8]):
    """
    Clean unwanted features of a specific frame from a Riot MatchTimelineDto and fetch player data. 
    Arguments:
     - timeline: A Riot MatchTimelineDto. More info at (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)
    Keyword arguments:
     - frame: A integer representing the frame of interest. The function does not handle cases where
        `frame` is larger than the total number of frames of `timeline`.
    Return:
     - Dictionary of list of dictionaries. Each nested dictionary represent a player at one `frame` of `timeline`
    """
    players_mega_dict = {}
    for frame in frames:
        players_mega_dict[str(frame)] = list(timeline['info']['frames'][frame]['participantFrames'].values())
    keys_to_remove = json_data_mask(players_mega_dict[str(frames[0])][0])
    keys_to_remove += ['currentGold', 'goldPerSecond', 'participantId', 
                       'magicDamageDone', 'magicDamageDoneToChampions', 'magicDamageTaken',
                       'physicalDamageDone', 'physicalDamageDoneToChampions', 'physicalDamageTaken',
                       'trueDamageDone', 'trueDamageDoneToChampions', 'trueDamageTaken']
    for frame, player_list in players_mega_dict.items():
        for player in player_list:
            if 'damageStats' in player.keys():
                damage_stat = player['damageStats']
                player.update(damage_stat)
            for key in keys_to_remove:
                if key in player.keys():
                    player.pop(key)
    return players_mega_dict


def add_creep_score(timeframes):
    """
    Compute and append the creep score as a feature for a specific timeframe.
    Arguments:
     - timeframe: A Dictionary of list of dictionaries. Each nested dictionary represent a player at this timeframe.
    Return:
     - `timeframe` with creep score computed.
    """
    if type(timeframes) is not dict:
        raise TypeError("Input timeframes must be a dictionary")
    
    for frame, player_list in timeframes.items():
        for player in player_list:
            if 'jungleMinionsKilled' in player.keys() and 'minionsKilled' in player.keys():
                player['creepScore'] = player['jungleMinionsKilled'] +player['minionsKilled']
                player.pop('jungleMinionsKilled')
                player.pop('minionsKilled')
            elif 'jungleMinionsKilled' not in player.keys() and 'minionsKilled' not in player.keys():
                if 'creepScore' not in player.keys():
                    raise ValueError("Missing information to construct creep score for a player.")
            else:
                raise ValueError("Missing information to construct creep score for a player.")
    
    return timeframes


def process_timeframe(timeline, frames=[8], matchid=None):
    """
    Return a single dictionary with cleaned and processed data for a specific frame of a
    Riot MatchTimelineDto.
    Arguments:
     - timeline: A Riot MatchTimelineDto. More info at (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)
    Keyword arguments:
     - frame: A list of integer representing the frames of interest. The function does not handle cases where
        element of `frame` is larger than the total number of frames of `timeline`.
     - matchid: The u ique matchid corresponding to `timeline`.
    Return:
     - Dictionary containing cleaned and processed data for each frame in `frames` in `timeline`. 
        Ready for further data analysis.
    """
    win = timeline['info']['frames'][-1]['events'][-1]['winningTeam'] == 100
    cleaned = clean_timeframe(timeline, frames)
    cleaned = add_creep_score(cleaned)
    final_dict = {}
    for frame in frames:
        for i in range(5):
            for key in list(cleaned[str(frame)][0].keys()):
                final_dict[key+'_'+str(i)+'_frame'+str(frame)] = cleaned[str(frame)][i][key] - cleaned[str(frame)][i+5][key]
    final_dict['matchId'] = matchid if matchid else 'UNKNOWN'
    final_dict['win'] = bool(win)
    return final_dict