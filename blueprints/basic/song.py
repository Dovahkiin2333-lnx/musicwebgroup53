from flask import Blueprint, render_template, url_for,redirect, send_from_directory, flash
from flask import request
from models.models import SongModel, LikeModel, PlaylistModel, PlaylistSongModel, CommentModel
from extensions.exts import db
from flask_login import current_user, login_required
import os

bp = Blueprint("song", __name__)

@bp.route('/covers/<path:filename>')
def serve_cover(filename):
    user_dir = os.path.dirname(filename)

    return send_from_directory(
        os.path.join('uploads', 'covers', user_dir), 
        os.path.basename(filename),
        mimetype='image/jpeg'
    )
@bp.route('/audios/<path:filename>')
def serve_audio(filename):
        
    user_dir = os.path.dirname(filename)
    return send_from_directory(
        os.path.join('uploads', 'audios', user_dir),
        os.path.basename(filename),
        mimetype='audio/mpeg'
    )

@bp.route('/song/<int:song_id>')
def song_detail(song_id):
    song = db.session.query(SongModel).filter(
    SongModel.id == song_id,
    SongModel.is_approved == True
    ).first()
    is_liked = False
    is_collected = False

    if current_user.is_authenticated:
        collection = PlaylistModel.query.filter_by(
            user_id=current_user.id,
            title="My Collection"
        ).first()

        is_collected = PlaylistSongModel.query.filter_by(
        playlist_id=collection.id,
        song_id=song_id
        ).first() is not None

        if not collection:
            collection = PlaylistModel(
                user_id=current_user.id,
                title="My Collection",
                is_public=False
            )
            db.session.add(collection)
            db.session.commit()

    
    if current_user.is_authenticated:
        is_liked = LikeModel.query.filter_by(
            user_id=current_user.id,
            song_id=song_id
        ).first() is not None


    
    comments = song.comments.filter_by(is_approved=True).order_by(CommentModel.created_at.desc()).all()
    
    return render_template('detail.html',
                         song=song,
                         is_collected=is_collected,
                         is_liked=is_liked,
                         comments=comments)

@bp.route('/like/<int:song_id>', methods=['POST'])
@login_required
def like_song(song_id):
    existing_like = LikeModel.query.filter_by(
        user_id=current_user.id,
        song_id=song_id
    ).first()
    
    if existing_like:
        return redirect(url_for('song.song_detail', song_id=song_id))
    
    liked = LikeModel(user_id=current_user.id, song_id=song_id)
    db.session.add(liked)
    db.session.commit()
    return redirect(url_for('song.song_detail', song_id=song_id))

@bp.route('/dislike/<int:song_id>', methods=['POST'])
@login_required
def dislike_song(song_id):
    dislike = LikeModel.query.filter_by(
        user_id=current_user.id,
        song_id=song_id
    ).first()
    
    if not dislike:
        return redirect(url_for('song.song_detail', song_id=song_id))
    
    db.session.delete(dislike)
    db.session.commit()
    return redirect(url_for('song.song_detail', song_id=song_id))



@bp.route('/collect/<int:song_id>', methods=['POST'])
@login_required
def collect_song(song_id):
    collection = PlaylistModel.query.filter_by(
        user_id=current_user.id,
        title="My Collection"
    ).first()

    existing = PlaylistSongModel.query.filter_by(
        playlist_id=collection.id,
        song_id=song_id
    ).first()
    
    if existing:
        flash('This song is already in your collection', 'info')
    else:
        max_position = db.session.query(db.func.max(PlaylistSongModel.position)).filter_by(
            playlist_id=collection.id
        ).scalar() or 0
        
        playlist_song = PlaylistSongModel(
            playlist_id=collection.id,
            song_id=song_id,
            position=max_position + 1
        )
        db.session.add(playlist_song)
        db.session.commit()
        flash('Song added to your collection', 'success')
    
    return redirect(url_for('song.song_detail', song_id=song_id))

@bp.route('/uncollect/<int:song_id>', methods=['POST'])
@login_required
def uncollect_song(song_id):
    collection = PlaylistModel.query.filter_by(
        user_id=current_user.id,
        title="My Collection"
    ).first()
    
    if collection:
        playlist_song = PlaylistSongModel.query.filter_by(
            playlist_id=collection.id,
            song_id=song_id
        ).first()
        
        if playlist_song:
            db.session.delete(playlist_song)
            db.session.commit()
            flash('Song removed from your collection', 'success')
    
    return redirect(url_for('song.song_detail', song_id=song_id))

@bp.route('/add_to_playlist/<int:song_id>', methods=['POST'])
@login_required
def add_to_playlist(song_id):
    playlist_id = request.form.get('playlist_id')
    
    if not playlist_id:
        flash('Please select a playlist', 'error')
        return redirect(url_for('song.song_detail', song_id=song_id))
    
    playlist = PlaylistModel.query.filter_by(
        id=playlist_id,
        user_id=current_user.id
    ).first()
    
    if not playlist:
        flash('Playlist not found', 'error')
        return redirect(url_for('song.song_detail', song_id=song_id))
    

    existing = PlaylistSongModel.query.filter_by(
        playlist_id=playlist.id,
        song_id=song_id
    ).first()
    
    if existing:
        flash('This song is already in the playlist', 'info')
    else:
        max_position = db.session.query(db.func.max(PlaylistSongModel.position)).filter_by(
            playlist_id=playlist.id
        ).scalar() or 0
        
        playlist_song = PlaylistSongModel(
            playlist_id=playlist.id,
            song_id=song_id,
            position=max_position + 1
        )
        db.session.add(playlist_song)
        db.session.commit()
        flash(f'Song added to {playlist.title}', 'success')
    
    return redirect(url_for('song.song_detail', song_id=song_id))

@bp.route('/song/<int:song_id>/comment', methods=['POST'])
@login_required
def add_comment(song_id):
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('song.song_detail', song_id=song_id))
    

    new_comment = CommentModel(
        content=content,
        user_id=current_user.id,
        song_id=song_id 
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('song.song_detail', song_id=song_id))

@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = CommentModel.query.get_or_404(comment_id)
    
    if current_user.id != comment.user_id and not current_user.is_admin:
        flash('You are not authorized to delete this comment', 'error')
        return redirect(url_for('song.song_detail', song_id=comment.song_id))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully', 'success')
    return redirect(url_for('song.song_detail', song_id=comment.song_id))