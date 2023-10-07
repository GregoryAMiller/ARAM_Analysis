import config
import apiCalls as ac
import psycopg2
import datetime
import time

def read_api_key(filename):
    """
    Reads the API key from a text file and returns the API key string.

    Args:
        filename (str): Name of the text file containing the API key.

    Returns:
        str: API key string read from the text file.
    """
    with open(filename, 'r') as file:
        api_key = file.read().strip()
    
    return api_key

def insert_into_player_table(puuid, summoner_name):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host = config.host,
            database = config.database,
            user = config.user,
            password = config.password,
            port = config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Insert data into the "Player" table
        insert_query = "INSERT INTO player (puuid, summoner_name) VALUES (%s, %s)"
        data = (puuid, summoner_name)
        cursor.execute(insert_query, data)

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        print("Data inserted into Player Table successfully.")
    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)

def is_summoner_name_exists(summoner_name):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SELECT query to check if the summoner_name exists
        select_query = "SELECT summoner_name FROM player WHERE summoner_name = %s"
        cursor.execute(select_query, (summoner_name,))
        
        # Fetch the result of the query
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result is not None

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return False

def is_match_id_exists(match_id):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SELECT query to check if the match_id exists
        select_query = "SELECT match_id FROM matches WHERE match_id = %s"
        cursor.execute(select_query, (match_id,))
        
        # Fetch the result of the query
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result is not None

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return False

def is_puuid_match_id_exists(summoner_puuid, match_id):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SELECT query to check if the match_id and summoner_puuid exist
        select_query = "SELECT match_id FROM playerMatches WHERE match_id = %s AND puuid = %s"
        cursor.execute(select_query, (match_id, summoner_puuid,))
        
        # Fetch the result of the query
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result is not None

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return False

def determine_winning_team_id(match_data):
    for team in match_data['info']['teams']:
        if team['win'] == True:
            #print('winning team' + str(team['teamId']))
            return team['teamId']


def determine_losing_team_id(match_data):
    for team in match_data['info']['teams']:
        if team['win'] == False:
            #print('winning team' + str(team['teamId']))
            return team['teamId']

def convert_game_time(game_creation):
    """
    Converts the gameCreation time from the League of Legends API to a PostgreSQL compatible timestamp.

    Args:
        game_creation (int): The gameCreation time obtained from the API.

    Returns:
        str: The gameCreation time converted to a PostgreSQL compatible timestamp.
    """
    # Convert the gameCreation time to a datetime object
    game_creation_datetime = datetime.datetime.fromtimestamp(game_creation / 1000)

    # Format the datetime object as a string in the PostgreSQL timestamp format
    game_creation_timestamp = game_creation_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
    return game_creation_timestamp

def check_player_existence(puuid):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Check if the player with the given puuid exists in the player table
        query = "SELECT COUNT(*) FROM player WHERE puuid = %s"
        cursor.execute(query, (puuid,))
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Return True if the player exists, False otherwise
        return result[0] > 0

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return False
    
