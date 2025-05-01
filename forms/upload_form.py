from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField, SelectField, DateField, FileField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length, Optional



MUSIC_CATEGORIES = [
    ('happy', 'happy'),
    ('relax', 'relax'),
    ('modern', 'modern'),
    ('vocal', 'vocal'),
    ('432Hz', '432Hz')  
]

class ImageUploadForm(FlaskForm):
    avatar = FileField('avatar', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        lambda form, field: validate_file_size(field, max_size=100),  
        lambda form, field: validate_filename(field),
    ])
    submit = SubmitField('Upload')

def validate_file_size(field, max_size):
    max_bytes = max_size * 1024 * 1024
    file_data = field.data
    file_data.seek(0, 2)  
    file_size = file_data.tell() 
    file_data.seek(0) 
    
    if file_size > max_bytes:
        raise ValidationError(f'File size must be less than {max_size}MB.')

def validate_filename(field):
    filename = field.data.filename
    if not filename:
        raise ValidationError('No file selected.')

    parts = filename.rsplit('.', 1)
    if len(parts) != 2:
        raise ValidationError('Filename must have an extension (e.g., .jpg).')
    
    name, ext = parts
    if '.' in name:
        raise ValidationError('Filename cannot contain "." (except for the extension).')
    if len(name) > 50:
        raise ValidationError('Filename must be ≤50 characters (excluding extension).')
    


class MusicUploadForm(FlaskForm):
    title = StringField('Song Title', validators=[
        DataRequired(message="Song title is required"),
        Length(max=100, message="Title cannot exceed 100 characters")
    ])
    
    artist = StringField('Artist', validators=[
        DataRequired(message="Artist name is required"),
        Length(max=100, message="Artist name cannot exceed 100 characters")
    ])
    
    category = SelectField('Category', choices=MUSIC_CATEGORIES, validators=[Optional()])
    
    release_date = DateField('Release Date', format='%Y-%m-%d', validators=[Optional()])
    
    cover = FileField('Cover Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG/PNG images allowed'),
        lambda form, field: validate_file_size(field, max_size=10) 
    ])
    
    audio = FileField('Audio File', validators=[
        DataRequired(message="Audio file is required"),
        FileAllowed(['mp3', 'wav', 'ogg'], 'Only MP3/WAV/OGG audio allowed'),
        lambda form, field: validate_file_size(field, max_size=500), 
        lambda form, field: validate_filename(field)
    ])