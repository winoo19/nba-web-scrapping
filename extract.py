import requests
import json
import os
import plotly.express as px
from PyPDF2 import PdfMerger


def get_team_info(season: int) -> list[dict]:
    r = requests.get(f"https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/{season}?key=d1b036faeb9e4c608b40a8a57d38d569")
    return r.json()


def get_player_info():
    r = requests.get(f"https://api.sportsdata.io/v3/nba/scores/json/Players/tor?key=d1b036faeb9e4c608b40a8a57d38d569")
    return r.json()


def parse_data(data: list[dict], keys) -> dict:
    data = {" ".join(element[key] for key in keys): element for element in data}
    return data


if __name__ == "__main__":

    if not os.path.exists("data"):
        os.mkdir("data")
    
    if not os.path.exists("pdfs"):
        os.mkdir("pdfs")

    season = 2023
    if not os.path.exists(f"data/raptors_{season}.json"):
        team_data = get_team_info(season)
        with open(f"data/raptors_{season}.json", "w") as f:
            json.dump(team_data, f)
    else:
        with open(f"data/raptors_{season}.json", "r") as f:
            team_data = json.load(f)

    if not os.path.exists(f"data/raptor_players.json"):
        players = get_player_info()
        with open(f"data/raptor_players.json", "w") as f:
            json.dump(players, f)
    else:
        with open(f"data/raptor_players.json", "r") as f:
            players = json.load(f)

    team_data = parse_data(team_data, ["Name"])["Toronto Raptors"]
    players = parse_data(players, ["FirstName", "LastName"])
    # print(sorted(
    #     players.keys(),
    #     key=lambda p: players[p]["Salary"] if players[p]["Salary"] else 0,
    #     reverse=True
    #     ))

    twos, twos_att = team_data["TwoPointersMade"], team_data["TwoPointersAttempted"]
    threes, threes_att = team_data["ThreePointersMade"], team_data["ThreePointersAttempted"]
    ft, ft_att = team_data["FreeThrowsMade"], team_data["FreeThrowsAttempted"]

    wins_v_loses = px.bar(x=["Wins", "Loses"], y=[team_data["Wins"], team_data["Losses"]], title="Wins vs losses")
    shots = px.bar(
        x=["two pointers", "three pointers", "free throws"],
        y=[
            [twos, threes, ft],
            [twos_att-twos, threes_att-threes, ft_att-ft]
            ],
        title="Shot accuracy"
    )
    defensive_stats = px.bar(
        x=["DefensiveRebounds", "Steals", "BlockedShots", "PlusMinus"],
        y=[
            team_data["DefensiveRebounds"],
            team_data["Steals"],
            team_data["BlockedShots"],
            team_data["PlusMinus"]
            ],
        title="Defensive stats"
    )
    offensive_stats = px.bar(
        x=["Possessions", "OffensiveRebounds", "Assists", "Turnovers"],
        y=[
            team_data["Possessions"],
            team_data["OffensiveRebounds"],
            team_data["Assists"],
            team_data["Turnovers"]
            ],
        title="Offensive stats"
    )

    graphs = [
        wins_v_loses,
        shots,
        defensive_stats,
        offensive_stats
        ]

    static_report = ''
    for i, graph_url in enumerate(graphs):

        graph_url.write_image(f"pdfs/{i}.pdf")
    
    merger = PdfMerger()

    for i in range(len(graphs)):
        merger.append(f"pdfs/{i}.pdf")

    merger.write("pdfs/report.pdf")
    merger.close()
