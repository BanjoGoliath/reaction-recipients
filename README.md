# Reaction Recipients
Flask app that uses a [Discord Chat Exporter](https://github.com/Tyrrrz/DiscordChatExporter) export to find and display every message with relevant reactions.

Run using:
```
python -m flask run
```
and follow terminal instructions to initialise the app with data. Your data files being the JSON (export format) and static (downloaded through the `Download assets` function) files/folders should be put into `static/` in any directory structure. The application will attempt to find them recursively. Do not touch `__do_not_remove/`.

The web interface will be available on `http://localhost:5000` on successful initialisation from the terminal.

>[!NOTE]
>Due to behaviours in the Discord CDN, if you choose to not `Download assets`, attachment links will expire and report HTTP 404 in the viewer after some time reporting `This content is no longer available`. This is a behaviour of their CDN to prevent cross-platform abuse.
>
>It is recommended to download assets when you do your exports.

>[!IMPORTANT]
>This app assumes a single user only on the Flask instance (localhost for **one** user viewing on their *own* machine, no shared web hosting).
