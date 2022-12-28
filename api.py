import requests
import json
import os
import plotly.express as px
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

KEY = None


def get_team_info(season: int, key) -> list[dict]:
    r = requests.get(f"https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/{season}?key={key}")
    return r.json()


def get_player_info(season, team, key):
    r = requests.get(f"https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/{season}/{team}?key={key}")
    return r.json()


def parse_data(data: list[dict], key) -> dict:
    data = {element[key]: element for element in data}
    return data


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")
    
    if not os.path.exists("output"):
        os.mkdir("output")


    season = 2023
    team = "TOR"
    if not os.path.exists(f"data/raptors_{season}.json"):
        team_data = get_team_info(season, KEY)
        with open(f"data/raptors_{season}.json", "w") as f:
            json.dump(team_data, f)
    else:
        with open(f"data/raptors_{season}.json", "r") as f:
            team_data = json.load(f)

    if not os.path.exists(f"data/raptor_players.json"):
        players = get_player_info(season, team, KEY)
        with open(f"data/raptor_players.json", "w") as f:
            json.dump(players, f)
    else:
        with open(f"data/raptor_players.json", "r") as f:
            players = json.load(f)


    team_data = parse_data(team_data, "Name")["Toronto Raptors"]
    players = parse_data(players, "Name")


    twos, twos_att = team_data["TwoPointersMade"], team_data["TwoPointersAttempted"]
    threes, threes_att = team_data["ThreePointersMade"], team_data["ThreePointersAttempted"]
    ft, ft_att = team_data["FreeThrowsMade"], team_data["FreeThrowsAttempted"]

    df = pd.DataFrame({
        "Points": [twos, twos_att-twos, threes, threes_att-threes, ft, ft_att-ft],
        "Type of shot": ["two", "two", "three", "three", "ft", "ft"],
        "legend": ["made", "missed", "made", "missed", "made", "missed"]
        })

    shots = px.bar(
        df,
        x="Type of shot",
        y="Points",
        color="legend",
        title="Shot accuracy",
        height=400
    )

    shots.write_image("output/graph.png")


    # Chart
    df_players = pd.DataFrame(players).T[[
        "Name", 'Position', 'Games', 'Minutes', 'FieldGoalsPercentage',
        'ThreePointersPercentage', 'FreeThrowsPercentage', 'Rebounds',
        'Assists', 'Steals', 'BlockedShots', 'Turnovers', 'Points',
        'TrueShootingPercentage', 'PlayerEfficiencyRating', 'PlusMinus'
        ]].rename(columns={
        "Games": "G",
        "Assists": "AST",
        "Minutes": "MIN",
        'Position': "POS",
        'FieldGoalsPercentage': "FG%",
        'ThreePointersPercentage': "3p%",
        'FreeThrowsPercentage': "FT%",
        'Rebounds': "REB",
        'Steals': "STL",
        'BlockedShots': "BLK",
        'Turnovers': "TO",
        'Points': "PTS",
        'TrueShootingPercentage': "TS%",
        'PlayerEfficiencyRating': "PER",
        'PlusMinus': "+/-"
        })
    
    df_players_pg = df_players.copy()
    df_players_pg["AST"] = df_players_pg.apply(lambda row: round(row["AST"]/row["G"], ndigits=2), axis=1)
    df_players_pg["MIN"] = df_players_pg.apply(lambda row: round(row["MIN"]/row["G"], ndigits=2), axis=1)
    df_players_pg["REB"] = df_players_pg.apply(lambda row: round(row["REB"]/row["G"], ndigits=2), axis=1)
    df_players_pg["STL"] = df_players_pg.apply(lambda row: round(row["STL"]/row["G"], ndigits=2), axis=1)
    df_players_pg["BLK"] = df_players_pg.apply(lambda row: round(row["BLK"]/row["G"], ndigits=2), axis=1)
    df_players_pg["TO"] = df_players_pg.apply(lambda row: round(row["TO"]/row["G"], ndigits=2), axis=1)
    df_players_pg["PTS"] = df_players_pg.apply(lambda row: round(row["PTS"]/row["G"], ndigits=2), axis=1)
    df_players_pg["PER"] = df_players_pg.apply(lambda row: round(row["PER"]/row["G"], ndigits=2), axis=1)
    df_players_pg["+/-"] = df_players_pg.apply(lambda row: round(row["+/-"]/row["G"], ndigits=2), axis=1)

    _, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    tabla_png = ax.table(cellText=df_players.values, colLabels=df_players.columns, loc='center')
    tabla_png.auto_set_font_size(False)
    tabla_png.set_fontsize(10)
    tabla_png.auto_set_column_width(col=list(range(len(df_players.columns))))
    plt.savefig("output/player_stats.png")

    _, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    tabla_png = ax.table(cellText=df_players_pg.values, colLabels=df_players_pg.columns, loc='center')
    tabla_png.auto_set_font_size(False)
    tabla_png.set_fontsize(10)
    tabla_png.auto_set_column_width(col=list(range(len(df_players_pg.columns))))
    plt.savefig("output/player_stats_pg.png")


    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(left=0, top=6)
    pdf.set_font("Helvetica")
    pdf.multi_cell(txt=f"Data analysis of {team} in season {season}\n", align="C", w=0)
    pdf.multi_cell(txt="\t\t\t\x95 Player stats:\n", w=0)
    pdf.image("output/player_stats.png", w=200)
    pdf.multi_cell(txt="\t\t\t\x95 Player stats per game:\n", w=0)
    pdf.image("output/player_stats_pg.png", w=200)
    pdf.multi_cell(txt="\t\t\t\x95 Shots made and missed:\n", w=0)
    pdf.image("output/graph.png", w=130, x=50)
    pdf.output("output/report.pdf")
