
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_babel import _


class ContactForm(FlaskForm):
    name = StringField(_('Nombre'), validators=[DataRequired(message=_('Este campo es obligatorio.'))])
    email = StringField('Correo Electrónico', validators=[DataRequired(message=_('Este campo es obligatorio.'))])
    message = TextAreaField('Mensaje', validators=[DataRequired(message=_('Este campo es obligatorio.'))])
    submit = SubmitField('Enviar')
