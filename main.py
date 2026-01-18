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

@app.get("/dashboard/{steam_id}")
def dashboard(steam_id: str, x_api_key: str = Header(None)):
    check_key(x_api_key)

    games_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={steam_id}&include_appinfo=true"
    games = requests.get(games_url).json()["response"].get("games", [])

    if not games:
        return {"error": "Profil privé ou SteamID invalide"}

    recent = sorted(games, key=lambda x: x.get("rtime_last_played", 0), reverse=True)[:3]

    total_trophies = 0
    for g in games[:10]:
        ach_url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={API_KEY}&steamid={steam_id}&appid={g['appid']}"
        ach = requests.get(ach_url).json()

        if "playerstats" in ach and "achievements" in ach["playerstats"]:
            total_trophies += sum(a["achieved"] for a in ach["playerstats"]["achievements"])

    return {
        "steam_id": steam_id,
        "total_trophies": total_trophies,
        "recent_games": recent
    }