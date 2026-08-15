AEP DOWNGRADER - WEB VERSION
=============================

FILES
-----
app.py
templates/index.html
static/style.css
static/script.js
requirements.txt

INSTALL
-------
1. Install Python 3.10+.

2. Open terminal in this folder.

3. Install dependencies:

   pip install -r requirements.txt

4. Start the website:

   python app.py

5. Open:

   http://127.0.0.1:5000


NETWORK ACCESS
--------------
To open it from another device on the same network, use the computer's
local IP address:

   http://YOUR-PC-IP:5000


IMPORTANT
---------
This web version keeps the same header-byte downgrade method from the
provided Telegram bot.

Changing the AEP header does not guarantee that every project will be
fully compatible with an older After Effects version. Complex projects,
newer features, plugins, expressions, and unsupported project data may
still cause problems in the older AE version.

For production/public hosting, add authentication, rate limiting,
secure temporary-file cleanup, HTTPS, and stronger upload validation.
