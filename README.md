# Reaction Recipients
Flask app that uses a [Discord Chat Exporter](https://github.com/Tyrrrz/DiscordChatExporter) export to find and display every message with relevant reactions.

Run using:
```
python -m flask run
```
and follow terminal instructions to initialise the app with data. Content directories for the JSON files downloaded through the `Download assets` function go in `static/`, whereas the JSON files themselves go in `static/data/`.

The web interface will be available on `http://localhost:5000` on successful initialisation from the terminal.

>[!NOTE]
>Due to behaviours in the Discord CDN, if you choose to not `Download assets`, attachment links will expire and report HTTP 404 in the viewer after some time reporting `This content is no longer available`. This is a behaviour of their CDN to prevent cross-platform abuse.
>
>It is recommended to download assets when you do your exports.

>[!IMPORTANT]
>This app assumes a single user only on the Flask instance (localhost for **one** user viewing on their *own* machine, no shared web hosting).
