from flaskforum import db, bcrypt, app
from flaskforum.models import User
from flask import Blueprint, request, jsonify, make_response
from flaskforum.models import *
from flaskforum.api.schema import *
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_login import current_user

"""
POSTMAN SETTINGS
Headers required : 
    'x-access-token : (token_value) - methods: POST, PUT, DELETE
    'Content-Type : application/json' - methods: POST, PUT
Body required: 
    'raw,JSON' - methods: POST, PUT
"""
api = Blueprint('api', __name__)

#TOKEN
@api.route('/api/login', methods=['GET']) # give token to user that login with valid details
def api_login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message' : 'Unauthorized Access'}), 401
    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return jsonify({'message' : 'Unauthorized Access'}), 401
    if bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.username, 'exp' : datetime.utcnow() + timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return jsonify({'message' : 'Unauthorized Access'}), 401

def token_required(verify_token): # verify token that has been given
    @wraps(verify_token)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query.filter_by(username=data['public_id']).first()
        except:
            return jsonify({'message' : 'Invalid Token'}), 401
        return verify_token(user, *args, **kwargs)
    return decorated

#POST METHODS
@api.route('/api/post', methods=['POST'])
@token_required
def api_create_post(c_user):
    data = request.get_json()
    title = data['title']
    content = data['content']
    forum_id = data['forum_id']
    forum = Forum.query.get(forum_id)
    if forum is None:
        return jsonify({'message' : 'Invalid request'})
    post = Post(title=title, content=content, forum_id=forum_id, user_id=c_user.id)
    db.session.add(post)
    forum.num_of_post += 1
    db.session.commit()
    result = post_schema.dump(post)
    return jsonify({'post' : result})

@api.route('/api/comment', methods=['POST'])
@token_required
def api_create_comment(c_user):
    data = request.get_json()
    content = data['content']
    post_id = data['post_id']
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({'message' : 'Invalid request'})
    comment = Comment(content=content, post_id=post_id, user_id=c_user.id)
    db.session.add(comment)
    post.num_of_comments += 1
    db.session.commit()
    result = comment_schema.dump(comment)
    return jsonify({'comment' : result})

@api.route('/api/reply', methods=['POST'])
@token_required
def api_create_reply(c_user):
    data = request.get_json()
    content = data['content']
    comment_id = data['comment_id']
    comment = Comment.query.get(comment_id)
    if comment is None:
        return jsonify({'message' : 'Invalid request'})
    reply = Reply(content=content, comment_id=comment_id, user_id=c_user.id)
    db.session.add(reply)
    comment.num_of_reply += 1
    db.session.commit()
    result = reply_schema.dump(comment)
    return jsonify({'reply' : result})

@api.route('/api/forum', methods=['POST'])
@token_required
def api_create_forum(c_user):
    data = request.get_json()
    name = data['name']
    about = data['about']
    forum = Forum(name=name, about=about, owner_id=c_user.id)
    db.session.add(forum)
    db.session.commit()
    result = forum_schema.dump(forum)
    return jsonify({'forum' : result})

#PUT METHODS
@api.route('/api/post/<int:id>', methods=['PUT'])
@token_required
def api_update_post(c_user, id):
    post = Post.query.filter_by(id=id, user_id=c_user.id).first()
    if post is None:
        return jsonify({'message' : 'Invalid request'})
    data = request.get_json()
    title = data['title']
    content = data['content']
    post.title = title
    post.content = content
    db.session.commit()
    result = post_schema.dump(post)
    return jsonify({'post' : result})

@api.route('/api/comment/<int:id>', methods=['PUT'])
@token_required
def api_update_comment(c_user, id):
    comment = Comment.query.filter_by(id=id, user_id=c_user.id).first()
    if comment is None:
        return jsonify({'message' : 'Invalid request'})
    data = request.get_json()
    content = data['content']
    comment.content = content
    db.session.commit()
    result = comment_schema.dump(comment)
    return jsonify({'comment' : result})

@api.route('/api/reply/<int:id>', methods=['PUT'])
@token_required
def api_update_reply(c_user, id):
    reply = Reply.query.filter_by(id=id, user_id=c_user.id).first()
    if reply is None:
        return jsonify({'message' : 'Invalid request'})
    data = request.get_json()
    content = data['content']
    reply.content = content
    db.session.commit()
    result = reply_schema.dump(reply)
    return jsonify({'reply' : result})

@api.route('/api/forum/<int:id>', methods=['PUT'])
@token_required
def api_update_forum(c_user, id):
    forum = Forum.query.filter_by(id=id, user_id=c_user.id).first()
    if forum is None:
        return jsonify({'message' : 'Invalid request'})
    data = request.get_json()
    about = data['about']
    forum.content = content
    db.session.commit()
    result = forum_schema.dump(forum)
    return jsonify({'forum' : result})

#DELETE METHODS
@api.route('/api/post/<int:id>', methods=['DELETE'])
@token_required
def api_delete_post(c_user,id):
    post = Post.query.filter_by(id=id, user_id=c_user.id).first()
    if post is None:
        return jsonify({'message' : 'Invalid request'})
    comment = Comment.query.filter_by(post_id=post.id)
    reply = db.session.query(Reply).outerjoin(Comment, Comment.id==Reply.comment_id).filter(Comment.post_id==post.id) if comment == None else None # if no comment exist for this post then reply is none
    if reply:
        for r in reply:
            db.session.delete(r)
    if comment:
        comment.delete() #delete comment all at once
    post.forum.num_of_post -= 1
    db.session.delete(post)
    db.session.commit()
    result = post_schema.dump(post)
    return jsonify({'post' : result})

