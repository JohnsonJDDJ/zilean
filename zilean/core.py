import os


def read_api_key(api_key=None):
    if not api_key:
        if not os.path.exists('apikey'):
            raise ValueError("Please provide valid Riot API key.")
        else:
            with open('apikey', 'r') as f:
                return f.read()
    else:
        return api_key


def json_data_mask(dic):
    keys_to_remove = []
    for k,v in dic.items():
        if type(v) is dict:
            keys_to_remove = keys_to_remove + [k]
    return keys_to_remove


def clean_timeframe(timeline, frame=5):
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


def process_timeframe(timeline, win, frame=10, matchid=None):
    cleaned = clean_timeframe(timeline, frame)
    cleaned = add_creep_score(cleaned)
    final_dict = {}
    for i in range(5):
        for key in list(cleaned[0].keys()):
            final_dict[key+'_'+str(i)] = cleaned[i][key] - cleaned[i+5][key]
    final_dict['matchId'] = matchid if matchid else 'UNKNOWN'
    final_dict['win'] = bool(win)
    return final_dict