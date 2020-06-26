from flask import Blueprint
from flaskforum import db
from flaskforum.users.utils import save_picture
from flask import render_template, url_for, flash, redirect, request, abort
from flaskforum.forums.forms import PostForm, CreateForum, CommentForm, ReplyForm, SearchForm, UpdateForum
from flaskforum.models import Post, Forum, Comment, Reply, User
from flask_login import current_user, login_required


forums = Blueprint('forums', __name__)

@forums.route('/forum/<string:name>')
def forum(name):
    searchForm = SearchForm()
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    forum = db.session.query(Forum, db.func.strftime('%d-%m-%Y',Forum.date_created)).filter_by(name=name).first_or_404() 
    forum_followers = len(Forum.query.filter_by(id=forum[0].id).first().follow_forum)
    follow_forum = User.query.filter_by(id=current_user.id).first().follow.filter_by(id=forum[0].id).first() if current_user.is_authenticated else None
    page = request.args.get('page',1,type=int) #represented as a '?page='
    # get the post, hours since the post was made, count the number of comments for the next 10 posts from a certain start point
    posts = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24,db.func.count(Comment.post_id)).order_by(Post.date_posted.desc())\
        .outerjoin(Comment, Post.id==Comment.post_id).group_by(Post.id).filter(Post.forum_id==forum[0].id).paginate(page=page, per_page=10)
    #posts = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24).order_by(Post.date_posted.desc()).filter_by(forum_id=forum[0].id).paginate(page=page, per_page=10)
    return render_template('forum.html', follow=follow, posts=posts, forum=forum, searchForm=searchForm, follow_forum=follow_forum, title=forum[0].name, forum_followers=forum_followers)

@forums.route('/forum/<string:name>/create_post', methods=['GET','POST'])
@login_required
def create_post(name):
    searchForm = SearchForm()   
    form = PostForm()
    forum = Forum.query.filter_by(name=name).first_or_404()
    if form.validate_on_submit():
        forum.num_of_post+=1
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id, forum_id=forum.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('forums.forum', name=name))
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    forum = Forum.query.filter_by(name=name).first_or_404()
    return render_template('forum_create_post.html', follow=follow, forum=forum, form=form, searchForm=searchForm, title= forum.name + " - Create Post")

@forums.route('/create_forum', methods=['GET','POST'])
@login_required
def create_forum():
    searchForm = SearchForm()
    form = CreateForum()
    if form.validate_on_submit():
        forum = Forum(name=form.name.data, about=form.about.data, owner_id=current_user.id)
        db.session.add(forum)
        db.session.commit()
        return redirect(url_for('main.home'))
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    return render_template('create_forum.html', follow=follow, form=form, searchForm=searchForm, title="Create Forum")

