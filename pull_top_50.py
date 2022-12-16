from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from player_rating_refresh import PlayerRatingClass

top_50_players = []

url = "https://slippi.gg/leaderboards?region="
regions = ['na', 'eu', 'other']
driver = webdriver.Firefox()
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

engine_url = 'sqlite:///db.sqlite3'
player_rate = PlayerRatingClass(engine_url)
for player in top_50_players:
    player_rating_class.insert_new_rating(player[1])
