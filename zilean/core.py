import os
import json
from time import time
from tqdm import tqdm

# =================
# == Basic Utils == 
# =================

def read_api_key(api_key:str=None) -> str:
    """Fetch the Riot Development API key. If None provided, it 
    will try to read the file `apikey` in the working directory.

    Parameters
    ----------
    api_key : :obj:`str`, optional
        The api key. 
    
    Returns
    -------
    str
        The api_key.

    Notes
    -----
        This function's main purpose is to hide your api key on
        public resources. You would want to store your api key
        in a file named `apikey` in the working directory, and 
        fetch your api key everytime through this function.
    """
    if not api_key:
        if not os.path.exists('apikey'):
            raise ValueError("Please provide valid Riot API key.")
        else:
            with open('apikey', 'r') as f:
                return f.read()
    else:
        return api_key

def write_messy_json(dic, file) -> None:
    """Append a dictionary to a file. The file are organized
    line-by-line (each dict is a line).

    Parameters
    ----------
    dic : dict
        Any dictionary.
    file : str
        Name of file to append.
    """
    with open(file, 'a') as f:
        json.dump(dic, f)
        f.write('\n')


def clean_json(file:str, cutoff:int=16) -> list:
    """Clean a messy JSON file that store `MatchTimelineDto`s.
    Only retain matches that last longer than a specific cutoff.

    Parameters
    ----------
    file : str
        Messy file produced by write_messy_json(dic, file).
    cutoff : int
        Minimum minutes the matches must have. Defaults to 16.

    Returns
    -------
    dict
        The cleaned JSON content as a dictionary.
    """
    with open(file, 'r') as f:
        matches = []
        for i, line in enumerate(tqdm(f)):
            match = json.loads(line)
            frame_interval = match['info']['frameInterval']
            total_frame_num = len(match['info']['frames'])
            if total_frame_num < int(cutoff*60000/frame_interval):
                continue;
            matches += [match]
    print(f"There are in total {len(matches)} crawled matches " +
          f"longer than {cutoff} minutes.")
    with open(file, 'w') as f:  
        json.dump(matches, f)
    return matches

# =====================
# == Data Processing == 
# =====================

def json_data_mask(dic:dict) -> list:
    """Construct a list of keys that have dictionary as their
    corresponding value pair. The list acts as a mask for further
    cleaning.

    Parameters
    ----------
    dic: dict.
        Any dictionary.

    Returns
    -------
    list
        Keys of input dictionary which have dictionary as value. 
    """
    keys_to_remove = []
    for k,v in dic.items():
        if type(v) is dict:
            keys_to_remove = keys_to_remove + [k]
    return keys_to_remove


def clean_timeframe(timeline:dict, frames:list=[8]) -> dict:
    """Clean unwanted features of a specific frame from a 
    `Riot MatchTimelineDto` and fetch player data. 

    Parameters
    ----------
    timeline : dict
        A Riot `MatchTimelineDto`. More info at 
        (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)
    frames : list
        Integers representing the frames of interest, defaults to [8]. 
    
    Returns
    -------
    dict
        Timeline with cleaned data. It will be a dictionary with
        lists as values. Elememnts of each list value are dictionaries.
        Each nested dictionary represent a player at one `frame` 
        of the `timeline`

    Notes
    -----
        The function does not handle cases where element of `frames`
        is larger than the total number of frames of the `timeline`.
    """
    players_mega_dict = {}
    for frame in frames:
        players_mega_dict[str(frame)] = list(timeline['info']['frames'][frame]
                                             ['participantFrames'].values())
    keys_to_remove = json_data_mask(players_mega_dict[str(frames[0])][0])
    keys_to_remove += ['currentGold', 'goldPerSecond', 'participantId', 
                       'magicDamageDone', 'magicDamageDoneToChampions', 
                       'magicDamageTaken', 'physicalDamageDone', 
                       'physicalDamageDoneToChampions', 'physicalDamageTaken',
                       'trueDamageDone', 'trueDamageDoneToChampions', 
                       'trueDamageTaken']
    for frame, player_list in players_mega_dict.items():
        for player in player_list:
            if 'damageStats' in player.keys():
                damage_stat = player['damageStats']
                player.update(damage_stat)
            for key in keys_to_remove:
                if key in player.keys():
                    player.pop(key)
    return players_mega_dict


def add_creep_score(timeframes:dict) -> dict:
    """Compute and append the creep score as a feature for a specific
    timeframe. The creep score is the amount of minion/jungle minions
    killed by a player.

    Parameters
    ----------
    timeframes : dict
        A dictionary with lists as values. Elememnts of each list value
        are dictionaries. Each nested dictionary represent a player at
        one frame of the `timeframes`.
    
    Returns
    -------
    dict
        `timeframes` with creep score computed.
    """
    if type(timeframes) is not dict:
        raise TypeError("Input timeframes must be a dictionary")
    
    for _, player_list in timeframes.items():
        for player in player_list:
            if 'jungleMinionsKilled' in player.keys() and 'minionsKilled' in player.keys():
                player['creepScore'] = player['jungleMinionsKilled'] + player['minionsKilled']
                player.pop('jungleMinionsKilled')
                player.pop('minionsKilled')
            elif 'jungleMinionsKilled' not in player.keys() and 'minionsKilled' not in player.keys():
                if 'creepScore' not in player.keys():
                    raise ValueError("Missing information to construct creep score for a player.")
            else:
                raise ValueError("Missing information to construct creep score for a player.")
    
    return timeframes