@forums.route('/forum/<int:id>/comments')
def comments(id):
    searchForm = SearchForm()
    replyForm = ReplyForm()
    per_p = 10
    post = db.session.query(Post, (db.func.julianday('now')-db.func.julianday(Post.date_posted))*24, db.func.count(Comment.post_id)).outerjoin(Comment, Post.id==Comment.post_id)\
        .filter(Post.id==id).first_or_404()
    #post = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24).filter_by(id=id).first_or_404()
    forum_followers = len(Forum.query.filter_by(id=post[0].forum.id).first().follow_forum)
    forum_date = db.session.query(Forum, db.func.strftime('%d-%m-%Y',Forum.date_created)).filter_by(id=post[0].forum_id).first()
    page = request.args.get('page',1,type=int)
    # get the comment, hours since the comment was made, count the number of replys for the next 10 comments from a certain start point of that post
    post_comments = db.session.query(Comment, (db.func.julianday('now')-db.func.julianday(Comment.date_commented))*24, db.func.count(Reply.comment_id))\
        .outerjoin(Reply, Comment.id == Reply.comment_id).filter(Comment.post_id==id).group_by(Comment.id).order_by(Comment.date_commented.desc()).paginate(page=page, per_page=per_p)
    #post_comments = db.session.query(Comment,(db.func.julianday('now')-db.func.julianday(Comment.date_commented))*24).order_by(Comment.date_commented.desc()).filter_by(post_id=id).paginate(page=page, per_page=10)
    comment = CommentForm()
    reply = ReplyForm()
    # get the reply, some of the user data, hours since the reply was made and only select the reply of the next 10 comments from starting point of that post
    temp_reply = db.engine.execute('SELECT Reply.*, User.username, User.display_picture, User.id as u_id, (julianday("now")-julianday(date_reply))*24 as date \
        FROM Reply INNER JOIN User ON Reply.user_id=User.id WHERE Reply.comment_id IN(SELECT id FROM Comment WHERE post_id=' + str(id) + ' ORDER BY date_commented desc LIMIT ' 
        + str(per_p) + ' OFFSET ' + str(per_p * (page-1)) + ') ORDER BY Reply.date_reply desc')
    #temp_reply = db.engine.execute('SELECT *, (julianday("now")-julianday(date_reply))*24 as date FROM Reply WHERE comment_id IN(SELECT id FROM Comment WHERE post_id=' + str(id) + ') ORDER BY date_reply desc LIMIT ' + str(per_p) + ' OFFSET ' + str(per_p * (page-1)))
    res_reply = dict()
    for t in temp_reply:
       if t.comment_id not in res_reply:
           res_reply[t.comment_id] = list()
       res_reply[t.comment_id].append(t)
    follow_forum = User.query.filter_by(id=current_user.id).first().follow.filter_by(id=post[0].forum_id).first() if current_user.is_authenticated else None
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    return render_template('comments.html', follow_forum=follow_forum, follow=follow, comment=comment, reply=reply, post=post, post_comments=post_comments, searchForm=searchForm, id=id, replyForm=replyForm, title= post[0].title + " - Post", forum_date=forum_date, res_reply=res_reply, forum_followers= forum_followers)

@forums.route('/searchResult', methods=['POST']) # used when search button is clicked
def SearchResult():
    searchForm = SearchForm()
    return redirect(url_for('forums.search', q=searchForm.search.data))

@forums.route('/search') 
def search():
    search = request.args.get('q', type=str)
    if search=='':
        return redirect(url_for('main.home'))
    search = search.lower()
    searchForm = SearchForm()
    searchForm.search.data = search
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    page = request.args.get('page',1,type=int) #represented as a '?page='
    result = Forum.query.order_by(Forum.date_created.desc()).filter(Forum.name.like("%"+search+"%")).paginate(page=page, per_page=15) 
    return render_template('search_results.html', follow=follow, searchForm=searchForm, result=result, search=search, title="Search Results")
    
@forums.route('/forum/<int:id>/update_post', methods=['GET','POST'])
@login_required
def update_post(id):
    form = PostForm()
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('forums.comments', id=id))
    elif request.method == 'GET':  # prevent post from been changed if it is a POST and form is invalid as it needs to show the data that was typed in
        form.title.data = post.title
        form.content.data = post.content
    searchForm = SearchForm()
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    forum = post.forum
    return render_template('post_update.html', follow=follow, forum=forum, form=form, searchForm=searchForm, post=post, title= post.title + " - Update post")

@forums.route('/forum/<int:id>/delete_post', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    name = post.forum.name
    if post.author != current_user:
        abort(403)
    comment = Comment.query.filter_by(post_id=id) 
    reply = Reply.query.filter_by(comment_id=comment.first().id) if comment == None else None # if no comment exist for this post then reply is none
    if reply:
        reply.delete() #multiple rows deleted at once
    if comment:
        comment.delete() #multiple rows deleted at once
    post.forum.num_of_post-=1
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('forums.forum', name=name))
    