@api.route('/api/comment/<int:id>', methods=['DELETE'])
@token_required
def api_delete_comment(c_user,id):
    comment = Comment.query.filter_by(id=id, user_id=c_user.id)
    if comment is None:
        return jsonify({'message' : 'Invalid request'})
    reply = Reply.query.filter_by(comment_id=comment.id)
    if reply:
        reply.delete() #dlete reply all at once
    comment.comment_post.num_of_comments -= 1
    db.session.delete(comment)
    db.session.commit()
    result = comment_schema.dump(comment)
    return jsonify({'comment' : result})

@api.route('/api/reply/<int:id>', methods=['DELETE'])
@token_required
def api_delete_reply(c_user,id):
    reply = Reply.query.filter(id=id, user_id=c_user.id)
    if reply is None:
        return jsonify({'message' : 'Invalid request'})
    reply.reply.num_of_reply -= 1
    db.session.delete(reply)
    db.session.commit()
    result = reply_schema.dump(reply)
    return jsonify({'reply' : result})

#GET METHODS
@api.route('/api/posts', methods=['GET'])
def api_get_posts():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('limit',5,type=int)
    user_id = request.args.get('user_id',None,type=int)
    forum_id = request.args.get('forum_id',None,type=int)
    if user_id is None and forum_id is None:
        return jsonify({'message' : 'Invalid request'})
    param = dict()
    if user_id:
        param['user_id'] = user_id
    if forum_id:
        param['forum_id'] = forum_id
    try:
        posts = Post.query.filter_by(**param).order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page).items
    except:
        return jsonify({'message' : 'Invalid request'})
    result = posts_schema.dump(posts)
    return jsonify({'posts' : result})

@api.route('/api/post/<int:id>', methods=['GET'])
def api_get_post():
    post = Post.query.get(id)
    if post is None:
        return jsonify({'message' : 'Post not found'})
    post_schema.dump(post)
    return jsonify({'post' : post})

@api.route('/api/comments', methods=['GET'])
def api_get_comments():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('limit',5,type=int)
    user_id = request.args.get('user_id',None,type=int)
    post_id = request.args.get('post_id',None,type=int)
    if user_id is None and post_id is None:
        return jsonify({'message' : 'Invalid request'})
    param = dict()
    if user_id:
        param['user_id'] = user_id
    if post_id:
        param['post_id'] = post_id
    try:
        comments = Comment.query.filter_by(**param).order_by(Comment.date_commented.desc()).paginate(page=page, per_page=per_page).items
    except:
        return jsonify({'message' : 'Invalid request'})
    result = comments_schema.dump(comments)
    return jsonify({'comments' : result})

@api.route('/api/comment/<int:id>', methods=['GET'])
def api_get_comment(id):
    comment = Comment.query.get(id)
    if comment is None:
        return jsonify({'message' : 'Comment not found'})
    comment_schema.dump(comment)
    return jsonify({'comment' : comment})

@api.route('/api/replys', methods=['GET'])
def api_get_replys():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('limit',5,type=int)
    user_id = request.args.get('user_id',None,type=int)
    comment_id = request.args.get('comment_id',None,type=int)
    if user_id is None and comment_id is None:
        return jsonify({'message' : 'Invalid request'})
    param = dict()
    if user_id:
        param['user_id'] = user_id
    if comment_id:
        param['comment_id'] = comment_id
    try:
        replys = Reply.query.filter_by(**param).order_by(Reply.date_reply.desc()).paginate(page=page, per_page=per_page).items
    except:
        return jsonify({'message' : 'Invalid request'})
    result = replys_schema.dump(replys)
    return jsonify({'replys' : result})

@api.route('/api/reply/<int:id>', methods=['GET'])
def api_get_reply(id):
    reply = Reply.query.get(id)
    if reply is None:
        return jsonify({'message' : 'Reply not found'})
    reply_schema.dump(reply)
    return jsonify({'reply' : reply})

@api.route('/api/forums', methods=['GET'])
def api_get_forums():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('limit',5,type=int)
    user_id = request.args.get('user_id',None,type=int)
    if user_id is None:
        return jsonify({'message' : 'Invalid request'})
    param = dict()
    if user_id:
        param['owner_id'] = user_id
    try:
        forums = Forum.query.filter_by(**param).order_by(Forum.date_created.desc()).paginate(page=page, per_page=per_page).items
    except:
        return jsonify({'message' : 'Invalid request'})
    result = forums_schema.dump(forums)
    return jsonify({'forums' : result})

@api.route('/api/forum/<int:id>', methods=['GET'])
def api_get_forum(id):
    forum = Forum.query.get(id)
    if forum is None:
        return jsonify({'message' : 'Forum not found'})
    forum_schema.dump(forum)
    return jsonify({'forum' : forum})

@api.route('/api/user', methods=['GET'])
def api_get_all_user():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('limit',5,type=int)
    users = User.query.all().paginate(page=page, per_page=per_page).items
    result = users_schema.dump(users)
    return jsonify({'users' : result})

@api.route('/api/user/<int:id>', methods=['GET'])
def api_get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'message' : 'User not found'})
    result = user_schema.dump(user)
    return jsonify({'user' : result})

