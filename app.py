import json
from pathlib import Path

from flask import Flask

from logger import dbg

app = Flask(__name__)

data_dir = Path.cwd() / "data"
try:
    data_dir.mkdir(parents=True)
    dbg.info("New data directory created under ./data")
except FileExistsError:
    dbg.debug("Data directory located and will be used under ./data")

dbg.debug("Looking for compatible files.")
json_files = []
print(f"\n{data_dir}")
for path in sorted(data_dir.rglob("*")):
    spacer = len(path.relative_to(data_dir).parts) * "    "
    if path.is_dir():
        print(f"{spacer}/{path.name}")
    elif path.suffix == ".json":
        print(f"{spacer}\033[0;32m{len(json_files)}\033[0m {path.name}")
        json_files.append(path)
print()

if len(json_files) == 0:
    dbg.fatal("No .json files were found in the ./data directory to use for reaction-recipients.\nPlease populate ./data with json (and optionally directory/folder assorted) exports from DiscordChatExporter.")
    exit(1)
    
files = []

if len(json_files) == 1:
    print(f"Using '{json_files[0]}' as the only available data file.")
else:
    print("Multiple .json files are present in the data subdirectories.\nPlease provide a comma separated list (e.g. 0,1,3) of data files to load into reaction-recipients.\nPress enter with no response to use all files.")
    while True:
        try:
            res = input("> ").strip().split(",")
            if res[0]:
                # Filtered user input
                indexes = set([idx for idx in map(lambda x: int(x), res) if 0 <= idx < len(json_files)])
            else:
                # Use all
                indexes = list(map(lambda x: x[0], enumerate(json_files)))
            if len(indexes) == 0:
                raise ValueError("No valid file indexes provided.")
            for i in indexes:
                with open(json_files[i], "r") as file:
                    try:
                        files.append(json.load(file))
                    except:
                        dbg.fatal(f"Could not read the contents of {file.name}. Aborting.")
                        exit(1)
            break
        except ValueError as e:
            dbg.error("Failed to parse: %s", e)

dbg.debug(f"Loaded {len(files)} files. Starting Flask server.")
print(files)

# bango land
exit(0)
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
