from flaskforum.models import Forum
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed

class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])
    submit = SubmitField('Post')

class CreateForum(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    about = TextAreaField('About', validators=[InputRequired()])
    submit = SubmitField('Create Forum')

    def validate_name(self, name): 
        name = Forum.query.filter_by(name=name.data).first()
        if name:
            raise ValidationError('That Forum name is taken. Please choose another')

class UpdateForum(FlaskForm):
    about = TextAreaField('About', validators=[InputRequired()])
    picture = FileField('Update Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update Forum')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[InputRequired()])
    submit = SubmitField('Comment')

class ReplyForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[InputRequired()])
    submit = SubmitField('Reply')

class SearchForm(FlaskForm):
    search = StringField('Search')