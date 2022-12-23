import requests
import shutil

icons = {
    "Unranked 1": "static/media/rank_Unranked1.89c1471dd8339b016d5b5091dc95327b.svg",
    "Unranked 2": "static/media/rank_Unranked2.32b756ecd0fb212d8ef93f22aa544813.svg",
    "Unranked 3": "static/media/rank_Unranked3.3d00d9f8b63cb7f9f28da1178ceb92c1.svg",
    "Bronze 1": "static/media/rank_Bronze_I.f4a5615366a7162c5cbe84a8fe3e3b72.svg",
    "Bronze 2": "static/media/rank_Bronze_II.ca1b9f3828159e0d2c14f42e5c336ec2.svg",
    "Bronze 3": "static/media/rank_Bronze_III.926dad245cc35e515006cdb08eedff70.svg",
    "Silver 1": "static/media/rank_Silver_I.b694a8fcee43995f9d8eacdb1cdd283b.svg",
    "Silver 2": "static/media/rank_Silver_II.80d78884f7e217605cecc8d085ff66ab.svg",
    "Silver 3": "static/media/rank_Silver_III.f055e41201f92706363485184b01a7f1.svg",
    "Gold 1": "static/media/rank_Gold_I.dbf30bb06579441db83a84359c9f7f7c.svg",
    "Gold 2": "static/media/rank_Gold_II.010eefcf4ef6535f0573e4c57e1d2bc5.svg",
    "Gold 3": "static/media/rank_Gold_III.335dd121b2978c869f1659f737336986.svg",
    "Platinum 1": "static/media/rank_Platinum_I.e788a14a6315286f8d411c52464e8dae.svg",
    "Platinum 2": "static/media/rank_Platinum_II.b3ff4dc16ac5e17e9357244a33a63f36.svg",
    "Platinum 3": "static/media/rank_Platinum_III.9dbea1040fee6c9d2501eac47485bcd6.svg",
    "Diamond 1": "static/media/rank_Diamond_I.3758158f3ad9a215311e6eb2dc968226.svg",
    "Diamond 2": "static/media/rank_Diamond_II.0f605ef22468b0fdc81cd5815353ec51.svg",
    "Diamond 3": "static/media/rank_Diamond_III.fb1783af36e8a03b5ecd22ae80495bf6.svg",
    "Master 1": "static/media/rank_Master_I.671b49b542024fc932524d6ed8e4a37f.svg",
    "Master 2": "static/media/rank_Master_II.28571e465043a2524d6a8ad6cfaf224e.svg",
    "Master 3": "static/media/rank_Master_III.5485903c6f464d65bb8d3d529d3ab21e.svg",
    "Grandmaster": "static/media/rank_Grand_Master.ee2c75e98fe1d2f075cbff29587563bb.svg"
}

url = 'https://slippi.gg/'

for key,value in icons.items():
    full_url = url + value
    response = requests.get(full_url, stream=True)
    file_name = 'static/images/ranks/' + value.split('/')[2].split('.')[0] + '.png'
    with open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)