import json
import pandas as pd
import numpy as np


def convert_json_to_dataframe(file_path):
    valid_json = []
    invalid_json = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                json_obj = json.loads(line)
                valid_json.append(json_obj)
            except json.JSONDecodeError as e:
                print(f"Skipping line due to JSONDecodeError: {e}")
                invalid_json.append(line)         
    df_valid_json = pd.DataFrame(valid_json)
    df_valid_json = df_valid_json.iloc[1:]
    df_invalid_json = pd.DataFrame(invalid_json)
    
    return df_valid_json, df_invalid_json   


def flatten_dict(data, parent_key="", sep="_"):
    items = []
    if data is None:
        return {}
    if not isinstance(data, dict):
        return {parent_key: data} if parent_key else {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def normalize_nested_dataframes(dataframe):
    nested_data = {}
    flat_data = dataframe.copy()
    flat_data['load_date'] = pd.Timestamp.now()  
    for col in flat_data.columns:
        if flat_data[col].apply(lambda x: isinstance(x, (dict, list))).any():
            #print(flat_data[col].head())
            if flat_data[col].apply(lambda x: isinstance(x, dict)).any():
                #print('nested document is a dictionary')
                nested_data[col] = pd.DataFrame(flat_data[col].apply(lambda x: flatten_dict(x) if isinstance(x, dict) else {}).tolist(), index=flat_data.index)
                nested_data[col].reset_index(inplace=True)
                nested_data[col].rename(columns={"index": "ID"}, inplace=True)
                flat_data[col + '_fk'] = flat_data.index
                flat_data = flat_data.drop(columns=[col])
            elif flat_data[col].apply(lambda x: isinstance(x, list)).any():
                #print('nested document is a list')
                flat_data_copy = flat_data.copy()
                flat_data_copy = flat_data_copy.explode(col)
                nested_data[col] = pd.DataFrame(flat_data_copy[col].apply(lambda x: flatten_dict(x) if isinstance(x, dict) else {}).tolist(), 
                                                index=flat_data_copy.index)
                nested_data[col].reset_index(inplace=True)
                nested_data[col].rename(columns={"index": "ID"}, inplace=True)
                flat_data[col + '_fk'] = flat_data.index
                flat_data = flat_data.drop(columns=[col])
                flat_data_copy = ''
    return nested_data, flat_data


def extract_data_for_dashboard(file_path):
    df_valid_json, df_invalid_json = convert_json_to_dataframe(file_path)
    nested_data, flat_data = normalize_nested_dataframes(df_valid_json)
    df_home_players = nested_data['homePlayers']
    df_home_players['Team'] = 'home'
    df_away_players = nested_data['awayPlayers']
    df_away_players['Team'] = 'away'
    df_balls = nested_data['balls']
    df_balls['Team'] = 'ball'
    df_home_players = pd.merge(df_home_players, flat_data, how='left', left_on='ID', right_on='homePlayers_fk')
    df_away_players = pd.merge(df_away_players, flat_data, how='left', left_on='ID', right_on='awayPlayers_fk')
    df_balls = pd.merge(df_balls, flat_data, how='left', left_on='ID', right_on='balls_fk')

    columns_to_union = ['ID','Team','jerseyNum','x','y','speed','videoTimeMs','frameNum','period','periodElapsedTime','periodGameClockTime']
    columns_for_ball = ['ID','Team','x','y','videoTimeMs','frameNum','period','periodElapsedTime','periodGameClockTime']
    df_home_players_selected = df_home_players[columns_to_union]
    df_away_players_selected = df_away_players[columns_to_union]
    df_balls_selected = df_balls[columns_for_ball]
    final_data = pd.concat([df_home_players_selected, df_away_players_selected, df_balls_selected], axis=0, ignore_index=True)
    final_data = final_data.sort_values(by='periodGameClockTime')
    minutes, seconds = divmod(final_data['periodGameClockTime'].astype(int), 60)
    final_data['game_clock'] = minutes.astype(str).str.zfill(2) + ':' + seconds.astype(str).str.zfill(2)
    final_data['game_min'] = minutes.astype(str).str.zfill(2)
    final_data['time_batch'] = np.ceil(minutes/10).astype(int)
    final_data['combined_frame'] = final_data['game_clock'].astype(str) + '-' + final_data['frameNum'].astype(str)
    return final_data

file_path = r"C:/Users/Emmanuel.Agholor/Documents/football positions proj/game_tracks.json"
final_data = extract_data_for_dashboard(file_path)
df = final_data.sort_values(by='game_clock').head(1000))
final_data_path = r"C:\Users\Emmanuel.Agholor\Documents\football positions proj\final_data.csv"
final_data_path2 = r"C:\Users\Emmanuel.Agholor\Documents\football positions proj\tracking_data.csv"
final_data.to_csv(final_data_path, index=False)
df.to_csv(final_data_path, index=False)