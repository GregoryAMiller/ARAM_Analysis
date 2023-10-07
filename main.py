import config
import apiCalls as ac
import psycopg2
import datetime
import time
import insert
import csv
import os

def save_lists_to_csv(summoner_file, seen_file, summoner_list, already_seen_list):
    try:
        # Save summoner_list to summoner_file
        with open(summoner_file, mode='w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row (optional)
            csv_writer.writerow(['summoner_list'])

            # Write the data from summoner_list
            csv_writer.writerows(zip(summoner_list))

        # Save already_seen_list to seen_file
        with open(seen_file, mode='w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row (optional)
            csv_writer.writerow(['already_seen_list'])

            # Write the data from already_seen_list
            csv_writer.writerows(zip(already_seen_list))

        print(f'Lists Successfully Saved to {summoner_file} and {seen_file}')
    except Exception as e:
        print(f"An error occurred while saving: {e}")

def load_lists_from_csv(summoner_file, seen_file):
    try:
        summoner_list = []
        already_seen_list = []

        # Load summoner_list from summoner_file
        with open(summoner_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                summoner_list.append(row[0])

        # Load already_seen_list from seen_file
        with open(seen_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                already_seen_list.append(row[0])

        return summoner_list, already_seen_list
    except FileNotFoundError:
        return ['Shade20'], []




def main():

    api_key = insert.read_api_key(filename = 'api_key.txt')

    # summoner_list = ['shade20']

    games_fetched = 50

    summoner_list, already_seen = load_lists_from_csv('summoners.csv', 'seen.csv')

    # print(summoner_list)

    # Start with an initial index
    index = 0

    try:

        while index < len(summoner_list):
            summoner = summoner_list[index]
            if summoner in already_seen:
                print(f'already seen {summoner}')
                index += 1
                continue
            print(f"Index: {index}, Summoner: {summoner}")
            print(f'**** LENGTH OF SUMMONER_LIST: {len(summoner_list)} *****')
            # Get the summoner's puuid 
            summoner_puuid = insert.get_player_puuid(api_key, summoner)
            # Get match history (match_ids list) using the puuid of the summoner 
            match_ids = ac.get_match_history(api_key, summoner_puuid, games_fetched)
            n = 0
            for match_id in match_ids:
                print(f"Index: {n} - match_id: {match_id}")
                n += 1
                match_data = ac.get_match_data(api_key, match_id)
                if match_data is None:
                    print(f'match_data is None, skipping match_id')
                    continue
                # if the match_id is already in the database continue
                if insert.is_match_id_exists(match_id):
                    print(f'Match id {match_id} already exists skipping to next match_id...')
                    continue
                # if the match is not a aram continue 
                if match_data['info']['gameMode'] != 'ARAM':
                    print(f'match_id {match_id} is not an ARAM game and won\'t be inserted')
                    continue

                # Insert participants in the match into summoner_list to branch into their games
                for i in range(0, 10):
                    summoner_name = match_data['info']['participants'][i]['summonerName']
                    if summoner_name not in summoner_list:
                        summoner_list.append(summoner_name)
                # Insert match data into the database
                insert.insert_player_match_data(match_data, match_id)
                print(f'match_id {match_id} inserted into playerMatches table')
            already_seen.append(summoner)

            save_lists_to_csv('summoners.csv', 'seen.csv', summoner_list, already_seen)

            # Move to the next summoner
            index += 1
        save_lists_to_csv('summoners.csv', 'seen.csv', summoner_list, already_seen)

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Saving lists.")
        save_lists_to_csv('summoners.csv', 'seen.csv', summoner_list, already_seen)

    except Exception as e:
        print(f"An error occurred: {e}")

        # Save the lists to a CSV file
        save_lists_to_csv('summoners.csv', 'seen.csv', summoner_list, already_seen)








if __name__ == "__main__":
    main()