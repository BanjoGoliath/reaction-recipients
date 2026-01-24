import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, render_template, url_for

from logger import dbg

app = Flask(__name__)

dbg.debug("Loading filters.")
filters_file = Path.cwd() / "filters.json"
if not filters_file.exists():
    dbg.info("New filters file created under filters.json")
    filters_file.touch()

filters = []
with filters_file.open("r+") as file:
    try:
        filters = json.load(file)
        for filter in filters:
            # Rudimentary check on JSON file structure for filters
            if not filter["name"] or not filter["unicode"]:
                raise Exception()
    except:
        # Sane defaults
        dbg.warning("Could not read and parse from filters.json, overwriting with defaults.")
        file.seek(0)
        file.truncate()
        defaults = [{"name": "fire", "unicode": "🔥"}, {"name": "cd", "unicode": "💿"}, {"name": "dvd", "unicode": "📀"}]
        json.dump(defaults, file)
        filters = defaults
    
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
    with json_files[0].open("r") as file:
        try:
            files.append(json.load(file))
        except:
            dbg.fatal(f"Could not read the contents of {file.name}. Aborting.")
            exit(1)
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
                with json_files[i].open("r") as file:
                    try:
                        files.append(json.load(file))
                    except:
                        dbg.fatal(f"Could not read the contents of {file.name}. Aborting.")
                        exit(1)
            break
        except ValueError as e:
            dbg.error("Failed to parse: %s", e)

dbg.debug(f"Loaded {len(files)} file(s). Starting Flask server.")

@app.route("/", defaults={"filter": None})
@app.route("/<filter>")
def index(filter):
    if filter is not None and filter not in map(lambda f: f["name"], filters):
        return redirect("/")
    filtered_message_data = get_filtered_message_data(filter, files)
    return render_template("index.html", files_loaded=len(files), filters=filters, active_filter_name=filter, filtered_message_data=filtered_message_data)

@app.route("/<dir>/<file>") # should be fine for directory then file located items
def static_content(dir, file):
    return redirect(url_for("static", filename=f"{dir}/{file}"))

@app.errorhandler(404)
def file_not_found(e):
    return render_template("404.html"), 404

@dataclass
class ReactedMessage:
    server: str # for DMs using Direct Messages
    channel: str # for DMs use GC or DM name
    guild_id: str
    channel_id: str
    message_id: str
    author_name: str # no pfp as we just use JSON
    content: str # any renderable text content
    probable_content: list[str] # best guess(es) to some content we can render with the message. e.g messages with single attachments which we can find
    has_attachments: bool
    timestamp: datetime # content post, not bothering about edit
    reacted_count: int # targetted reaction filter #, usually 1
    additional_reactions_present: bool # whether to note other reactions are present on the message


def get_filtered_message_data(filter: str, files: list):
    matched_reacted_messages: list[ReactedMessage] = []
    for file in files:
        try:
            for message in file["messages"]:
                if not message["reactions"]:
                    pass

                for reaction in message["reactions"]:
                    if reaction["emoji"]["code"].lower() == filter.lower():
                        matched_reacted_messages.append(
                            ReactedMessage(file["guild"]["name"], file["channel"]["name"], "@me" if (gid := file["guild"]["id"]) == "0" else gid, file["channel"]["id"], message["id"], message["author"]["nickname"], message["content"], try_get_probable_content(message), not not message["attachments"], datetime.fromisoformat(message["timestamp"]), reaction["count"], len(message["reactions"]) > 1)
                        )
        except Exception as e:
            dbg.error(f"Malformed data searching for filter '{filter}'. Ignoring error: {e}")
    return matched_reacted_messages

def try_get_probable_content(message):
    try:
        # all attachments available. also this will just auto play videos or download files since we use an iframe internally but thats fine. funnier.
        # ideally we check the file type and render img or video appropriately.
        return list(map(lambda x: x["url"], message["attachments"])) or [message["content"]]
    except:
        return [message["content"]]
    
# bango land
# fire = []
# disc = []
# gold = []
# with open("data.json", "r") as file:
#     data = json.load(file)
#     messages = data.get("messages")

# link_prefix = f"https://discord.com/channels/@me/{data["channel"]["id"]}"

# for message in messages:
#     if not message["reactions"]:
#         pass

#     for reaction in message["reactions"]:
#         match reaction.get("emoji").get("code"):
#             case "fire":
#                 fire.append(f"{link_prefix}/{message["id"]}")
#             case "cd":
#                 disc.append(f"{link_prefix}/{message["id"]}")
#             case "dvd":
#                 gold.append(f"{link_prefix}/{message["id"]}")

# pprint(f"{len(fire)} messages were Fired:{fire}")
# pprint(f"{len(disc)} messages were saved to compact disc:{disc}")
# pprint(f"{len(gold)} messages were saved to golden disk for aliens to view:{gold}")
