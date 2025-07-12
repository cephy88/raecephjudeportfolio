from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import TextArea
from models import Category

class CKEditorWidget(TextArea):
    """Custom widget for CKEditor"""
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super().__call__(field, **kwargs)

class CKEditorField(TextAreaField):
    widget = CKEditorWidget()

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    content = CKEditorField('Content', validators=[DataRequired()])
    excerpt = TextAreaField('Excerpt', validators=[Optional(), Length(max=500)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published')])
    featured_image = StringField('Featured Image URL', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = [(0, 'Select Category')] + [(c.id, c.name) for c in Category.query.all()]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    color = StringField('Color', validators=[Optional(), Length(max=7)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])