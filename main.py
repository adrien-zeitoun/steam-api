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

@app.get("/dashboard")
def dashboard(x_api_key: str = Header(None)):
    check_key(x_api_key)

    games_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={STEAM_ID}&include_appinfo=true"
    games = requests.get(games_url).json()["response"]["games"]

    # 3 derniers jeux joués
    recent = sorted(games, key=lambda x: x.get("rtime_last_played", 0), reverse=True)[:3]

    # Limite à 10 jeux pour les trophées
    total_trophies = 0
    for g in games[:10]:
        ach_url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={API_KEY}&steamid={STEAM_ID}&appid={g['appid']}"
        ach = requests.get(ach_url).json()

        if "playerstats" in ach and "achievements" in ach["playerstats"]:
            total_trophies += sum(a["achieved"] for a in ach["playerstats"]["achievements"])

    return {
        "total_trophies": total_trophies,
        "recent_games": recent
    }

    