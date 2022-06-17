import os
import json
from tqdm import tqdm

# =================
# == Basic Utils == 
# =================

def read_api_key(api_key=None):
    """
    Fetch the Riot Development API key.

    Keyword arguments:

    - api_key: A string representing the api Key. If None (default), 
      it will try to read the file `apikey` in the current directory.

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
    Append a dictionary to a file. The file are organized line-by-line 
    (each dic is a line).

    Arguments:

    - dic: Any dictionary.
    - file: String, representing a file name.
    """
    with open(file, 'a') as f:
        json.dump(dic, f)
        f.write('\n')


def clean_json(file, cutoff=16) -> list:
    """
    Clean a messy file into a propoer dictionary and rewrite the file
    as proper JSON. Return the JSON content as a dictionary.

    Arguments:

    - file: String. Messy file produced by write_messy_json(dic, file).
    - cutoff: Integer. Represents the minimum minutes a match must have.

    Return:
    
    - The cleaned JSON content as a dictionary.
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
    print(f"There are in total {len(matches)} crawled KR high elo matches " +
          f"longer than {cutoff} minutes.")
    with open(file, 'w') as f:  
        json.dump(matches, f)
    return matches

# =====================
# == Data Processing == 
# =====================

def json_data_mask(dic):
    """
    Construct a list of keys that have dictionary as their corresponding
    value pair. The list acts as a mask for further cleaning.

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
    Clean unwanted features of a specific frame from a `Riot MatchTimelineDto`
    and fetch player data. 

    Arguments:

    - timeline: A Riot `MatchTimelineDto`. More info at 
    (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)

    Keyword arguments:

    - frames: A list of integers representing the frames of interest. 
      The function does not handle cases where element of `frames` is larger
      than the total number of frames of `timeline`.

    Return:

    - Dictionary of list of dictionaries. Each nested dictionary represent
      a player at one `frame` of `timeline`
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


def add_creep_score(timeframes):
    """
    Compute and append the creep score as a feature for a specific
    timeframe. The creep score is the amount of minion/jungle minions
    killed by a player.

    Arguments:

    - timeframe: A Dictionary of list of dictionaries. Each nested
      dictionary represent a player at each timeframe of interest.
    
    Return:

    - `timeframe` with creep score computed.
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


def add_proportion(timeframes):
    """
    Transform original features to proportions, which include:

    - Total gold -> gold porportion. Gold porportion measures the 
      porportion of gold in this position in relation to the total
      gold of the whole team. This feature is more advance because
      it considers the total gold of the team.
    - Xp -> xp porportion. Xp porportion measures the porportion
      of xp in this position in relation to the total xp of the whole
      team. This feature is more advance because it considers the total
      xp of the team.
    
    Arguments:

    - timeframe: A Dictionary of list of dictionaries. Each nested
      dictionary represent a player at each timeframe of interest.
    
    Return:
    
    - `timeframe` with porportions computed.
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



def process_timeframe(timeline, frames=[8], matchid=None, creep_score=True, 
                      porportion=True):
    """
    Return a single dictionary with cleaned and processed data for
    specific frames of a `Riot MatchTimelineDto`.

    Arguments:

    - timeline: A Riot `MatchTimelineDto`. More info at 
      (https://developer.riotgames.com/apis#match-v5/GET_getTimeline)

    Keyword arguments:

    - frames: A list of integer representing the frames of interest. 
      The function does not handle cases where element of `frames` is larger 
      than the total number of frames of `timeline`.
    - matchid: The unique matchid corresponding to `timeline`.
    - creep_score: Boolean. If True (recommended), then compute the creep 
      score for the players, then drop the `minionKilled` and 
      `jungleMinionKilled` feature of the players.
    - porportion: Boolean. If True, then add `goldPorportion` and 
      `xpPorportion` as features to the players.

    Return:

    - Dictionary containing cleaned and processed data for each frame
      in `frames` in `timeline`. Ready for further data analysis.
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
    """
    Check if the given input is a valid `MatchTimelineDto`. Return
    the match id if it is valid, return `None` oterhwise. 
    """
    matchid = None
    try:
        # The matchid
        matchid = timeline["metadata"]["matchId"]
        # The match result label
        win = timeline['info']['frames'][-1]['events'][-1]['winningTeam'] == 100
        # The participants
        timeline['info']['frames'][0]['participantFrames'].values()
        return matchid
    except:  
        raise ValueError("The input dictionary is not a valid " +
                         "MatchTimelineDto")      