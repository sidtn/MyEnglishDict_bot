import os
from dotenv import load_dotenv
from db_manager import DbManage

db = DbManage('words.db')

load_dotenv()
TOKEN = os.getenv('TOKEN')
ADMIN_ID = 434325361
ALLOWED_USERS = db.get_users()
