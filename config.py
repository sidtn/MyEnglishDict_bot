import os
from dotenv import load_dotenv
from db_manager import DbManage

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = 434325361
ALLOWED_USERS = DbManage('words.db').get_users()
