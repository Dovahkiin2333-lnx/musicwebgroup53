from flask import (
    Blueprint,
    jsonify,
    render_template,
    request
)
from extensions.exts import db, socketio
from models.models import (
    FriendshipModel,
    MessageModel,
    UserModel
)
from flask_login import current_user, login_required
from datetime import datetime

bp = Blueprint("message", __name__)

@bp.route("/sections/messages")
@login_required
def load_upload_section():
    return render_template(
        "profile/sections/message.html")

@bp.route('/friends')
@login_required
def get_friends():
    friendships = FriendshipModel.query.filter(
        (FriendshipModel.user_id == current_user.id) |
        (FriendshipModel.friend_id == current_user.id)
    ).all()
    
    friend_ids = set()
    for f in friendships:
        if f.user_id == current_user.id:
            reverse = FriendshipModel.query.filter_by(
                user_id=f.friend_id,
                friend_id=current_user.id
            ).first()
            if reverse:
                friend_ids.add(f.friend_id)
        else:
            reverse = FriendshipModel.query.filter_by(
                user_id=current_user.id,
                friend_id=f.user_id
            ).first()
            if reverse:
                friend_ids.add(f.user_id)
    
    friends = UserModel.query.filter(UserModel.id.in_(friend_ids)).all()
    
    friends_data = [{
        'id': friend.id,
        'username': friend.username
    } for friend in friends]
    
    return jsonify({'success': True, 'friends': friends_data})


@bp.route('/history')
@login_required
def get_message_history():
    friend_id = request.args.get('friend_id')

    
    messages = MessageModel.query.filter(
        ((MessageModel.sender_id == current_user.id) & (MessageModel.recipient_id == friend_id)) |
        ((MessageModel.sender_id == friend_id) & (MessageModel.recipient_id == current_user.id))
    ).order_by(MessageModel.timestamp.asc()).all()
    
    messages_data = [{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'recipient_id': msg.recipient_id,
        'body': msg.body,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages]
    
    return jsonify({'success': True, 'messages': messages_data})


@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()

    message = MessageModel(
        sender_id=current_user.id,
        recipient_id=data['recipient_id'],
        body=data['message'],
        timestamp=datetime.now()
    )
    db.session.add(message)
    db.session.commit()
    
    socketio.emit('new_message', {
        'id': message.id,
        'sender_id': current_user.id,
        'recipient_id': data['recipient_id'],
        'body': data['message'],
        'timestamp': message.timestamp.isoformat()
    }, room=str(data['recipient_id']))
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'sender_id': current_user.id,
            'recipient_id': data['recipient_id'],
            'body': data['message'],
            'timestamp': message.timestamp.isoformat()
        }
    })

@socketio.on('friend_request')
def handle_friend_request(data):
    sender_id = data['sender_id']
    recipient_id = data['recipient_id']
    
    existing = FriendshipModel.query.filter_by(
        user_id=sender_id,
        friend_id=recipient_id
    ).first()
    
    if not existing:
        new_request = FriendshipModel(
            user_id=sender_id,
            friend_id=recipient_id
        )
        db.session.add(new_request)
        db.session.commit()
        
        socketio.emit('friend_request_received', {
            'sender_id': sender_id,
            'sender_name': UserModel.query.get(sender_id).username
        }, room=str(recipient_id))
        
        socketio.emit('friend_request_sent', {
            'recipient_id': recipient_id
        }, room=str(sender_id))

@socketio.on('accept_friend_request')
def handle_accept_friend(data):
    original_request = FriendshipModel.query.filter_by(
        user_id=data['sender_id'],
        friend_id=data['recipient_id']
    ).first()
    
    if original_request:
        reverse_friendship = FriendshipModel(
            user_id=data['recipient_id'],
            friend_id=data['sender_id']
        )
        db.session.add(reverse_friendship)
        db.session.commit()
        
        socketio.emit('friendship_established', {
            'friend_id': data['sender_id'],
            'friend_name': UserModel.query.get(data['sender_id']).username
        }, room=str(data['recipient_id']))
        
        socketio.emit('friendship_established', {
            'friend_id': data['recipient_id'],
            'friend_name': UserModel.query.get(data['recipient_id']).username
        }, room=str(data['sender_id']))
