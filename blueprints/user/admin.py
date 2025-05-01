from flask import Blueprint, request, render_template, flash, redirect, url_for, current_app
from sqlalchemy import select, desc,func
from models.models import SongModel, UserModel, NotificationModel, CommentModel, ProfileModel, SearchIndexModel, LikeModel
from extensions.exts import db
from flask_login import current_user
from utils.decorators import roles_required
from utils.delete_process import delete_song, delete_user
from datetime import datetime

bp = Blueprint("admin", __name__)

@bp.route('/audit')
@roles_required('admin', 'sadmin')
def audit():
    unapproved_avatars = db.session.scalars(
        select(ProfileModel)
        .where(ProfileModel.avatar_filename.is_not(None))
        .where(ProfileModel.avatar_approved == False)
    ).all()
    unapproved_descriptions = db.session.scalars(
        select(ProfileModel)
        .where(ProfileModel.description.is_not(None))
        .where(ProfileModel.description_approved == False)
    ).all()
    unapproved_songs = db.session.scalars(
        select(SongModel)
        .where(SongModel.is_approved == False)
    ).all()
    unapproved_comments = CommentModel.query.filter_by(is_approved=False).all()

    return render_template('admin/audit.html',
                            unapproved_avatars=unapproved_avatars,
                            unapproved_descriptions=unapproved_descriptions,
                            unapproved_songs=unapproved_songs,
                            unapproved_comments=unapproved_comments)


@bp.route('/process_avatar', methods=['POST'])
@roles_required('admin', 'sadmin')
def process_avatar():
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    profile = ProfileModel.query.filter_by(user_id=user_id).first()
    if profile:
        if action == 'approve':
            profile.avatar_approved = True
            NotificationModel.send_notification(
                receiver_id=profile.user_id,
                content=f"Your avatar was approved. Reason: {reason}",
                sender_id=current_user.id 
                )
        else:
            NotificationModel.send_notification(
                receiver_id=profile.user_id,
                content=f"Your avatar was rejected. Reason: {reason}",
                sender_id=current_user.id 
                )
        
        db.session.commit()
    
    return redirect(url_for('admin.audit'))

@bp.route('/process_description', methods=['POST'])
@roles_required('admin', 'sadmin')
def process_description():
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    profile = ProfileModel.query.filter_by(user_id=user_id).first()
    if profile:
        if action == 'approve':
            profile.description_approved = True
            NotificationModel.send_notification(
                receiver_id=profile.user_id,
                content=f"Your description was approved. Reason: {reason}",
                sender_id=current_user.id 
                )
        else:
            NotificationModel.send_notification(
                receiver_id=profile.user_id,
                content=f"Your description was rejected. Reason: {reason}",
                sender_id=current_user.id 
                )
        
        db.session.commit()
    
    return redirect(url_for('admin.audit'))

@bp.route('/process_song', methods=['POST'])
@roles_required('admin', 'sadmin')
def process_song():
    song_id = request.form.get('song_id')
    song_title = request.form.get('song_title')
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    song = SongModel.query.filter_by(id=song_id).first()
    index = SearchIndexModel.query.filter(
    SearchIndexModel.content_id == song_id,
    SearchIndexModel.content_type == 'song'
    ).first()

    if song:
        if action == 'approve':
            song.is_approved = True
            index.is_approved = True
            NotificationModel.send_notification(
                receiver_id=song.uploader_id,
                content=f"Your music {song_title} was approved. Reason: {reason}",
                sender_id=current_user.id 
                )
        else:
            NotificationModel.send_notification(
                receiver_id=song.uploader_id,
                content=f"Your music {song_title} was denied. Reason: {reason}",
                sender_id=current_user.id 
                )
        
        db.session.commit()
    
    return redirect(url_for('admin.audit'))

@bp.route('/process_comment', methods=['POST'])
@roles_required('admin', 'sadmin')
def process_comment():
    comment_id = request.form.get('comment_id')
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    comment = CommentModel.query.filter_by(id=comment_id).first()
    if comment:
        if action == 'approve':
            comment.is_approved = True
            NotificationModel.send_notification(
                receiver_id=comment.user_id,
                content=f"Your comment was approved. Reason: {reason}",
                sender_id=current_user.id 
                )
        else:
            NotificationModel.send_notification(
                receiver_id=comment.user_id,
                content=f"Your avatar was rejected. Reason: {reason}",
                sender_id=current_user.id 
                )
        
        db.session.commit()
    
    return redirect(url_for('admin.audit'))



@bp.route("/manage", methods=["GET", "POST"])
@roles_required("sadmin", "admin")
def manage():
    if request.method == "GET":
        songs = db.session.scalars(select(SongModel).order_by(desc(SongModel.id))).all()
        users = db.session.scalars(select(UserModel).order_by(desc(UserModel.id))).all()
        
        return render_template(
            "admin/manage.html", 
            songs=songs, 
            users=users
        )
    
@bp.route("/reports")
@roles_required("sadmin", "admin")
def reports():
    category_stats = get_category_stats()
    return render_template(
        "admin/reports.html",
        category_stats = category_stats,
        now = datetime.now()
    )

def get_category_stats():
    all_categories = ['happy', 'relax', 'modern', 'vocal', '432Hz']
    stats = db.session.execute(
        select(
            SongModel.category,
            func.count(LikeModel.id).label('count')
        )
        .join(LikeModel, SongModel.id == LikeModel.song_id, isouter=True)
        .where(SongModel.is_approved == True)
        .group_by(SongModel.category)
    ).all()
    
    stats_dict = {category: count for category, count in stats}

    result = []
    for category in all_categories:
        result.append({
            'category': category,
            'count': stats_dict.get(category, 0)
        })
    
    return result


@bp.route('/change_role', methods=['POST'])
@roles_required("sadmin", "admin")
def change_role():
    try:
        user_id = request.form.get('user_id')
        new_role = request.form.get('new_role')
        
        if not user_id or not new_role:
            flash('Missing required parameters', 'error')
            return redirect(url_for('admin.manage'))
            
        user = UserModel.query.get(user_id)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin.manage'))
            
        valid_roles = ['user', 'student', 'admin']
        if new_role not in valid_roles:
            flash('Invalid role specified', 'error')
            return redirect(url_for('admin.manage'))
            
        if new_role == 'student' and not user.student_id:
            flash('Cannot set role to student without student ID', 'error')
            return redirect(url_for('admin.manage'))
            
        user.role = new_role
        db.session.commit()
        flash('User role updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing user role: {str(e)}")
        flash('Failed to update user role', 'error')
        
    return redirect(url_for('admin.manage'))


@bp.route('/delete_user', methods=['POST'])
@roles_required("sadmin", "admin")
def delete_user_route():
    try:
        user_id = request.form.get('user_id')
        print(user_id)
        if not user_id:
            flash('User ID is required', 'error')
            return redirect(url_for('admin.manage'))
        user = UserModel.query.get(user_id)    
        print(user.username)
        success, message = delete_user(user_id)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        current_app.logger.error(f"Error in delete_user route: {str(e)}")
        flash('An error occurred while deleting user', 'error')
        
    return redirect(url_for('admin.manage'))
@bp.route('/delete_song', methods=['POST'])
@roles_required("sadmin", "admin")
def delete_song_route():
    try:
        song_id = request.form.get('song_id')
        if not song_id:
            flash('Song ID is required', 'error')
            return redirect(url_for('admin.manage'))
            
        success, message = delete_song(song_id)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        current_app.logger.error(f"Error in delete_song route: {str(e)}")
        flash('An error occurred while deleting song', 'error')
        
    return redirect(url_for('admin.manage'))