def insert_player_match_data(match_data, match_id):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        # if match_id is in matches table skip inserting into matches table
        if not is_match_id_exists(match_id):
            # Convert participants list to a PostgreSQL array format
            participants_array = "{" + ",".join(match_data['metadata']['participants']) + "}"
            # print(participants_array)
            # Insert data into the Matches table
            insert_match_query = """
                INSERT INTO matches (match_id, dataVersion, participants, game_creation, game_duration, game_end_time_stamp,
                game_id, game_mode, game_name, game_start_time_stamp, game_type, game_version, map_id, platform_id, queue_id, winning_team_id, losing_team_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            match_values = (
                match_data['metadata']['matchId'], match_data['metadata']['dataVersion'], participants_array, int(match_data['info']['gameCreation']),
                match_data['info']['gameDuration'], convert_game_time(match_data['info']['gameEndTimestamp']), match_data['info']['gameId'], match_data['info']['gameMode'],
                match_data['info']['gameName'], convert_game_time(match_data['info']['gameStartTimestamp']), match_data['info']['gameType'], match_data['info']['gameVersion'],
                match_data['info']['mapId'], match_data['info']['platformId'], match_data['info']['queueId'], determine_winning_team_id(match_data), 
                determine_losing_team_id(match_data)
            )
            cursor.execute(insert_match_query, match_values)
            print(f'match_id: {match_id} inserted into the matches table!')
        else:
            print(f'match_id: {match_id} is already in the matches table')
        #if not is_puuid_match_id_exists(summoner_puuid, match_id):

        for i in range(0,10):
            if is_puuid_match_id_exists(match_data['info']['participants'][i]['puuid'], match_id):
                print(f'playerMatch already in playerMatches table')
                continue
            if not check_player_existence(match_data['info']['participants'][i]['puuid']):
                insert_into_player_table(match_data['info']['participants'][i]['puuid'], match_data['info']['participants'][i]['summonerName'])
            # Insert data into the PlayerMatches table
            insert_player_match_query = """
                INSERT INTO playerMatches (puuid, match_id, assists, baronKills, bountyLevel, champExperience, champLevel,
                championId, championName, championTransform, consumablesPurchased, damageDealtToBuildings, damageDealtToObjectives, damageDealtToTurrets,
                damageSelfMitigated, deaths, detectorWardsPlaced, doubleKills, dragonKills, firstBloodAssist, firstBloodKill, firstTowerAssist, firstTowerKill,
                gameEndedInEarlySurrender, gameEndedInSurrender, goldEarned, goldSpent, individualPosition, inhibitorKills, inhibitorTakedowns, inhibitorsLost,
                item0, item1, item2, item3, item4, item5, item6, itemsPurchased, killingSprees, kills, lane, largestCriticalStrike, largestKillingSpree, largestMultiKill,
                longestTimeSpentLiving, magicDamageDealt, magicDamageDealtToChampions, magicDamageTaken, neutralMinionsKilled, nexusKills, nexusTakedowns, nexusLost,
                objectivesStolen, objectivesStolenAssists, participantId, pentaKills, physicalDamageDealt, physicalDamageDealtToChampions, physicalDamageTaken,
                profileIcon, quadraKills, riotIdName, riotIdTagline, champion_role, sightWardsBoughtInGame, spell1Casts, spell2Casts, spell3Casts, spell4Casts, summoner1Casts,
                summoner1Id, summoner2Casts, summoner2Id, summonerId, summonerLevel, summonerName, teamEarlySurrendered, teamId, teamPosition, timeCCingOthers, timePlayed, totalDamageDealt,
                totalDamageDealtToChampions, totalDamageShieldedOnTeammates, totalDamageTaken, totalHeal, totalHealsOnTeammates, totalMinionsKilled, totalTimeCCDealt, totalTimeSpentDead,
                totalUnitsHealed, tripleKills, trueDamageDealt, trueDamageDealtToChampions, trueDamageTaken, turretKills, turretTakedowns, turretsLost, unrealKills, visionScore,
                visionWardsBoughtInGame, wardsKilled, wardsPlaced, win)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # i = match_data['metadata']['participants'].index(summoner_puuid)
            # player_damage = match_data["info"]['participants'][i]["totalDamageDealtToChampions"]
            player_match_values = (
                match_data['info']['participants'][i]['puuid'],
                match_data['metadata']['matchId'],
                match_data['info']['participants'][i]['assists'],
                match_data['info']['participants'][i]['baronKills'],
                match_data['info']['participants'][i]['bountyLevel'],
                match_data['info']['participants'][i]['champExperience'],
                match_data['info']['participants'][i]['champLevel'],
                match_data['info']['participants'][i]['championId'],
                match_data['info']['participants'][i]['championName'],
                bool(match_data['info']['participants'][i]['championTransform']),
                match_data['info']['participants'][i]['consumablesPurchased'],
                match_data['info']['participants'][i]['damageDealtToBuildings'],
                match_data['info']['participants'][i]['damageDealtToObjectives'],
                match_data['info']['participants'][i]['damageDealtToTurrets'],
                match_data['info']['participants'][i]['damageSelfMitigated'],
                match_data['info']['participants'][i]['deaths'],
                match_data['info']['participants'][i]['detectorWardsPlaced'],
                match_data['info']['participants'][i]['doubleKills'],
                match_data['info']['participants'][i]['dragonKills'],
                match_data['info']['participants'][i]['firstBloodAssist'],
                match_data['info']['participants'][i]['firstBloodKill'],
                match_data['info']['participants'][i]['firstTowerAssist'],
                match_data['info']['participants'][i]['firstTowerKill'],
                match_data['info']['participants'][i]['gameEndedInEarlySurrender'],
                match_data['info']['participants'][i]['gameEndedInSurrender'],
                match_data['info']['participants'][i]['goldEarned'],
                match_data['info']['participants'][i]['goldSpent'],
                match_data['info']['participants'][i]['individualPosition'],
                match_data['info']['participants'][i]['inhibitorKills'],
                match_data['info']['participants'][i]['inhibitorTakedowns'],
                match_data['info']['participants'][i]['inhibitorsLost'],
                match_data['info']['participants'][i]['item0'],
                match_data['info']['participants'][i]['item1'],
                match_data['info']['participants'][i]['item2'],
                match_data['info']['participants'][i]['item3'],
                match_data['info']['participants'][i]['item4'],
                match_data['info']['participants'][i]['item5'],
                match_data['info']['participants'][i]['item6'],
                match_data['info']['participants'][i]['itemsPurchased'],
                match_data['info']['participants'][i]['killingSprees'],
                match_data['info']['participants'][i]['kills'],
                match_data['info']['participants'][i]['lane'],
                match_data['info']['participants'][i]['largestCriticalStrike'],
                match_data['info']['participants'][i]['largestKillingSpree'],
                match_data['info']['participants'][i]['largestMultiKill'],
                match_data['info']['participants'][i]['longestTimeSpentLiving'],
                match_data['info']['participants'][i]['magicDamageDealt'],
                match_data['info']['participants'][i]['magicDamageDealtToChampions'],
                match_data['info']['participants'][i]['magicDamageTaken'],
                match_data['info']['participants'][i]['neutralMinionsKilled'],
                match_data['info']['participants'][i]['nexusKills'],
                match_data['info']['participants'][i]['nexusTakedowns'],
                match_data['info']['participants'][i]['nexusLost'],
                match_data['info']['participants'][i]['objectivesStolen'],
                match_data['info']['participants'][i]['objectivesStolenAssists'],
                match_data['info']['participants'][i]['participantId'],
                match_data['info']['participants'][i]['pentaKills'],
                match_data['info']['participants'][i]['physicalDamageDealt'],
                match_data['info']['participants'][i]['physicalDamageDealtToChampions'],
                match_data['info']['participants'][i]['physicalDamageTaken'],
                match_data['info']['participants'][i]['profileIcon'],
                match_data['info']['participants'][i]['quadraKills'],
                match_data['info']['participants'][i]['riotIdName'],
                match_data['info']['participants'][i]['riotIdTagline'],
                match_data['info']['participants'][i]['role'],
                match_data['info']['participants'][i]['sightWardsBoughtInGame'],
                match_data['info']['participants'][i]['spell1Casts'],
                match_data['info']['participants'][i]['spell2Casts'],
                match_data['info']['participants'][i]['spell3Casts'],
                match_data['info']['participants'][i]['spell4Casts'],
                match_data['info']['participants'][i]['summoner1Casts'],
                match_data['info']['participants'][i]['summoner1Id'],
                match_data['info']['participants'][i]['summoner2Casts'],
                match_data['info']['participants'][i]['summoner2Id'],
                match_data['info']['participants'][i]['summonerId'],
                match_data['info']['participants'][i]['summonerLevel'],
                match_data['info']['participants'][i]['summonerName'],
                match_data['info']['participants'][i]['teamEarlySurrendered'],
                match_data['info']['participants'][i]['teamId'],
                match_data['info']['participants'][i]['teamPosition'],
                match_data['info']['participants'][i]['timeCCingOthers'],
                match_data['info']['participants'][i]['timePlayed'],
                match_data['info']['participants'][i]['totalDamageDealt'],
                match_data['info']['participants'][i]['totalDamageDealtToChampions'],
                match_data['info']['participants'][i]['totalDamageShieldedOnTeammates'],
                match_data['info']['participants'][i]['totalDamageTaken'],
                match_data['info']['participants'][i]['totalHeal'],
                match_data['info']['participants'][i]['totalHealsOnTeammates'],
                match_data['info']['participants'][i]['totalMinionsKilled'],
                match_data['info']['participants'][i]['totalTimeCCDealt'],
                match_data['info']['participants'][i]['totalTimeSpentDead'],
                match_data['info']['participants'][i]['totalUnitsHealed'],
                match_data['info']['participants'][i]['tripleKills'],
                match_data['info']['participants'][i]['trueDamageDealt'],
                match_data['info']['participants'][i]['trueDamageDealtToChampions'],
                match_data['info']['participants'][i]['trueDamageTaken'],
                match_data['info']['participants'][i]['turretKills'],
                match_data['info']['participants'][i]['turretTakedowns'],
                match_data['info']['participants'][i]['turretsLost'],
                match_data['info']['participants'][i]['unrealKills'],
                match_data['info']['participants'][i]['visionScore'],
                match_data['info']['participants'][i]['visionWardsBoughtInGame'],
                match_data['info']['participants'][i]['wardsKilled'],
                match_data['info']['participants'][i]['wardsPlaced'],
                match_data['info']['participants'][i]['win']
            )
            cursor.execute(insert_player_match_query, player_match_values)
            summoner_name = match_data['info']['participants'][i]['summonerName']
            print(f'{summoner_name}, match_id: {match_id} inserted into the playerMatches table!')
        print(f'summoner {summoner_name}, match_id: {match_id} in the playerMatches table')

        # Commit the changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # print("Data inserted successfully.")
        return True

    except (Exception, psycopg2.Error) as error:
        print("Mark Error connecting to PostgreSQL database:", error)
        return False

