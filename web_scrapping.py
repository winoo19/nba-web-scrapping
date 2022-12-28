import requests
from bs4 import BeautifulSoup


def get_page():
    return requests.get("https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/").text

def parse_html(html):
    html = BeautifulSoup(html, "html.parser")
    return html.find_all("div", {"class": "cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative"})


if __name__ == "__main__":
    html = get_page()
    odds = parse_html(html)

    done = False
    while not done:
        team_odds = []
        for i, div in enumerate(odds):
            print(f"{i}. {div.find('a').text.strip()}")

        ans = input(f"\nInput the number of the desired game: ")
        try:
            team_odds = odds[int(ans)]
        except:
            done = True
            continue

        home_team_quota, away_team_quota = team_odds.find_all("span", {"class": "px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base"})
        print(f"\nThe quota for the game {team_odds.find('a').text.strip()} is {home_team_quota.text} - {away_team_quota.text}\n")

        ans = input("Do you want to look for the quota of a different game? (y/n): ")
        if ans.lower() != "y":
            done = True
        else:
            print("\n\n")