def add_proportion(timeframes:dict) -> dict:
    """Transform original features to proportions, which include:

    - Total gold -> gold porportion. Gold porportion measures the 
      porportion of gold in this position in relation to the total
      gold of the whole team. This feature is more advance because
      it considers the total gold of the team.
    - Xp -> xp porportion. Xp porportion measures the porportion
      of xp in this position in relation to the total xp of the whole
      team. This feature is more advance because it considers the total
      xp of the team.
    
    Parameters
    ----------
    timeframes : dict
        A dictionary with lists as values. Elememnts of each list value
        are dictionaries. Each nested dictionary represent a player at
        one frame of the `timeframes`.

    Returns
    -------
    dict
        `timeframes` with porportions computed.
    """
    if type(timeframes) is not dict:
        raise TypeError("Input timeframes must be a dictionary")

    for frame, player_list in timeframes.items():
        # Calculate total gold and xp for the team
        blue_gold, blue_xp, red_gold, red_xp = 0, 0, 0, 0
        for index, player in enumerate(player_list):
            if 'totalGold' not in player.keys() or 'xp' not in player.keys():
                raise ValueError("Missing crucial information to construct " +
                                 "proportion stats for a player.")
            if index < 5:
                blue_gold += player["totalGold"]
                blue_xp += player["xp"]
            else:
                red_gold += player["totalGold"]
                red_xp += player["xp"]
        # Compute porportions
        for index, player in enumerate(player_list):
            if index < 5:
                player["goldPorportion"] =  player["totalGold"] / blue_gold
                player["xpPorportion"] =  player["xp"] / blue_xp
            else:
                player["goldPorportion"] =  player["totalGold"] / red_gold
                player["xpPorportion"] =  player["xp"] / red_xp

    return timeframes


def process_timeframe(timeline:dict, frames:list=[8], matchid:str=None, 
                      creep_score:bool=True, porportion:bool=True) -> dict:
    """Return a single dictionary with cleaned and processed data for
    specific frames of a `Riot MatchTimelineDto`.

    Parameters
    ----------
    timeline : dict
        A Riot `MatchTimelineDto`. More info at 
        (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)
    frames : list 
        Integers representing the frames of interest, defaults to [8].
    matchid : :obj:`str`, optional
        The unique matchid corresponding to `timeline`, defaults to
        None.
    creep_score : bool
        Whether to compute the creep_score, defaults to True.
    porportion : bool
        Whether to add `goldPorportion` and `xpPorportion` as 
        features to the players, default to True.
    
    Returns
    -------
    dict
        Dictionary containing cleaned and processed data for each frame
        in `frames` in `timeline`. Ready for further data analysis.

    Notes
    -----
        The function does not handle cases where element of `frames`
        is larger than the total number of frames of the `timeline`.
    """
    win = timeline['info']['frames'][-1]['events'][-1]['winningTeam'] == 100
    cleaned = clean_timeframe(timeline, frames)
    if creep_score:
        cleaned = add_creep_score(cleaned)
    if porportion:
        cleaned = add_proportion(cleaned)
    final_dict = {}
    if len(frames) == 1:
        frame = frames[0]
        for i in range(5):
            for key in list(cleaned[str(frame)][0].keys()):
                key_name = key+'_'+str(i)
                final_dict[key_name] = (cleaned[str(frame)][i][key] 
                                        - cleaned[str(frame)][i+5][key])
    else:
        for frame in frames:
            for i in range(5):
                for key in list(cleaned[str(frame)][0].keys()):
                    key_name = key+'_'+str(i)+'_frame'+str(frame)
                    final_dict[key_name] = (cleaned[str(frame)][i][key]
                                            - cleaned[str(frame)][i+5][key])
    final_dict['matchId'] = matchid if matchid else 'UNKNOWN'
    final_dict['win'] = bool(win)
    return final_dict


def validate_timeline(timeline):
    """Check if the given input is a valid `MatchTimelineDto`. 
    Return the match id if it is valid, return `None` oterhwise.
    """
    matchid = None
    try:
        # The matchid
        matchid = timeline["metadata"]["matchId"]
        # Frame interval
        timeline['info']['frameInterval']
        # The match result label
        timeline['info']['frames'][-1]['events'][-1]['winningTeam']
        # The participants
        timeline['info']['frames'][0]['participantFrames'].values()
        return matchid
    except:  
        raise ValueError("The input dictionary is not a valid " +
                         "MatchTimelineDto")      