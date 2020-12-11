from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional

#############################################################
# User Account Info Forms
#############################################################

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])

class UserEditForm(FlaskForm):
    """Form for editing user."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired(message="Growing area name required")])
    password = PasswordField('Password', validators=[Length(min=6), DataRequired(message="Password required")])

#############################################################
# Growing Area Forms
#############################################################

class GrowingAreaForm(FlaskForm):
    """Form for adding or editing a growing area in the user's garden."""
    name = StringField('Name', validators=[DataRequired(), Length(max=40)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    light_level = SelectField('Light Level', choices=["Full Sun", "Partial Sun/Shade", "Full Shade"])
    soil_texture = SelectField('Soil Texture', choices=["Clay", "Loam", "Sandy", "Rocky"])
    soil_moisture = SelectField('Soil Moisture', choices=["Dry", "Medium", "Damp", "Wet"])
    soil_ph = FloatField('Soil ph', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Length(max=400)])
    
#############################################################
# Plant List Forms - NewPlantListForm, AddPlantForm
#############################################################

class NewPlantListForm(FlaskForm):
    """Form for creating a new plant list."""
    name = StringField('Name', validators=[DataRequired(), Length(max=30)])
    description = StringField('Description', validators=[Optional(), Length(max=300)])
    growing_area = SelectField('Planting Area', validators=[Optional()])

class AddPlantForm(FlaskForm):
    """Simple form for adding plant to a list."""
    plant_list = SelectField(validators=[DataRequired()])
    plant_id = HiddenField(validators=[DataRequired()])
    plant_slug = HiddenField(validators=[DataRequired()])
    plant_scientific_name = HiddenField(validators=[DataRequired()])
    plant_image_url = HiddenField(validators=[DataRequired()])



# TODO: Advanced Search Form


