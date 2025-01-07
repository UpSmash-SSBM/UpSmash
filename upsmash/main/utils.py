from datetime import datetime
import subprocess
import os
from bs4 import BeautifulSoup
import time
import json
from sqlalchemy import or_
from multiprocessing import Process
from upsmash.models import Player, SlippiReplay, SlippiActionCounts, SlippiOverall, MeleeCharacters, SlippiReplayPlayerInfo, StageID
from upsmash import db
from upsmash.utils import create_new_player, refresh_player_rating
from upsmash import create_min_app
from upsmash.config import Config
from boto3 import session as BotoSession
import zipfile

app = create_min_app()
app.app_context().push()

def games_get(connect_code):
    connect_code = connect_code.replace("-","#").upper()
    current_player = Player.query.filter_by(connect_code=connect_code).first()
    if not current_player:
        current_player = create_new_player(connect_code)
    if not current_player:
        return None
    played = [i for i, in SlippiReplay.query.with_entities(SlippiReplay.filename).filter(SlippiReplay.player1_id== current_player.id | SlippiReplay.player2_id== current_player.id)]
    return played

def calc_ratio(count):
    total = count['success'] + count['fail']
    if total > 0:
        ratio = count['success'] / total
    else:
        ratio = None
    return ratio

def upload_slippi_file_to_s3(local_filename, upload_filename):
    session = BotoSession.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url=Config.S3_BUCKET,
                            aws_access_key_id=Config.S3_ACCESS,
                            aws_secret_access_key=Config.S3_PRIVATE)
    client.upload_file(local_filename, 'slippifiles', upload_filename)

def create_zip_file(local_filename, game_filename):
    archive_directory = 'upsmash/static/archive_files/'
    zip_filename = archive_directory + game_filename + '.zip'
    with zipfile.ZipFile(zip_filename,'w', zipfile.ZIP_DEFLATED) as zip:
        zip.write(local_filename, arcname = game_filename)

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
        new_player_info.append(player_info.id)
    return new_player_info

def load_slippi_file(filename):
    full_filename = os.path.join('upsmash/static/json/', filename + '.json')
    if not os.path.exists(full_filename):
        print("Slp json file does not exist")
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
        try:
            players = metadata['players']
        except:
            print("Couldn't get players")
            return None
        winner = data['winner']
        winner_id = None
        setting_players = settings['players']
        match_info = settings['matchInfo']
        match_id = match_info['matchId']
        if match_id:
            match_type = match_id.split('.')[1].split('-')[0].upper()
        else:
            match_type = None
        stage_id = StageID(settings['stageId'])

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
            new_players.append(current_player.id)
        #print("PLAYERS: " + str(new_players))
        if not SlippiReplay.query.filter_by(filename=filename,player1_id=new_players[0],player2_id=new_players[1]).first(): #add test to make sure not already exists
            players_info = get_player_info(setting_players)
            
            slippi_datetime = filename[5:20]
            slp_datetime = datetime.strptime(slippi_datetime, '%Y%m%dT%H%M%S')
            #print("slippidatetime: " + slippi_datetime)
            new_slippi_replay = SlippiReplay(filename=filename,player1_id=new_players[0],
                player2_id=new_players[1], winner_id=winner_id, datetime=slp_datetime,player1_info_id=players_info[0],
                player2_info_id=players_info[1], game_type=match_type, stage_id=stage_id
            )
            
            db.session.add(new_slippi_replay)
            db.session.commit()
            #print("replay_id: " + str(new_slippi_replay.id))
            add_slippi_file_to_action_counts(new_slippi_replay, filename, players, stats['actionCounts'])
            add_slippi_file_to_overall(new_slippi_replay, filename, players, stats['overall'])

def load_slippi_files(filename):
    archive_directory = 'upsmash/static/archive_files/'
    zip_filename = archive_directory + filename + '.zip'
    subprocess.run(["node", "to_json.js",filename])
    slp_path = os.path.join('upsmash/static/files/', filename)
#    create_zip_file(slp_path, filename)
    if os.path.exists(slp_path):
        os.remove(slp_path)
#    upload_slippi_file_to_s3(zip_filename, filename + '.zip')
#    os.remove(zip_filename)
    base_filename = filename.split('.')[0]
    load_slippi_file(base_filename)
    json_path = os.path.join('upsmash/static/json/', base_filename + '.json')
    if os.path.exists(json_path):
        os.remove(json_path)

def refresh_all_ratings():
    print("Refreshing all ratings")
    players = Player.query.all()
    for player in players:
        refresh_player_rating(player)

def upload(request):
    files = request.files
    for new_file_key, new_file_value in files.items(True):
        filename = new_file_value.filename
        new_file_value.save(os.path.join('upsmash/static/files/', filename))
        load_slippi_files(filename)
        #proc = Process(target=load_slippi_files, args=(filename,))
        #proc.start()
    return 'Processing files'
