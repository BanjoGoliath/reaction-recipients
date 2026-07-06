import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

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
    
static_dir = Path.cwd() / "static"

dbg.debug("Looking for compatible files.")
json_files = []
static_subdirectories = []
print(f"\n{static_dir}")
for path in sorted(static_dir.rglob("*", recurse_symlinks=True)):
    spacer = len(path.relative_to(static_dir).parts) * "    "
    if path.is_dir() and path.name != "__do_not_remove":
        print(f"{spacer}/{path.name}")
        static_subdirectories.append(path)
    elif path.suffix == ".json":
        print(f"{spacer}\033[0;32m{len(json_files)}\033[0m {path.name}")
        json_files.append(path)
print()

if len(json_files) == 0:
    dbg.fatal("No .json files were found in the ./static/ directory or children for use with reaction-recipients.\nPlease populate ./static/ with JSON exports from DiscordChatExporter, including static asset folders together with the JSON files if used.\nYou may wish to symlink the folders containing all of your exports and data into ./static/.")
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
                        dbg.warning(f"Could not read the contents of {file.name}. Skipping...")
            break
        except ValueError as e:
            dbg.error("Failed to parse: %s", e)


# Static assets need to be resolved recursively too as with the JSON files on discovery
found_asset_paths = set()
def get_asset(asset_path: str):
    if asset_path.startswith("http"):
        return asset_path
    for fap in found_asset_paths:
        if fap[0] == asset_path:
            return fap[1]
    for subdir in static_subdirectories:
        new_path = Path.joinpath(subdir, asset_path.replace("\\", "/"))
        if new_path.exists():
            resolved_path = str(new_path.relative_to(static_dir.parent))
            found_asset_paths.add((asset_path, resolved_path))
            return resolved_path
    return asset_path


dbg.debug(f"Loaded {len(files)} file(s). Starting Flask server.")

@app.route("/", defaults={"filter": None})
@app.route("/<filter>")
def index(filter):
    if filter is not None and filter not in map(lambda f: f["name"], filters):
        return redirect("/")
    filtered_message_data = get_filtered_message_data(filter, files) if filter is not None else []
    return render_template("index.html", files_loaded=len(files), filters=filters, active_filter_name=filter, filtered_message_data=filtered_message_data, get_asset=get_asset)

@app.route("/change_filters", methods=["POST"])
def change_filters():
    global filters
    new_filter_names = set()
    for filter in request.form:
        new_filter_names.add(filter.strip().replace(" ", "_"))
    new_filters = []
    for code in new_filter_names:
        new_filters.append({"name": code, "unicode": try_get_emoji(code)})
    filters = new_filters
    with filters_file.open("w") as file:
        json.dump(new_filters, file)
    return redirect("/")

def try_get_emoji(code):
    try:
        for file in files:
            for message in file["messages"]:
                for reaction in message["reactions"]:
                    if reaction["emoji"]["code"] == code:
                        return reaction["emoji"]["name"]
    except:
        return code
    return code


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
    author_name: str
    author_pfp: str # link similar to attachment but more sophisticated and image-like
    content: str # any renderable text content
    attachment_urls: list[str] # can be empty
    timestamp: datetime # content post, not bothering about edit
    reacted_count: int # targetted reaction filter #, usually 1
    additional_reactions_present: bool # whether to note other reactions are present on the message


def get_filtered_message_data(filter: str, files: list):
    matched_reacted_messages: list[ReactedMessage] = []
    for file in files:
        try:
            for message in file["messages"]:
                for reaction in message["reactions"]:
                    if reaction["emoji"]["code"].lower() == filter.lower():
                        matched_reacted_messages.append(
                            ReactedMessage(
                                file["guild"]["name"],
                                file["channel"]["name"],
                                "@me" if (gid := file["guild"]["id"]) == "0" else gid,
                                file["channel"]["id"],
                                message["id"],
                                message["author"]["nickname"],
                                message["author"]["avatarUrl"],
                                message["content"],
                                list(map(lambda x: x["url"], message["attachments"])),
                                datetime.fromisoformat(message["timestamp"]),
                                reaction["count"], len(message["reactions"]) > 1
                            )
                        )
        except Exception as e:
            dbg.error(f"Malformed data searching for filter '{filter}'. Ignoring error: {e}")
    matched_reacted_messages.sort(key=lambda x: x.timestamp)
    return matched_reacted_messages
    
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
