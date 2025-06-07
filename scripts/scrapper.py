import requests
from bs4 import BeautifulSoup
import csv
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
PARAMS = {
    "land_id": "0",
    "ausrichtung": "alle",
    "spielerposition_id": "alle",
    "altersklasse": "alle",
    "jahrgang": "0",
    "kontinent_id": "0",
    "plus": "1"
}

def get_soup(url, params=None):
    for _ in range(3):
        try:
            res = requests.get(url, headers=HEADERS, params=params)
            res.raise_for_status()
            return BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            time.sleep(2)
    return None

def parse_players_table(soup, starting_id):
    players = []
    table = soup.find("table", {"class": "items"})
    if not table:
        print("⚠️ Players table not found")
        return players, starting_id

    rows = table.find_all("tr", {"class": ["odd", "even"]})
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 14:
            continue

        player_name = cols[1].find("a", {"class": "spielprofil_tooltip"})
        player_name = player_name.text.strip() if player_name else ""

        position = cols[4].text.strip()
        age = cols[5].text.strip()

        nationality_img = cols[2].find_all("img")
        nationality = ", ".join([img.get("title", "") for img in nationality_img])

        club_img = cols[3].find("img")
        club = club_img.get("alt", "") if club_img else ""

        market_value = cols[6].text.strip()
        matches_played = cols[7].text.strip()
        goals = cols[8].text.strip()
        own_goals = cols[9].text.strip()
        assists = cols[10].text.strip()
        yellow_cards = cols[11].text.strip()
        double_yellow_cards = cols[12].text.strip()
        red_cards = cols[13].text.strip()

        player = {
            "ID": starting_id,
            "Player": player_name,
            "Position": position,
            "Age": age,
            "Nationality": nationality,
            "Club": club,
            "MarketValue": market_value,
            "MatchesPlayed": matches_played,
            "Goals": goals,
            "OwnGoals": own_goals,
            "Assists": assists,
            "YellowCards": yellow_cards,
            "DoubleYellowCards": double_yellow_cards,
            "RedCards": red_cards,
        }

        players.append(player)
        starting_id += 1

    return players, starting_id

def scrape_players(pages=1):
    all_players = []
    current_id = 1
    for page in range(1, pages + 1):
        print(f"📄 Scraping page {page}...")
        params = PARAMS.copy()
        params["page"] = page

        soup = get_soup(BASE_URL, params)
        if not soup:
            print(f"❌ Failed to retrieve page {page}")
            continue

        players_on_page, current_id = parse_players_table(soup, current_id)
        all_players.extend(players_on_page)

        print(f" Extracted {len(players_on_page)} players from page {page}")
        time.sleep(2)
    return all_players

def save_to_csv(players, filename="transfermarkt_players.csv"):
    keys = [
        "ID", "Player", "Position", "Age", "Nationality", "Club",
        "MarketValue", "MatchesPlayed", "Goals", "OwnGoals",
        "Assists", "YellowCards", "DoubleYellowCards", "RedCards"
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(players)
    print(f" Saved {len(players)} players to {filename}")

def main():
    pages_to_scrape = 20  # You can change this as needed
    players = scrape_players(pages=pages_to_scrape)
    save_to_csv(players)

if __name__ == "__main__":
    main()



# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# url = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
# headers = {"User-Agent": "Mozilla/5.0"}
# params = {
#     "land_id": "0",
#     "ausrichtung": "alle",
#     "spielerposition_id": "alle",
#     "altersklasse": "alle",
#     "jahrgang": "0",
#     "kontinent_id": "0",
#     "plus": "1"
# }

# response = requests.get(url, headers=headers, params=params)
# soup = BeautifulSoup(response.text, "html.parser")
# table = soup.find("table", class_="items")
# rows = table.find("tbody").find_all("tr")

# players = []
# player_id = 1

# for idx, row in enumerate(rows):
#     cols = row.find_all("td")
    
#     if len(cols) < 13:
#         # print(f"Skipping row {idx} due to insufficient columns")
#         continue

#     # Extract player name and position from nested table inside second <td>
#     player_name = None
#     position = None

#     player_cell = cols[1]
#     nested_table = player_cell.find("table")
#     if nested_table:
#         trs = nested_table.find_all("tr")
#         if len(trs) >= 1:
#             a_tag = trs[0].find("a")
#             if a_tag:
#                 player_name = a_tag.get_text(strip=True)
#         if len(trs) >= 2:
#             position = trs[1].get_text(strip=True)
#     else:
#         a_tag = player_cell.find("a")
#         if a_tag:
#             player_name = a_tag.get_text(strip=True)

   
#     if not player_name:

#         continue

#     # Extract rest of columns safely
#     age = cols[2].get_text(strip=True)
#     nationality = cols[3].img['title'] if cols[3].find("img") else ''
#     club = cols[4].img['alt'] if cols[4].find("img") else ''
#     market_value = cols[5].get_text(strip=True)
#     matches = cols[6].get_text(strip=True)
#     goals = cols[7].get_text(strip=True)
#     own_goals = cols[8].get_text(strip=True)
#     assists = cols[9].get_text(strip=True)
#     yellow_cards = cols[10].get_text(strip=True)
#     double_yellows = cols[11].get_text(strip=True)
#     red_cards = cols[12].get_text(strip=True)

#     players.append({
#         "ID": str(player_id),
#         "Player": player_name,
#         "Position": position if position else "",
#         "Age": age,
#         "Nationality": nationality,
#         "Club": club,
#         "MarketValue": market_value,
#         "MatchesPlayed": matches,
#         "Goals": goals,
#         "OwnGoals": own_goals,
#         "Assists": assists,
#         "YellowCards": yellow_cards,
#         "DoubleYellowCards": double_yellows,
#         "RedCards": red_cards
#     })
#     player_id += 1

# df = pd.DataFrame(players)
# print(df.head(10))
