import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

SECRET_KEY = "asdfkasjdhf"

WTF_CSRF_ENABLED = True  
WTF_CSRF_SECRET_KEY = "ziasdyfgfmfdy"


HOSTNAME = '127.0.0.1'
PORT = '3306'
USERNAME = 'root'
PASSWORD = '7355608'
# DATABASE = 'musicweb'
DB_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/musicweb?charset=utf8mb4'
SQLALCHEMY_DATABASE_URI = DB_URI

SQLALCHEMY_BINDS = {
    'studentdb': f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/studentdb?charset=utf8mb4'
}


MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "2908842370@qq.com"
MAIL_PASSWORD = "jykcfuutsbabdgcf"
MAIL_DEFAULT_SENDER = "2908842370@qq.com"


