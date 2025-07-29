# forms.py (Full Code)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InventoryForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    # START: NEW FIELD FOR THE FORM
    low_stock_threshold = IntegerField('Low Stock Threshold', 
                                       validators=[DataRequired(), NumberRange(min=0)], 
                                       default=5)
    # END: NEW FIELD
    submit = SubmitField('Add Item')

class SaleForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    total_price = FloatField('Total Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Record Sale')