import loadSave as ls
import requests
import time



def check_match_type(match_data, match_id):
    """
    Checks if the match data corresponds to the desired game mode (ARAM).

    Args:
        match_data (dict): The match data retrieved from the Riot Games API.

    Returns:
        dict or None: The match data if it matches the desired game mode, or None if it doesn't.
    """
    if match_data['info']['gameMode'] == 'ARAM':
        return match_data
    else:
        return None


def get_puuid(api_key, summoner_name):
    """
    Retrieves the encrypted PUUID (Player Universally Unique Identifier) of a summoner.

    Args:
        api_key (str): The Riot Games API key.
        summoner_name (str): The name of the summoner.

    Returns:
        str: The PUUID of the summoner.
    """
    
    # summonerName_puuid_map = {}
    ''' player_puuid_map = {
            player_name: puuid
    }
    '''

    # load the summonerName_puuid_map from file
    # summonerName_puuid_map = ls.load_summonerName_puuid_map()

    # # if summoner_name in summonerName_puuid_map:
    # if summoner_name in summonerName_puuid_map:
    #     return summonerName_puuid_map[summoner_name]
    
    response = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}")
    summoner_data = response.json()
    # summonerName_puuid_map[summoner_name] = summoner_data['puuid']
    # ls.save_summonerName_puuid_map(summonerName_puuid_map)
    return summoner_data['puuid']



def get_match_history(api_key, summoner_puuid, games_fetched):
    """
    Retrieves the match history (list of match IDs) for a summoner.

    Args:
        api_key (str): The Riot Games API key.
        summoner_puuid (str): The PUUID of the summoner.
        games_fetched (int): The number of games to fetch.

    Returns:
        list: A list of match IDs.
    """
    match_ids = []
    start = 0
    count = 100  # Number of games to fetch per request

    # if the new match_ids are already in the match_data_map (one of the keys) then we do not need to make more api_calls

    while games_fetched > 0:
        if games_fetched < count:
            count = games_fetched

        response = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?start={start}&count={count}&api_key={api_key}")
        
        # Check for rate limit exceeded (429) response
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 120))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue
        
        # Return match IDs if response is successful (200)
        if response.status_code == 200:
            match_ids.extend(response.json())
            # check if any of the  current 100 match_ids is in match_data_map (the keys are match_ids) then we can
            # matching_ids = [match_id for match_id in match_ids if match_id in match_data_map]
            # if match_ids:
            #     print(f'Match IDs found: dont need to go farther in history')
            #     return match_ids
            # return the current match_history since we now know that we already have the older games as just need to look at the most recent 100-500
            # match_ids.extend(response.json())
        
        games_fetched -= count
        start += count
    # print(f'No Matching IDs found')
    return match_ids

def get_match_data(api_key, match_id):


    response = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}")
    # add response to the hash map with the match_id as the key

    # Check for rate limit exceeded (429) response
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 120))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return get_match_data(api_key, match_id)
        
    # Return match data if response is successful (200)
    if response.status_code == 200:
        return response.json()

def get_summoner_name_from_puuid(api_key, summoner_puuid):

    response = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summoner_puuid}?api_key={api_key}')

    # Check for rate limit exceeded (429) response
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 120))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return get_summoner_name_from_puuid(api_key, summoner_puuid)

    # Return match data if response is successful (200)
    if response.status_code == 200:
        summoner_info = response.json()
        return summoner_info['name']



import datetime
def convert_game_time(game_creation):
    """
    Converts the gameCreation time from the League of Legends API to a date format.

    Args:
        game_creation (int): The gameCreation time obtained from the API.

    Returns:
        str: The gameCreation time converted to a date format.
    """
    # Convert the gameCreation time to a datetime object
    game_creation_datetime = datetime.datetime.fromtimestamp(game_creation / 1000)
    
    # Format the datetime object as a string
    game_creation_date = game_creation_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # print(game_creation_date)
    return game_creation_date

# match_data = get_match_data('RGAPI-70db93e7-4326-4f80-b361-9fae7034e6fd', 'NA1_4651987820')

# def determine_winning_team_id(match_data):
#     for team in match_data['info']['teams']:
#         if team['win'] == True:
#             #print('winning team' + str(team['teamId']))
#             return team['teamId']


# def determine_losing_team_id(match_data):
#     for team in match_data['info']['teams']:
#         if team['win'] == False:
#             #print('winning team' + str(team['teamId']))
#             return team['teamId']

# match_values = (
#                 match_data['metadata']['matchId'], match_data['metadata']['dataVersion'], match_data['metadata']['participants'], convert_game_time(match_data['info']['gameCreation']),
#                 match_data['info']['gameDuration'], convert_game_time(match_data['info']['gameEndTimestamp']), match_data['info']['gameId'], match_data['info']['gameMode'],
#                 match_data['info']['gameName'], convert_game_time(match_data['info']['gameStartTimestamp']), match_data['info']['gameType'], match_data['info']['gameVersion'], match_data['info']['mapId'],
#                 match_data['info']['platformId'], match_data['info']['queueId'], determine_winning_team_id(match_data), determine_losing_team_id(match_data)
#             )
# for value in match_values:
#     print(f'value: {value} type: {type(value)}')


# # print(match_data)
# print(match_data['info']['gameEndTimestamp'])
# print(match_data)
# print(match_data['info']['teams'])
# winning_team_id = 0



# print(winning_team_id)