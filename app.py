from flask import Flask
import config as config
from extensions.exts import db, mail, socketio
from models.models import UserModel
from blueprints.user.admin import bp as admin_bp
from blueprints.basic.home import bp as home_bp
from blueprints.basic.song import bp as song_bp
from blueprints.user.auth import bp as auth_bp
from blueprints.user.upload import bp as upload_bp
from blueprints.user.profile import bp as profile_bp
from blueprints.user.message import bp as message_bp
from blueprints.basic.search import bp as search_bp
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_login import current_user

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
mail.init_app(app)
csrf = CSRFProtect(app)
socketio.init_app(app, cors_allowed_origins="*")

migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


app.register_blueprint(auth_bp, url_prefix="/user/auth")
app.register_blueprint(profile_bp, url_prefix='/user/profile')
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(upload_bp, url_prefix="/user/upload")
app.register_blueprint(home_bp, url_prefix='/')
app.register_blueprint(song_bp, url_prefix="/song")
app.register_blueprint(message_bp, url_prefix="/user/profile")
app.register_blueprint(search_bp, url_prefix="/")

csrf.exempt(app.view_functions['message.send_message'])
csrf.exempt(app.view_functions['home.category'])
csrf.exempt(app.view_functions['song.like_song'])
csrf.exempt(app.view_functions['song.dislike_song'])
csrf.exempt(app.view_functions['profile.add_playlist'])
csrf.exempt(app.view_functions['profile.delete_playlist'])
csrf.exempt(app.view_functions['profile.rename_playlist'])
csrf.exempt(app.view_functions['profile.publish_playlist'])
csrf.exempt(app.view_functions['profile.set_private'])
csrf.exempt(app.view_functions['profile.delete_song_route'])


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

@app.context_processor
def my_context_processor():
    return {"current_user": current_user}


if __name__ == '__main__':
    socketio.run(app, debug=True)
