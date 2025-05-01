from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from models.models import (UserModel, SongModel, CommentModel, FriendshipModel, MessageModel, 
    ProfileModel, LikeModel, PlaylistModel, PlaylistSongModel, NotificationModel, SearchIndexModel
)
from extensions.exts import db
import os
import shutil
from pathlib import Path
from flask import current_app


def safe_delete_file(file_path):
    try:
        if file_path.exists():
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False
def safe_delete_folder(folder_path):
    try:
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Error deleting folder {folder_path}: {str(e)}")
        return False
    

def delete_user(user_id):
    try:
        user = UserModel.query.get(user_id)
        if not user:
            return False, "User not found"
        
        user_folder_prefix = f"{user.role}{user.id}"

        FriendshipModel.query.filter(
        (FriendshipModel.user_id == user_id) | 
        (FriendshipModel.friend_id == user_id)
        ).delete()
        
        MessageModel.query.filter(
            (MessageModel.sender_id == user_id) | 
            (MessageModel.recipient_id == user_id)
        ).delete()
        
        profile = ProfileModel.query.filter_by(user_id=user_id).first()
        if profile and profile.avatar_filename:
            avatar_folder = Path(current_app.config['UPLOAD_FOLDER']) / 'avatars' / user_folder_prefix
            avatar_path = avatar_folder / profile.avatar_filename
            safe_delete_file(avatar_path)
            if avatar_folder.exists() and not any(avatar_folder.iterdir()):
                safe_delete_folder(avatar_folder)
        
        ProfileModel.query.filter_by(user_id=user_id).delete()
        
        NotificationModel.query.filter(
            (NotificationModel.send_by == user_id) | 
            (NotificationModel.accept_by == user_id)
        ).delete()
        
        LikeModel.query.filter_by(user_id=user_id).delete()
        
        comments = CommentModel.query.filter_by(user_id=user_id).all()
        for comment in comments:
            delete_comment(comment.id)
        
        songs = SongModel.query.filter_by(uploader_id=user_id).all()
        for song in songs:
            delete_song(song.id)
        
        PlaylistModel.query.filter_by(user_id=user_id).delete()
        
        SearchIndexModel.query.filter_by(
            content_type='user', 
            content_id=user_id
        ).delete()

        for folder_type in ['avatars', 'audios', 'covers']:
            user_folder = Path(current_app.config['UPLOAD_FOLDER']) / folder_type / user_folder_prefix
            safe_delete_folder(user_folder)
        
        print("till here,"+ user.username)
        db.session.delete(user)
        db.session.commit()
        deleted_user = UserModel.query.get(user_id)
        print(f"User after deletion: {deleted_user}")
        return True, "User deleted successfully"
    
    except IntegrityError as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting user: {str(e)}"

def delete_song(song_id):
    try:
        song = SongModel.query.get(song_id)
        if not song:
            return False, "Song not found"
        
        uploader_folder_prefix = f"{song.uploader.role}{song.uploader.id}"

        if song.audio_filename:
            audio_folder = Path(current_app.config['UPLOAD_FOLDER']) / 'audios' / uploader_folder_prefix
            audio_path = audio_folder / song.audio_filename
            safe_delete_file(audio_path)
            if audio_folder.exists() and not any(audio_folder.iterdir()):
                safe_delete_folder(audio_folder)
        
        if song.cover_filename:
            cover_folder = Path(current_app.config['UPLOAD_FOLDER']) / 'covers' / uploader_folder_prefix
            cover_path = cover_folder / song.cover_filename
            safe_delete_file(cover_path)
            if cover_folder.exists() and not any(cover_folder.iterdir()):
                safe_delete_folder(cover_folder)

        LikeModel.query.filter_by(song_id=song_id).delete()
        
        PlaylistSongModel.query.filter_by(song_id=song_id).delete()
        
        comments = CommentModel.query.filter_by(song_id=song_id).all()
        for comment in comments:
            delete_comment(comment.id)
        
        SearchIndexModel.query.filter_by(
            content_type='song', 
            content_id=song_id
        ).delete()
        
        db.session.delete(song)
        db.session.commit()
        
        return True, "Song deleted successfully"
    
    except IntegrityError as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting song: {str(e)}"

def delete_comment(comment_id):
    try:
        comment = CommentModel.query.get(comment_id)
        if not comment:
            return False, "Comment not found"
        
        db.session.delete(comment)
        db.session.commit()
        
        return True, "Comment deleted successfully"
    
    except IntegrityError as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting comment: {str(e)}"