def get_puuid_by_summoner_name(summoner_name):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SELECT query to retrieve the puuid for the given summoner_name
        select_query = "SELECT puuid FROM player WHERE summoner_name = %s"
        cursor.execute(select_query, (summoner_name,))

        # Fetch the result of the query
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        if result:
            return result[0]  # Return the puuid if summoner_name exists in the player table
        else:
            return None  # Return None if summoner_name does not exist

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None
           
def is_player_match_exists(match_id, summoner_puuid):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SELECT query to check if the entry exists in PlayerMatches table
        select_query = "SELECT 1 FROM playerMatches WHERE match_id = %s AND puuid = %s"
        cursor.execute(select_query, (match_id, summoner_puuid))
        
        # Fetch the result of the query
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result is not None

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return False

def get_unique_participants():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the query to fetch the participants from the matches table
        query = """
                    SELECT m.participants
                    FROM matches m
                    INNER JOIN playerMatches pm ON m.match_id = pm.match_id
                    WHERE pm.summonername = 'Shade20'
                """
        cursor.execute(query)

        # Fetch the result of the query
        result = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Extract the unique participant PUUIDs from the result
        unique_participants = set()
        for row in result:
            participants = row[0]
            unique_participants.update(participants)

        return list(unique_participants)

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return []

# def get_summoner_name_by_puuid(api_key, summoner_puuid):
#     # if the puuid is not already in the player table
#         # make api call to get summoner_name from puuid
#         # return the summoner_name

