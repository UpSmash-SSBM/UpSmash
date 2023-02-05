from datetime import datetime
import subprocess
import os
from bs4 import BeautifulSoup
import time
from selenium.webdriver.firefox.options import Options
import json
from sqlalchemy import or_
from selenium import webdriver
from multiprocessing import Process
from upsmash.models import Player, SlippiReplay, SlippiActionCounts, SlippiOverall, MeleeCharacters, SlippiReplayPlayerInfo
from upsmash import db
from upsmash.utils import create_new_player, refresh_player_rating
from upsmash import create_min_app

app = create_min_app()
app.app_context().push()

def games_get(connect_code):
    connect_code = connect_code.replace("-","#").upper()
    current_player = Player.query.filter_by(connect_code=connect_code).first()
    if not current_player:
        current_player = create_new_player(connect_code)
    if not current_player:
        return None
    played = [i for i, in SlippiReplay.query.with_entities(SlippiReplay.filename).filter(or_(SlippiReplay.player1_id== current_player.id, SlippiReplay.player2_id== current_player.id))]
    return played

def calc_ratio(count):
    total = count['success'] + count['fail']
    if total > 0:
        ratio = count['success'] / total
    else:
        ratio = None
    return ratio

def add_slippi_file_to_overall(slippi_replay, filename, players, overall):
    for player in overall:
        connect_code = players[str(player['playerIndex'])]['names']['code']
        current_player = Player.query.filter_by(connect_code=connect_code).first()
        if not current_player:
            print("Couldn't find player: " + connect_code)
            return False

        new_overall = SlippiOverall(slippi_replay_id=slippi_replay.id, player_id=current_player.id, input_counts=player['inputCounts']['total'], 
            total_damage=player['totalDamage'], kill_count=player['killCount'], successful_conversions=player['successfulConversions']['total'], 
            successful_conversion_ratio=player['successfulConversions']['ratio'], inputs_per_minute=player['inputsPerMinute']['ratio'],digital_inputs_per_minute=player['digitalInputsPerMinute']['ratio'],
            openings_per_kill=player['openingsPerKill']['ratio'], damage_per_opening=player['damagePerOpening']['ratio'], 
            neutral_win_ratio=player['neutralWinRatio']['ratio'], counter_hit_ratio=player['counterHitRatio']['ratio'], 
            beneficial_trades=player['beneficialTradeRatio']['ratio']
        )
        db.session.add(new_overall)
        db.session.commit()

def add_slippi_file_to_action_counts(slippi_replay, filename, players, action_counts):
    for player in action_counts:
        connect_code = players[str(player['playerIndex'])]['names']['code']
        current_player = Player.query.filter_by(connect_code=connect_code).first()
        if not current_player:
            print("Couldn't find player: " + connect_code)
            return False

        lcancel_ratio = calc_ratio(player['lCancelCount'])
        wall_tech_ratio = calc_ratio(player['wallTechCount'])
        
        new_action_count = SlippiActionCounts(slippi_replay_id=slippi_replay.id, player_id=current_player.id, wavedash=player['wavedashCount'], 
            waveland=player['wavelandCount'], airdodge=player['airDodgeCount'], dashdance=player['dashDanceCount'], 
            spotdodge=player['spotDodgeCount'], ledgegrab=player['ledgegrabCount'],roll=player['rollCount'],
            lcancel_success_ratio=lcancel_ratio, grab_success=player['grabCount']['success'], 
            grab_fail=player['grabCount']['fail'], tech_away=player['groundTechCount']['away'], 
            tech_in=player['groundTechCount']['in'], tech=player['groundTechCount']['neutral'],
            tech_fail=player['groundTechCount']['fail'],
            wall_tech_success_ratio=wall_tech_ratio
        )
        db.session.add(new_action_count)
        db.session.commit()

def get_player_info(setting_players):
    new_player_info = []
    for players in setting_players:
        player_character = MeleeCharacters(players['characterId'])
        player_color = players['characterColor']
        player_info = SlippiReplayPlayerInfo(character=player_character,characterColor=player_color)
        db.session.add(player_info)
        db.session.commit()
        new_player_info.append(player_info)
    return new_player_info

