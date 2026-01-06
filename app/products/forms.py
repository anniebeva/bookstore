from flask_wtf import FlaskForm
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import TextAreaField, SubmitField
from wtforms.validators import Length, DataRequired

class ReviewForm(FlaskForm):
    review = TextAreaField(
        'Review',
        validators=[Length(max=1000)],
        render_kw={'rows': 4}
    )

    rating = RadioField(
        'Rating',
        choices=[
            ('1', '⭐'),
            ('2', '⭐⭐'),
            ('3', '⭐⭐⭐'),
            ('4', '⭐⭐⭐⭐'),
            ('5', '⭐⭐⭐⭐⭐'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit review')