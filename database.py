from settings import *
import datetime
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

class DatabaseHandler:

    def __init__(self):
        pass

    async def new_user(self, user_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(
            f"""INSERT INTO users VALUES ({str(user_id)}, 0, 'n', 'n');"""
        )
        conn.commit()
        cur.close()
        conn.close()
        return

    async def set_user_state(self, user_id,  state:int):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')        
        cur = conn.cursor()
        cur.execute(f"""UPDATE users SET state='{state}' WHERE userid='{str(user_id)}';""")
        conn.commit()
        cur.close()
        conn.close()

    async def get_user_state(self, user_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor() 
        cur.execute(f"""SELECT state FROM users WHERE userid='{str(user_id)}';""")
        res = cur.fetchone()
        cur.close()
        conn.close()
        return res[0]
    
    async def get_instagram_username(self, user_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"""SELECT insta FROM users WHERE userid='{str(user_id)}';""")
        res = cur.fetchone()
        cur.close()
        conn.close()
        return res[0]

    async def is_user(self, user_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM users WHERE userid='{str(user_id)}';""")
        res = cur.fetchall()
        cur.close()
        conn.close()
        if len(res) != 0: 
            return True, res[0]
        return False, ()

    async def set_instagra_username(self, user_id, username):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"""UPDATE users SET insta='{username}' WHERE userid='{str(user_id)}';""")
        conn.commit()
        cur.close()
        conn.close()

    async def wait_user(self, user_id):
        now = datetime.datetime.now()
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"""UPDATE users SET lastused = '{now}' WHERE userid='{user_id}';""")
        conn.commit()
        cur.close()
        conn.close()
        return

    async def all_users_id(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"""SELECT userid FROM users""")
        users = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for user in users:
            result.append(user[0])
        return result


