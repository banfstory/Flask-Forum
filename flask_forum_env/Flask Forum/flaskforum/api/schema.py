from flaskforum import db, ma

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','username')

class ForumSchema(ma.Schema):
    class Meta:
        fields = ('id','name','date_created','about','display_picture','num_of_post', 'owner_id')

class PostSchema(ma.Schema):
    class Meta:
        fields = ('id','title','date_posted','content','num_of_comments','user_id','forum_id')

class CommentSchema(ma.Schema):
    class Meta:
        fields = ('id','content','date_commented','num_of_reply','user_id','post_id')

class ReplySchema(ma.Schema):
    class Meta:
        fields = ('id','content','date_rely','user_id','comment_id')

user_schema = UserSchema() 
users_schema = UserSchema(many=True)
forum_schema = ForumSchema() 
forums_schema = ForumSchema(many=True)
post_schema = PostSchema() 
posts_schema = PostSchema(many=True)
comment_schema = CommentSchema() 
comments_schema = CommentSchema(many=True)
reply_schema = ReplySchema() 
replys_schema = ReplySchema(many=True)
forum_schema = ForumSchema()
