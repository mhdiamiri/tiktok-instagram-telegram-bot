import os

# telegram bot token
token = ""

# database
DATABASE_NAME  = ""
DATABASE_USERNAME = ""
DATABASE_PASSWORD = ""

# instagram login
SAVE_LOGIN_DIR = "logins/"
if not os.path.exists(SAVE_LOGIN_DIR):
    os.mkdir(SAVE_LOGIN_DIR)

# server
CONNECTION_POOL_SIZE = 1280

# delay in seconds
DELAY = 30

# messages
WELCOME_MESSAGE = """Hi. please send me an instagram or tiktok link.
"""
LOGIN_MESSAGE ="""Please Send me your Instagram's username and password in two lines.
for example if your username is <b><i>"messi"</i></b> and your password is <b><i>"1234"</i></b> send me a message like this:
<i><b>messi</b></i>
<i><b>1234</b></i>
"""
INTERNAL_ERROR_MESSAGE = """
Internal Error! Please try again later.
"""

# bot admins
admin_id_list = [
        '5131315919',
]
