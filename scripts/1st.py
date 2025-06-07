import requests
from bs4 import BeautifulSoup
import time
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def get_soup(url):
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

def scrape_profile_stats(profile_url):
    soup = get_soup(profile_url)
    stats = {
        "MatchesPlayed": "", "Goals": "", "OwnGoals": "", "Assists": "",
        "YellowCards": "", "DoubleYellowCards": "", "RedCards": ""
    }

    if not soup:
        return stats

    try:
        stat_table = soup.select_one('div.large-6.columns > .profilheader')
        boxes = soup.select('.quick-facts > div.dataZusatzbox')
        for box in boxes:
            label = box.find("span", class_="data-label")
            value = box.find("span", class_="data-value")
            if label and value:
                label_text = label.text.strip().lower()
                value_text = value.text.strip()
                if "appearances" in label_text:
                    stats["MatchesPlayed"] = value_text
                elif "goals" in label_text and "own" not in label_text:
                    stats["Goals"] = value_text
                elif "own goals" in label_text:
                    stats["OwnGoals"] = value_text
                elif "assists" in label_text:
                    stats["Assists"] = value_text
                elif "yellow cards" in label_text and "second" not in label_text:
                    stats["YellowCards"] = value_text
                elif "second yellow" in label_text:
                    stats["DoubleYellowCards"] = value_text
                elif "red cards" in label_text:
                    stats["RedCards"] = value_text
    except Exception as e:
        print(f"Error parsing stats from profile {profile_url}: {e}")

    return stats

