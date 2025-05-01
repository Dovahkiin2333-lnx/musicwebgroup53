from flask import Blueprint, url_for, jsonify
from models.models import SongModel, ProfileModel, SearchIndexModel
from extensions.exts import db
from sqlalchemy import select
from werkzeug.utils import secure_filename
from forms.upload_form import ImageUploadForm, MusicUploadForm
from datetime import datetime
from flask_login import login_required, current_user
import os
from pathlib import Path
from flask import current_app

bp = Blueprint("upload", __name__)


@bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.avatar.data
        file.seek(0)
        filename = secure_filename(file.filename)

        avatar_folder = f"{current_user.role}{current_user.id}"
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])/'avatars'/ avatar_folder
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / filename
        file.save(str(file_path))

        profile = db.session.scalar(
            select(ProfileModel).where(ProfileModel.user_id == current_user.id)
        )
        if not profile:
            profile = ProfileModel(user_id = current_user.id, avatar_filename=filename)
            db.session.add(profile)
        else:
            profile.avatar_filename = filename
            profile.avatar_approved = False
        db.session.commit()

        avatar_url = url_for('profile.get_avatar', filename = filename, user_id = current_user.id)
        return jsonify({
            "success": True,
            "avatar_url": avatar_url,
            "message": "Avatar uploaded successfully"
        })
    
    return jsonify({
        "success": False,
        "error": form.errors
    }), 400


@bp.route('/upload_music', methods=['POST'])
@login_required
def upload_music():
    form = MusicUploadForm()
    
    if form.validate_on_submit():
        try:
            audio_file = form.audio.data
            audio_filename = f"audio_{current_user.id}_{int(datetime.now().timestamp())}_{secure_filename(audio_file.filename)}"
            audio_folder = f"{current_user.role}{current_user.id}"
            upload_dir = Path(current_app.config['UPLOAD_FOLDER'])/'audios'/ audio_folder
            upload_dir.mkdir(parents=True, exist_ok=True)
            audio_path = upload_dir / audio_filename
            audio_file.save(audio_path)
            
            cover_filename = None
            if form.cover.data:
                cover_file = form.cover.data
                cover_filename = f"cover_{current_user.id}_{int(datetime.now().timestamp())}_{secure_filename(cover_file.filename)}"
                cover_folder = f"{current_user.role}{current_user.id}"
                cover_upload_dir = Path(current_app.config['UPLOAD_FOLDER'])/'covers'/ cover_folder
                cover_upload_dir.mkdir(parents=True, exist_ok=True)
                cover_path = cover_upload_dir / cover_filename
                cover_file.save(cover_path)
            
            new_song = SongModel(
                title=form.title.data,
                artist=form.artist.data,
                category=form.category.data if form.category.data else None,
                release_date=datetime.combine(form.release_date.data, datetime.min.time()) if form.release_date.data else None,
                cover_filename=cover_filename,
                audio_filename=audio_filename,
                uploader_id=current_user.id,
                is_approved=False 
            )
            
            db.session.add(new_song)
            db.session.commit()
            
            new_song_cover = f"{current_user.role}{current_user.id}/{new_song.cover_filename}"
            search_entry = SearchIndexModel(
            content_type="song",
            content_id=new_song.id,
            title=new_song.title,
            description=f"artist: {new_song.artist}",
            image_url=new_song_cover,
            is_approved = new_song.is_approved,
            search_content=f"{new_song.title} {new_song.artist}"
            )
            db.session.add(search_entry)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Song uploaded successfully! It will be reviewed soon."
            })
            
        except Exception as e:
            current_app.logger.error(f"Upload failed: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"Upload failed: {str(e)}"
            }), 500
    
    errors = {field.name: field.errors for field in form if field.errors}
    return jsonify({
        "success": False,
        "message": "Validation failed",
        "errors": errors
    }), 400