@forums.route('/forum/<int:id>/update_forum', methods=['GET','POST'])
@login_required
def update_forum(id): 
    form = UpdateForum() 
    forum = Forum.query.get_or_404(id)
    if forum.owner != current_user:
        abort(403)
    image_file = url_for('static', filename='forum_pics/' + forum.display_picture)
    if form.validate_on_submit(): 
        if form.picture.data: # if user has not attached a file into the picture form than dont do anything with the picture
            picture_file=save_picture(form.picture.data, 'forum_pics')
            forum.display_picture = picture_file
        forum.about = form.about.data
        db.session.commit()
        return redirect(url_for('forums.update_forum', id=id))
    elif request.method == 'GET': # prevent post from been changed if it is a POST and form is invalid as it needs to show the data that was typed in
        form.about.data = forum.about       
    searchForm = SearchForm()
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    return render_template('forum_update.html', follow=follow, forum=forum, form=form, searchForm=searchForm, image_file=image_file, title= forum.name + " - Update forum")

@forums.route("/forum/<int:id>/remove_picture", methods=['POST'])
@login_required
def forum_remove_pic(id):
    forum = Forum.query.get_or_404(id)
    if current_user.is_authenticated and forum.owner == current_user:
        forum.display_picture = 'default.png'
        db.session.commit()
        return redirect(url_for('forums.update_forum', id=id))
    else:
        abort(403)

@forums.route('/forum/<int:id>/update_comment', methods=['POST'])
@login_required
def update_comment(id): 
    form = CommentForm() 
    comment = Comment.query.get_or_404(id)
    if comment.comment_user != current_user:
        abort(403)
    if form.validate_on_submit(): 
        comment.content = form.comment.data
        db.session.commit()
    page = request.args.get('page',1,type=int) #represented as a '?page='
    return redirect(url_for('forums.comments', id=comment.comment_post.id, page=page))

@forums.route('/forum/<int:id>/update_reply', methods=['POST'])
@login_required
def update_reply(id): 
    form = ReplyForm() 
    reply = Reply.query.get_or_404(id)
    if reply.reply_user != current_user:
        abort(403)
    if form.validate_on_submit(): 
        reply.content = form.comment.data
        db.session.commit()
    page = request.args.get('page',1,type=int) #represented as a '?page='
    return redirect(url_for('forums.comments', id=reply.reply.comment_post.id, page=page))

@forums.route('/forum/<int:id>/delete_comment', methods=['POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.comment_user!=current_user:
        abort(403)
    post_id = comment.comment_post.id
    reply = Reply.query.filter_by(comment_id=comment.id)
    if reply:
        reply.delete() #multiple rows deleted at once
    comment.comment_post.num_of_comments-=1
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('forums.comments', id=post_id))

@forums.route('/forum/<int:id>/delete_reply', methods=['POST'])
@login_required
def delete_reply(id):
    reply = Reply.query.get_or_404(id)
    if reply.reply_user!=current_user:
        abort(403)
    post_id = reply.reply.comment_post.id
    reply.reply.num_of_reply-=1
    db.session.delete(reply)
    db.session.commit()
    page = request.args.get('page',1,type=int) #represented as a '?page='
    return redirect(url_for('forums.comments', id=post_id, page=page))

@forums.route('/forum/<int:id>/comments/post_comment', methods=['POST'])
@login_required
def post_comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id=id).first()
        post.num_of_comments+=1
        comment = Comment(content=form.comment.data, user_id=current_user.id, post_id=id)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('forums.comments', id=id))

@forums.route('/forum/<int:id>/comments/reply_comment', methods=['POST'])
@login_required
def reply_comment(id):
    form = ReplyForm()
    comment = Comment.query.filter_by(id=id).first()
    page = request.args.get('page',1,type=int) #represented as a '?page='
    if form.validate_on_submit():
        comment.num_of_reply+=1
        reply = Reply(content=form.comment.data, comment_id=id, user_id=current_user.id)
        db.session.add(reply)
        db.session.commit()
    return redirect(url_for('forums.comments', id=comment.comment_post.id, page=page))