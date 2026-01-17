from fastapi import FastAPI, Header, HTTPException
import requests
import os

app = FastAPI()

API_KEY = os.getenv("STEAM_API_KEY")
STEAM_ID = os.getenv("STEAM_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

def check_key(key):
    if key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Accès refusé")

@app.get("/")
def home():
    return {"status": "API Steam OK"}

@app.get("/recent-games")
def recent_games(x_api_key: str = Header(None)):
    check_key(x_api_key)

    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={STEAM_ID}&include_appinfo=true"
    data = requests.get(url).json()

    games = data["response"]["games"]
    games_sorted = sorted(games, key=lambda x: x.get("rtime_last_played", 0), reverse=True)

    return games_sorted[:3]

@app.get("/trophies")
def trophies(x_api_key: str = Header(None)):
    check_key(x_api_key)

    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={STEAM_ID}"
    games = requests.get(url).json()["response"]["games"]

    total = 0
    for g in games:
        ach = requests.get(
            f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
            f"?key={API_KEY}&steamid={STEAM_ID}&appid={g['appid']}"
        ).json()

        if "playerstats" in ach and "achievements" in ach["playerstats"]:
            total += sum(a["achieved"] for a in ach["playerstats"]["achievements"])

    return {"total_trophies": total}