# Usage example
# unique_participants = get_unique_participants()
# print(len(unique_participants))

def get_summoner_name_by_puuid(puuid):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the query to check if puuid exists in the player table
        query = "SELECT summoner_name FROM player WHERE puuid = %s"
        cursor.execute(query, (puuid,))

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # If result exists, return the summoner_name
        if result:
            return result[0]
        else:
            return None

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None
    
def create_list_of_summoner_names(api_key):
    summoner_puuids = get_unique_participants()
    print(len(summoner_puuids))
    summoner_puuids = summoner_puuids[:1000]
    summoner_names = []
    for counter, puuid in enumerate(summoner_puuids, start=1):
        # check the database to see if that puuid is the player table
        summoner_name = get_summoner_name_by_puuid(puuid)
        # if the puuid is already in the player table then get the name from the player table via puuid and append the name to the summoner_names
        if summoner_name:
            summoner_names.append(summoner_name)
            print(f'{summoner_name} appended to summoner_names (count: {counter})')
            continue
        summoner_name = ac.get_summoner_name_from_puuid(api_key, puuid)
        summoner_names.append(summoner_name)
        print(f'{summoner_name} appended to summoner_names (count: {counter})')
        insert_into_player_table(puuid, summoner_name)
        print(f'{summoner_name} added to player table')
    return summoner_names

