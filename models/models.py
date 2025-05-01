from extensions.exts import db
from datetime import datetime
from flask_login import UserMixin

class Student(db.Model):
    __bind_key__ = 'studentdb'  
    __tablename__ = 'students' 

    id = db.Column(db.Integer, primary_key=True)
    s_name = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(100), unique=True)  
    s_id = db.Column(db.String(9), unique=True)    



class UserModel(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    s_name = db.Column(db.String(100))
    password = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)
    role = db.Column(db.String(20), nullable=False, default="user")
    student_id = db.Column(db.Integer, nullable=True)
    messages_sent = db.relationship('MessageModel', foreign_keys='MessageModel.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('MessageModel', foreign_keys='MessageModel.recipient_id', backref='recipient', lazy='dynamic')
    friends = db.relationship('FriendshipModel', foreign_keys='FriendshipModel.user_id', backref='user', lazy='dynamic')

    

    __table_args__ = (
        db.CheckConstraint(
            role.in_(['student','user','admin','auditor','sadmin']),
            name='check_role_values'
        ),
    )
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class FriendshipModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    friend = db.relationship('UserModel',
                              foreign_keys=[friend_id],
                                backref=db.backref('friend_of', lazy='dynamic'))
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )
    def __repr__(self):
        return f'<Friendship {self.user_id} -> {self.friend_id}>'
    
    
class MessageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return f'<Message {self.sender_id} -> {self.recipient_id}>'
    

class EmailCaptchaModel(db.Model):
    __tablename__ = "email_captcha"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    captcha = db.Column(db.String(100), nullable=False)

class ProfileModel(db.Model):
    __tablename__ = "user_profiles"
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    description = db.Column(db.Text)
    avatar_filename = db.Column(db.String(255))
    avatar_upload_time = db.Column(db.DateTime, default=datetime.now)
    avatar_approved = db.Column(db.Boolean, default=False)
    description_approved = db.Column(db.Boolean, default=False)
    
    user = db.relationship("UserModel", backref=db.backref("profile", uselist=False))
    


class SongModel(db.Model):
    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    cover_filename = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    release_date = db.Column(db.DateTime, nullable=True)
    audio_filename = db.Column(db.String(500), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    upload_time = db.Column(db.DateTime, default=datetime.now)
    uploader = db.relationship('UserModel', backref=db.backref('uploaded_songs', lazy='dynamic'))
    __table_args__ = (
        db.CheckConstraint(
            category.in_(['happy','relax','modern','vocal','432Hz']),
            name='check_category_value'
        ),
    )

    @property
    def cover_path(self):
        return f"{self.uploader.role}{self.uploader.id}/{self.cover_filename}" if self.cover_filename else None
    
    @property
    def audio_path(self):
        return f"{self.uploader.role}{self.uploader.id}/{self.audio_filename}"

class LikeModel(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    liked_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('UserModel', backref=db.backref('likes', lazy='dynamic'))
    song = db.relationship('SongModel', backref=db.backref('likes', lazy='dynamic'))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'song_id', name='_user_song_like_uc'),
    )


class PlaylistModel(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    user = db.relationship('UserModel', backref=db.backref('playlists', lazy='dynamic', cascade='all, delete-orphan'))
    songs = db.relationship('PlaylistSongModel', backref='playlist', lazy='dynamic', cascade='all, delete-orphan')
    


class PlaylistSongModel(db.Model):
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id', ondelete='CASCADE'), nullable=False)
    position = db.Column(db.Integer, nullable=False, doc='sequence')
    added_at = db.Column(db.DateTime, default=datetime.now())
    
    
    song = db.relationship('SongModel', backref=db.backref('playlist_associations', lazy='dynamic'))
    
   
    __table_args__ = (
        db.UniqueConstraint('playlist_id', 'song_id', name='_playlist_song_uc'),
    )


class CommentModel(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(500), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_approved = db.Column(db.Boolean, default=False)
    
    user = db.relationship('UserModel', backref=db.backref('comments', lazy='dynamic'))
    song = db.relationship('SongModel', backref=db.backref('comments', lazy='dynamic'))

class NotificationModel(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(500), nullable=False)  
    send_by = db.Column(db.Integer, db.ForeignKey('user.id')) 
    accept_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    sender = db.relationship('UserModel', foreign_keys=[send_by], backref='sent_notifications')
    receiver = db.relationship('UserModel', foreign_keys=[accept_by], backref='received_notifications')

    @staticmethod
    def send_notification(receiver_id, content, sender_id=None):
        notification = NotificationModel(
            content=content,
            send_by=sender_id,
            accept_by=receiver_id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
class SearchIndexModel(db.Model):
    __tablename__ = "search_index"
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(20), nullable=False)  
    content_id = db.Column(db.Integer, nullable=False)  
    search_content = db.Column(db.Text, nullable=False)  
    title = db.Column(db.String(200), nullable=False)  
    description = db.Column(db.Text)  
    image_url = db.Column(db.String(500))  
    is_approved = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.Index('idx_search', 'search_content', mysql_prefix='FULLTEXT'),
        db.Index('idx_content', 'content_type', 'content_id', unique=True),
    )