def load_slippi_file(filename):
    full_filename = os.path.join('upsmash/static/json/', filename + '.json')
    if not os.path.exists(full_filename):
        print("Slp file does not exist")
        return False
    with open(full_filename) as f:
        try:
            data = json.load(f)
        except:
            print("Couldn't load file: " + filename)
            return False

        settings = data['settings']
        stats = data['stats']
        metadata = data['metadata']
        players = metadata['players']
        winner = data['winner']
        winner_id = None
        setting_players = settings['players']
        match_info = settings['matchInfo']
        match_id = match_info['matchId']
        match_type = match_id.split('.')[1].split('-')[0].upper()

        new_players = []
        #print("PLAYERS: " + str(players))
        for player in players.values():
            if not 'code' in player['names'].keys():
                print("Local game file")
                return False
            connect_code = player['names']['code']
            current_player = Player.query.filter_by(connect_code=connect_code).first()
            if not current_player:
                current_player = create_new_player(connect_code)
                #print("current_player: " + str(current_player))
            current_player = Player.query.filter_by(connect_code=connect_code).first()
            if not current_player:
                print("Couldn't find player: " + connect_code)
                return False
            if connect_code == winner:
                winner_id = current_player.id
            new_players.append(current_player)
        #print("PLAYERS: " + str(new_players))
        if not SlippiReplay.query.filter_by(filename=filename,player1_id=new_players[0].id,player2_id=new_players[1].id).first(): #add test to make sure not already exists
            players_info = get_player_info(setting_players)
            
            slippi_datetime = filename[5:20]
            slp_datetime = datetime.strptime(slippi_datetime, '%Y%m%dT%H%M%S')
            #print("slippidatetime: " + slippi_datetime)
            new_slippi_replay = SlippiReplay(filename=filename,player1_id=new_players[0].id,
                player2_id=new_players[1].id, winner_id=winner_id, datetime=slp_datetime,player1_info_id=players_info[0].id,
                player2_info_id=players_info[1].id, game_type=match_type
            )
            
            db.session.add(new_slippi_replay)
            db.session.commit()
            #print("replay_id: " + str(new_slippi_replay.id))
            add_slippi_file_to_action_counts(new_slippi_replay, filename, players, stats['actionCounts'])
            add_slippi_file_to_overall(new_slippi_replay, filename, players, stats['overall'])

def load_slippi_files(filename):
    subprocess.run(["node", "../slippi_js/to_json.js",filename])
    slp_path = os.path.join('upsmash/static/files/', filename)
    os.remove(slp_path)
    base_filename = filename.split('.')[0]
    load_slippi_file(base_filename)
    json_path = os.path.join('upsmash/static/json/', base_filename + '.json')
    os.remove(json_path)

def refresh_all_ratings():
    print("Refreshing all ratings")
    players = Player.query.all()
    for player in players:
        refresh_player_rating(player)

def top_50_players_thread():
    print("Refreshing top 50 players")
    #players = get_top_50_players()
    with open('player_list.json') as f:
        players = json.load(f)
    #print(players)
    for player in players:
        #print(player)
        connect_code = player[1]
        current_player = Player.query.filter_by(connect_code=connect_code).first()
        if not current_player:
                current_player = create_new_player(connect_code)

def get_top_50_players():
    top_50_players = []
    url = "https://slippi.gg/leaderboards?region="
    regions = ['na', 'eu', 'other']
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    for region in regions:
        driver.get(url + region)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find("table").find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            player_name = cells[2].find("a").get_text()
            player_tag = cells[2].find("p").get_text()
            top_50_players.append((player_name, player_tag))
    driver.close()
    return top_50_players

def upload(request):
    files = request.files
    for new_file in files.values():
        filename = new_file.filename
        new_file.save(os.path.join('upsmash/static/files/', filename))
        #load_slippi_files(filename)
        proc = Process(target=load_slippi_files, args=(filename,))
        proc.start()
    return 'Processing files'
