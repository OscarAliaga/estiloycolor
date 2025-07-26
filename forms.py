from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_babel import _

class ContactForm(FlaskForm):
    name = StringField(_('Nombre'), validators=[
        DataRequired(message=_('Este campo es obligatorio.'))
    ])

    email = StringField(_('Correo Electrónico'), validators=[
        DataRequired(message=_('Este campo es obligatorio.')),
        Email(message=_('Ingrese un correo válido.'))
    ])

    phone = StringField(_('Teléfono'))  # opcional: puedes añadir validaciones de formato

    from flask_babel import _

    subject = SelectField(_('Motivo de contacto'), choices=[
        ('consulta', _('Consulta general')),
        ('asesoria', _('Agendar asesoría')),
        ('colaboracion', _('Colaboración o invitación')),
        ('otro', _('Otro'))
    ])

    message = TextAreaField(_('Mensaje'), validators=[
        DataRequired(message=_('Este campo es obligatorio.'))
    ])

    consent = BooleanField(_('Acepto el uso de mis datos para ser contactada.'), validators=[
        DataRequired(message=_('Debes aceptar el uso de tus datos para continuar.'))
    ])

    submit = SubmitField(_('Enviar'))
