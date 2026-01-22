import json
from pprint import pprint

fire = []
disc = []
gold = []

with open("data.json", "r") as file:
    data = json.load(file)
    messages = data.get("messages")

link_prefix = f"https://discord.com/channels/@me/{data["channel"]["id"]}"

for message in messages:
    if not message["reactions"]:
        pass

    for reaction in message["reactions"]:
        match reaction.get("emoji").get("code"):
            case "fire":
                fire.append(f"{link_prefix}/{message["id"]}")
            case "cd":
                disc.append(f"{link_prefix}/{message["id"]}")
            case "dvd":
                gold.append(f"{link_prefix}/{message["id"]}")



pprint(f"{len(fire)} messages were Fired:{fire}")
pprint(f"{len(disc)} messages were saved to compact disc:{disc}")
pprint(f"{len(gold)} messages were saved to golden disk for aliens to view:{gold}")
