import requests
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROUP_ID = 35287587

ROLE_IDS = {
    229688001: "Small Council",
    230814004: "The Hand",
    231098004: "King Consort Daemon",
    231112001: "Queen Rhaenyra"
}

TARGET_PLACE_ID = 82465164655976
DISCORD_ROLE_ID = "1475231504350056534"

def get_all_role_users():
    users = {}

    for role_id, role_name in ROLE_IDS.items():
        cursor = None

        while True:
            url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles/{role_id}/users?limit=100"
            if cursor:
                url += f"&cursor={cursor}"

            res = requests.get(url).json()

            for user in res.get("data", []):
                users[user["userId"]] = (user["username"], role_name)

            cursor = res.get("nextPageCursor")
            if not cursor:
                break

    return users

def check_presence(user_ids):
    url = "https://presence.roblox.com/v1/presence/users"
    res = requests.post(url, json={"userIds": user_ids}).json()
    return res.get("userPresences", [])

def send_alert(username, role_name):
    important_roles = ["The Hand", "King Consort Daemon", "Queen Rhaenyra"]

    if role_name in important_roles:
        content = f"<@&1475231504350056534> 🚨 {username} ({role_name}) joined THE CAPITAL OF THE REALM!"
    else:
        content = f"🚨 {username} ({role_name}) joined THE CAPITAL OF THE REALM!"

    requests.post(WEBHOOK_URL, json={"content": content})

def main():
    tracked_users = get_all_role_users()
    user_ids = list(tracked_users.keys())

    for i in range(0, len(user_ids), 100):
        batch = user_ids[i:i+100]
        presences = check_presence(batch)

        for user in presences:
            user_id = user["userId"]
            status = user.get("userPresenceType")
            place_id = user.get("placeId")

            username, role_name = tracked_users.get(user_id, ("Unknown", "Unknown"))

            if status == 2 and place_id == TARGET_PLACE_ID:
                send_alert(username, role_name)

if __name__ == "__main__":
    main()
