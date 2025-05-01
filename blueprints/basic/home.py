from flask import Blueprint, render_template
from flask import request
from models.models import SongModel, LikeModel
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from flask_login import current_user
from extensions.exts import db

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    songs = db.session.scalars(
        select(SongModel)
        .where(SongModel.is_approved == True)
        .order_by(desc(SongModel.release_date))
        .limit(9)
    ).all()
    
    rec_song_ids = []
    if current_user.is_authenticated:
        liked_song_ids = [like.song_id for like in 
            LikeModel.query.filter_by(user_id=current_user.id).all()]
        if liked_song_ids:
            recommendations = (
                db.session.query(LikeModel.song_id)
                .filter(
                    LikeModel.song_id.notin_(liked_song_ids),
                    LikeModel.user_id.in_(
                        select(LikeModel.user_id)
                        .where(
                            LikeModel.song_id.in_(liked_song_ids),
                            LikeModel.user_id != current_user.id
                        )
                        .group_by(LikeModel.user_id)
                    )
                )
                .group_by(LikeModel.song_id)
                .order_by(func.count().desc())
                .limit(3)
                .all()
            )
            rec_song_ids = [r.song_id for r in recommendations]
    
    if len(rec_song_ids) < 5:
        remaining = max(0, 5 - len(rec_song_ids))
        hot_songs = db.session.scalars(
        select(SongModel.id)
        .where(SongModel.is_approved == True)
        .join(LikeModel, SongModel.id == LikeModel.song_id, isouter=True)
        .group_by(SongModel.id)
        .order_by(func.count(LikeModel.id).desc())
        .limit(remaining)
        ).all()
        rec_song_ids.extend(hot_songs)
        if len(rec_song_ids) < 5:
            new_songs = db.session.scalars(
                select(SongModel.id)
                .where(SongModel.is_approved == True)
                .order_by(desc(SongModel.release_date))
                .limit(5 - len(rec_song_ids))
            ).all()
            rec_song_ids.extend(new_songs)
    
    recommended_songs = db.session.scalars(
        select(SongModel)
        .where(SongModel.id.in_(rec_song_ids))
    ).all()
    
    return render_template(
        "home.html",
        songs=songs,
        recs=recommended_songs
    )





@bp.route('/category', methods=['POST'])
def category():
    keyword = request.form.get("keyword")
    songs = db.session.scalars(
        select(SongModel)
        .where(SongModel.category == keyword)
        .where(SongModel.is_approved == True)
    ).all()
    return render_template('home.html', songs=songs)
