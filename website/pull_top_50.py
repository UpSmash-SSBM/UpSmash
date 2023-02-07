from upsmash import create_full_app
from upsmash.utils import get_or_create_player
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import json
import os

app = create_full_app()

file_output = 'top_50_players.json'
if not os.path.exists(file_output):
    top_50_players = []
    engine_url = ['sqlite:///db.sqlite3']
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

    print(json.dumps(top_50_players))
else:
    with open(file_output) as player_file:
        top_50_players = json.load(player_file)
        for player in top_50_players:
            print(player[1])
            get_or_create_player(player[1])