def scrape_player_data_from_url(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    players_data = []
    rows = soup.select("table.items > tbody > tr")

    for i, row in enumerate(rows):
        cols = row.find_all("td")
        if len(cols) != 9:
            continue

        try:
            player_data = {
                "ID": cols[0].text.strip(),
                "Player": "",
                "Position": "",
                "Age": cols[5].text.strip(),
                "Nationality": "",
                "Club": "",
                "MarketValue": cols[8].text.strip(),
                "MatchesPlayed": "",
                "Goals": "",
                "OwnGoals": "",
                "Assists": "",
                "YellowCards": "",
                "DoubleYellowCards": "",
                "RedCards": ""
            }

            player_info_table = cols[1].find("table", class_="inline-table")
            if player_info_table:
                name_link_tag = player_info_table.select_one("td.hauptlink > a")
                if name_link_tag:
                    player_data["Player"] = name_link_tag.text.strip()
                    profile_relative_url = name_link_tag.get('href', '')
                    profile_url = "https://www.transfermarkt.com" + profile_relative_url
                    stats = scrape_profile_stats(profile_url)
                    player_data.update(stats)

                # Position
                position_row = player_info_table.find_all("tr")
                if len(position_row) > 1:
                    pos_td = position_row[1].find("td")
                    if pos_td:
                        player_data["Position"] = pos_td.text.strip()

            nationality_imgs = cols[6].find_all("img", class_="flaggenrahmen")
            player_data["Nationality"] = ", ".join(img["title"] for img in nationality_imgs if img.has_attr("title"))

            club_tag = cols[7].find("a", title=True)
            player_data["Club"] = club_tag["title"] if club_tag else ""

            players_data.append(player_data)

        except Exception as e:
            print(f"Error parsing player row {i+1}: {e}")
            continue

    return players_data

def get_all_player_data(base_url, num_pages=1):
    all_players = []

    for page_num in range(1, num_pages + 1):
        url = f"{base_url}?page={page_num}"
        print(f"\nFetching page {page_num}: {url}")
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            html_content = res.text
            players_on_page = scrape_player_data_from_url(html_content)
            print(f"Scraped {len(players_on_page)} players from page {page_num}")
            all_players.extend(players_on_page)
            time.sleep(2)
        except Exception as e:
            print(f"Failed to fetch page {page_num}: {e}")
            break

    return all_players

# --- Main Execution ---
base_url = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
num_pages_to_scrape = 20

print("Starting scraping...")
final_player_data = get_all_player_data(base_url, num_pages_to_scrape)
print(f"\nDone. Total players scraped: {len(final_player_data)}")

# Save to CSV
if final_player_data:
    keys = final_player_data[0].keys()
    with open('players_data_full.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(final_player_data)
    print("Data saved to players_data_full.csv")
else:
    print("No data scraped.")




# import requests
# from bs4 import BeautifulSoup
# import time # To add a small delay between requests

# def scrape_player_data_from_url(html_content):
#     """
#     Scrapes player data from the provided HTML content of a Transfermarkt page.
#     Adjusted for the live Transfermarkt.com 'Most Valuable Players' column structure.
#     This page DOES NOT contain MatchPlayed, Goals, etc. stats.
#     """
#     soup = BeautifulSoup(html_content, "html.parser")
#     players_data = []
#     rows = soup.select("table.items > tbody > tr")

#     if not rows:
#         print("No player rows found. Check the table selector or HTML content.")
#         return players_data

#     for i, row in enumerate(rows):
#         cols = row.find_all("td")

#         # Skip rows that are not player data rows (e.g., table headers, sub-sections)
#         # A valid player row on this page has 9 td elements.
#         if len(cols) != 9:
#             # print(f"Skipping row {i+1} due to unexpected number of columns ({len(cols)}). Expected 9.")
#             continue

#         player_data = {
#             "ID": "",
#             "Player": "",
#             "Position": "",
#             "Age": "",
#             "Nationality": "",
#             "Club": "",
#             "MarketValue": "",
#             "ProfileURL": ""
#             # Removed Keys for MatchesPlayed, Goals, OwnGoals, Assists, Cards, SubIn/Out
#             # as they are not present on this specific Transfermarkt page's table.
#         }

#         try:
#             # ID: Always cols[0] for rank
#             player_data["ID"] = cols[0].text.strip()

#             # Player Name & Profile URL: Nested within cols[1] -> table -> tr -> td.hauptlink
#             # And Position: Nested within cols[1] -> table -> tr[1] -> td
#             player_info_table = cols[1].find("table", class_="inline-table")
#             if player_info_table:
#                 # Player Name and URL
#                 name_link_tag = player_info_table.select_one("td.hauptlink > a")
#                 if name_link_tag:
#                     player_data["Player"] = name_link_tag.text.strip()
#                     profile_url = name_link_tag.get('href', '')
#                     if profile_url and not profile_url.startswith('http'):
#                         player_data["ProfileURL"] = "https://www.transfermarkt.com" + profile_url

#                 # Position (second row of the inline table)
#                 position_row = player_info_table.find_all("tr")
#                 if len(position_row) > 1: # Check if the second <tr> exists
#                     position_td = position_row[1].find("td")
#                     if position_td:
#                         player_data["Position"] = position_td.text.strip()

#             # Age: In cols[5] (after ID, player/position complex, and 3 redundant image/name/pos tds)
#             player_data["Age"] = cols[5].text.strip()

#             # Nationality: In cols[6]
#             nationality_images = cols[6].find_all("img", class_="flaggenrahmen")
#             nationalities = [img['title'] for img in nationality_images if img.has_attr('title')]
#             player_data["Nationality"] = ", ".join(nationalities) if nationalities else ""

#             # Club: In cols[7]
#             club_link = cols[7].find("a", title=True)
#             if club_link:
#                 player_data["Club"] = club_link['title']

#             # Market Value: In cols[8]
#             player_data["MarketValue"] = cols[8].text.strip()

#             players_data.append(player_data)

#         except Exception as e:
#             print(f"ERROR: Could not parse row {i+1} due to: {e}")
#             # print(f"Problematic row HTML (first 500 chars): {str(row)[:500]}...\n")
#             continue # Continue to the next row even if one fails

#     return players_data

# def get_all_player_data(base_url, num_pages=1):
#     """
#     Fetches and scrapes player data across multiple pages.
#     """
#     all_players = []
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     } # Important for avoiding 403 Forbidden errors

#     for page_num in range(1, num_pages + 1):
#         url = f"{base_url}?page={page_num}"
#         print(f"Fetching data from: {url}")
#         try:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
#             html_content = response.text
#             players_on_page = scrape_player_data_from_url(html_content)
#             all_players.extend(players_on_page)
#             print(f"Successfully scraped {len(players_on_page)} players from page {page_num}.")
#             time.sleep(2) # Be polite and avoid overwhelming the server
#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching page {page_num}: {e}")
#             break # Stop if a page cannot be fetched
#         except Exception as e:
#             print(f"An unexpected error occurred while processing page {page_num}: {e}")
#             break

#     return all_players

# # --- Main Execution ---
# base_url = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
# num_pages_to_scrape = 20 # Set back to 1 page for focused testing, change to 3 or more for full data

# print("Starting to scrape player data...")
# final_player_data = get_all_player_data(base_url, num_pages_to_scrape)

# print(f"\n--- Scraping Complete: Total {len(final_player_data)} Players Extracted ---")
# for player in final_player_data:
#     print(player)
    
# import csv

# # Assuming final_player_data is a list of dictionaries
# if final_player_data:
#     keys = final_player_data[0].keys()  # Get CSV header from dict keys

#     with open('players_data.csv', 'w', newline='', encoding='utf-8') as output_file:
#         dict_writer = csv.DictWriter(output_file, fieldnames=keys)
#         dict_writer.writeheader()
#         dict_writer.writerows(final_player_data)

#     print("Data saved to players_data.csv")
# else:
#     print("No data to save.")

    