# create_list_of_summoner_names()

def get_player_puuid(api_key, summoner_name):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
            port=config.port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SELECT query to retrieve the player's puuid
        select_query = "SELECT puuid FROM player WHERE summoner_name = %s"
        cursor.execute(select_query, (summoner_name,))

        # Fetch the result of the query
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        if result:
            return result[0]  # Return the player's puuid from the database

        # Summoner not found in the player table, fetch the puuid using the API
        summoner_puuid = ac.get_puuid(api_key, summoner_name)
        return summoner_puuid

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None

def get_unique_match_ids():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
                host=config.host,
                database=config.database,
                user=config.user,
                password=config.password,
                port=config.port
            )


        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the SQL query to retrieve unique match_ids
        query = "SELECT DISTINCT match_id FROM matches;"
        cursor.execute(query)

        # Fetch all the unique match_ids from the result
        unique_match_ids = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return unique_match_ids

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None

def get_match_ids_not_10():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
                host=config.host,
                database=config.database,
                user=config.user,
                password=config.password,
                port=config.port
            )

        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the SQL query to retrieve unique match_ids
        query = """
            SELECT match_id
            FROM playerMatches
            GROUP BY match_id
            HAVING COUNT(*) < 10;
        """
        cursor.execute(query)

        # Fetch all the unique match_ids from the result
        unique_match_ids = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return unique_match_ids

    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None

def main():
    # ['shade20', 'I reformed gg', 'taran', 'Treebéard', 'Poppa Flores', 'TheDeadChicken', 'ronzoni', 'Riot SlickStoat', 'Send Gromp Nudes']
    # create function that loops through a bunch of my games and gets puuids then collects summoner_names via puuids to collect a massive list of puuids
    api_key = read_api_key(filename = 'api_key.txt')

    summoner_list = ['shade20', 'i reformed gg', 'taran', 'treebéard', 'poppa flores', 'thedeadchicken', 'ronzoni', 'riot slickStoat', 'send gromp nudes']
    # summoner_list = create_list_of_summoner_names(api_key)
    games_fetched = 50

    for index, summoner in enumerate(summoner_list):
        print(f"Index: {index}, Summoner: {summoner}")
        # if the summoner_name is already in the player table then return the puuid associated with the summoner_name
        # else call the api to get the puuid fiven the summoner_name
        # if the summoner_name is already in the player table then return the puuid associated with the summoner_name instead of calling api
        summoner_puuid = get_player_puuid(api_key, summoner)
        # print(f'summoner {summoner} in database')
        match_ids = ac.get_match_history(api_key, summoner_puuid, games_fetched)
    # match_ids = get_match_ids_not_10()
    # print(match_ids)
        for index, match_id in enumerate(match_ids):
            print(f"Index: {index}, match_id: {match_id}")
            # if the match_is is not in the table
            # if not is_match_id_exists(match_id):
                # get the match data and insert into database (filling matches table and playerMatches table)
            # if is_player_match_exists(match_id, summoner_puuid):
            #     print(f'match_id {match_id} and summoner_puuid already in playerMatches table')
            #     continue
            match_data = ac.get_match_data(api_key, match_id)
            # i = match_data['metadata']['participants'].index(match_data['info']['participants'][i]['puuid'])
            if match_data is None:
                print(f'match_data is None skipping match_id')
                continue
            if match_data['info']['gameMode'] != 'ARAM':
                print(f'match_id {match_id} is not an aram game and wont be inserted')
                continue
            insert_player_match_data(match_data, match_id)
            print(f'match_id {match_id} inserted into playerMatches table')



if __name__ == "__main__":
    main()