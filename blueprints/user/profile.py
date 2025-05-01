from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    current_app,
    abort,
    send_from_directory,
)
from extensions.exts import db
from models.models import (
    UserModel,
    ProfileModel,
    PlaylistModel,
    SongModel,
    PlaylistSongModel,
    FriendshipModel
)
from forms.auth_form import ChangePwForm, ChangeUsernameForm
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from sqlalchemy import select
from utils.delete_process import delete_song


ALLOWED_CATEGORIES = ["happy", "relax", "modern", "vocal", "432HZ"]

bp = Blueprint("profile", __name__)


from flask import abort

@bp.route("/my-profile", methods=["GET", "POST"])
@login_required
def my_profile():
    collection = PlaylistModel.query.filter_by(
        user_id=current_user.id,
        title="My Collection"
    ).first()

    if not collection:
        my_collection = PlaylistModel(
            user_id = current_user.id,
            title = "My Collection"
        )
        db.session.add(my_collection)
        db.session.commit()

    return profile_impl(current_user.id) 

@bp.route("/<int:user_id>", methods=["GET"])
def public_profile(user_id):
    return profile_impl(user_id)

def profile_impl(user_id):
    user = db.session.scalar(
        select(UserModel).where(UserModel.id ==user_id)
    )
    profile = db.session.scalar(
        select(ProfileModel).where(ProfileModel.user_id == user_id)
    )
    if not profile:
        if user_id == current_user.id:
            profile = ProfileModel(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        else:  
            abort(404)
    friendship_status = 'none'
    if current_user.is_authenticated and current_user.id != user_id:
        sent_request=FriendshipModel.query.filter_by(
            user_id = current_user.id,
            friend_id = user_id
        ).first()

        received_request = FriendshipModel.query.filter_by(
            user_id = user_id,
            friend_id = current_user.id
        ).first()

        if sent_request:
            friendship_status = 'sent'
        elif received_request:
            friendship_status = 'received'
        if sent_request and received_request:
            existing_friendship = FriendshipModel.query.filter(
                ((FriendshipModel.user_id == current_user.id) & 
                 (FriendshipModel.friend_id == user_id)) |
                ((FriendshipModel.user_id == user_id) & 
                 (FriendshipModel.friend_id == current_user.id))
            ).first()

            if existing_friendship:
                friendship_status='friends'
    return render_template("profile/profile.html", profile=profile,
                            user = user,
                            friendship_status = friendship_status
                            )



@bp.route("/avatars/<int:user_id>/<filename>")
def get_avatar(user_id, filename):
    user = db.session.scalar(
        select(UserModel).where(UserModel.id ==user_id)
    )
    if not user:
        abort(404)
    profile = db.session.scalar(
        select(ProfileModel).where(ProfileModel.user_id == user_id)
    )
    if not profile or not profile.avatar_approved:
        if not current_user.is_authenticated or current_user.id != user_id:
            return redirect(url_for("static", filename="images/default-user-avatar.jpg"))
        
    avatar_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "avatars" / f"{user.role}{user.id}"
    if not (avatar_dir / filename).exists():
        abort(404)
    return send_from_directory(avatar_dir.as_posix(), filename)



@bp.route("/sections/upload-music")
@login_required
def load_upload_section():
    return render_template(
        "profile/sections/upload-music.html", categories=ALLOWED_CATEGORIES
    )

@bp.route("/sections/setting", methods=['POST', 'GET'])
@login_required
def profile_setting():
    profile = db.session.scalar(
    select(ProfileModel).where(ProfileModel.user_id == current_user.id)
        )
    if request.method=='GET':
        return render_template(
            "profile/sections/setting.html", profile = profile
        )
    
    form_type = request.form.get('form_type')
    
    if form_type == 'update-uname':
        form = ChangeUsernameForm(request.form)
        if form.validate():
            current_user.username = form.new_username.data
            db.session.commit()
            return jsonify(success=True, message="Username updated!")
    
    elif form_type == 'change-password':
        form = ChangePwForm(request.form)
        if form.validate():
            if not check_password_hash(current_user.password, form.current_password.data):
                return jsonify(success=False, message="Current password is incorrect!"), 400
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            return jsonify(success=True, message="New password updated!")

    elif form_type == 'update-description':
        new_description = request.form.get('new_description','').strip()
        if len(new_description) > 500:
             return jsonify(success=False, message="Description too long (max 500 chars)"),400
        profile.description = new_description
        profile.description_approved = False
        db.session.commit()
        return jsonify(
        success=True,
        message="Description submitted for admin review!"
    )
    
    print(form.errors)
    return jsonify(
        success=False,
        message="Validation failed",
        errors=form.errors
    ), 400

@bp.route("/sections/my-collection")
@login_required
def my_collection():
    collection = PlaylistModel.query.filter_by(
        user_id=current_user.id,
        title="My Collection"
    ).first()
    if not collection:
        collection = PlaylistModel(
            title="My Collection",
            user_id=current_user.id
        )
        db.session.add(collection)
        db.session.commit()
    songs = [ps.song for ps in collection.songs.order_by(PlaylistSongModel.added_at)]
    return render_template(
        "profile/sections/my-collection.html",
        songs=songs
    )

@bp.route("/sections/<int:user_id>/playlists")
def my_playlists(user_id):
    playlists = PlaylistModel.query.filter_by(user_id=user_id).all()
    if current_user.is_authenticated:
        return render_template(
            "profile/sections/my-playlists.html", 
            playlists=playlists,
            current_user_id=current_user.id, 
            owner_id=user_id  
        )
    return render_template(
            "profile/sections/my-playlists.html", 
            playlists=playlists, 
            owner_id=user_id  
        )



@bp.route('/playlist/<int:playlist_id>/songs')
def playlist_songs(playlist_id):
    playlist = PlaylistModel.query.get_or_404(playlist_id)
    songs = SongModel.query.join(PlaylistSongModel).filter(
        PlaylistSongModel.playlist_id == playlist_id
    ).order_by(PlaylistSongModel.position).all()
    return render_template('profile/sections/playlist-songs.html', 
                         songs=songs, 
                         playlist_id=playlist_id,
                         is_public = playlist.is_public,
                         owner = playlist.user_id)


@bp.route('/add_playlist', methods=['POST'])
@login_required
def add_playlist():
    data = request.get_json()
    new_playlist = PlaylistModel(title=data['name'], user_id=current_user.id)
    db.session.add(new_playlist)
    db.session.commit()
    return jsonify(success=True)


@bp.route('/delete_playlist/<int:playlist_id>', methods=['DELETE'])
@login_required
def delete_playlist(playlist_id):
    playlist = PlaylistModel.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        return jsonify(success=False, message="Unauthorized"), 403
    db.session.delete(playlist)
    db.session.commit()
    return jsonify(success=True)


@bp.route('/rename_playlist/<int:playlist_id>', methods=['PUT'])
@login_required
def rename_playlist(playlist_id):
    data = request.get_json()
    playlist = PlaylistModel.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        return jsonify(success=False, message="Unauthorized"), 403
    playlist.title = data['new_name']
    db.session.commit()
    return jsonify(success=True)

@bp.route('/sections/<int:user_id>/posts')
def my_posts(user_id):
    songs = SongModel.query.filter(
    SongModel.uploader_id == user_id,
    SongModel.is_approved == True
    ).order_by(
    SongModel.upload_time.desc()
    ).all()
    return render_template('profile/sections/my-posts.html', songs=songs)


@bp.route('/delete-song/<int:song_id>', methods=['DELETE'])
@login_required
def delete_song_route(song_id):
    song = SongModel.query.get_or_404(song_id)
    
    if song.uploader_id != current_user.id and (current_user.role != 'admin' or 'sadmin'):
        return jsonify(success=False, message="Unauthorized"), 403
    
    success, message = delete_song(song_id)
    if not success:
        return jsonify({"success": False, "message": message}), 500
    
    return jsonify({"success": True, "message": message})

@bp.route('/publish_playlist/<int:playlist_id>', methods=['POST'])
@login_required
def publish_playlist(playlist_id):
    playlist = PlaylistModel.query.get_or_404(playlist_id)
    
    if playlist.user_id != current_user.id:
        return jsonify(success=False, message="Unauthorized"), 403
    
    try:
        playlist.is_public = True
        db.session.commit()
        return jsonify(success=True, is_public=True)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error publishing playlist: {str(e)}")
        return jsonify(success=False, message="Failed to publish playlist"), 500

@bp.route('/set_private/<int:playlist_id>', methods=['POST'])
@login_required
def set_private(playlist_id):
    playlist = PlaylistModel.query.get_or_404(playlist_id)
    
    if playlist.user_id != current_user.id:
        return jsonify(success=False, message="Unauthorized"), 403
    
    try:
        playlist.is_public = False
        db.session.commit()
        return jsonify(success=True, is_public=False)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error setting playlist private: {str(e)}")
        return jsonify(success=False, message="Failed to set playlist private"), 500

@bp.route("/piano")
@login_required
def piano():
    return render_template("piano.html")