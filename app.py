from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_babel import Babel, _, get_locale
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()
from config import Config
from models import db, Contact
from forms import ContactForm
import os
import re

app = Flask(__name__)
app.config.from_object(Config)

# Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'en']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'


def get_locale():
    # Intenta obtener el idioma de los argumentos de la URL primero
    lang = request.args.get('lang')
    if lang:
        session['lang'] = lang  # Guarda en la sesión si está presente
    # Si no está en la URL, usa el de la sesión, o el por defecto 'es'
    return session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])


babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals['get_locale'] = get_locale  # Hace get_locale disponible en las plantillas Jinja

# DB y Mail
db.init_app(app)
mail = Mail(app)


@app.route('/contact', methods=["GET", "POST"])
@app.route('/<lang>/contact', methods=["GET", "POST"])
def contact(lang=None):
    # Establece el idioma de la sesión si se proporciona en la URL
    if lang:
        session['lang'] = lang
    # Obtiene el idioma actual para usarlo en la lógica y redirecciones
    lang = session.get('lang', 'es')

    form = ContactForm()

    # Define las opciones del SelectField. Esto es correcto.
    form.subject.choices = [
        ('consulta', _('Consulta general')),
        ('asesoria', _('Agendar asesoría')),
        ('colaboracion', _('Colaboración o invitación')),
        ('otro', _('Otro'))
    ]

    # --- INICIO DE LA SECCIÓN DE DEBUG Y WORKAROUND ---
    # Imprime el valor RAW recibido directamente del formulario POST
    raw_subject_from_request = request.form.get("subject")
    print("Valor recibido de subject (desde request.form):", raw_subject_from_request)
    print("Choices válidos (valores internos esperados):", [c[0] for c in form.subject.choices])
    print("Choices válidos (textos mostrados):", [c[1] for c in form.subject.choices])

    # Crea un mapeo inverso de texto visible a valor interno
    # Ejemplo: {'Consulta general': 'consulta', 'Agendar asesoría': 'asesoria', ...}
    display_to_value_map = {v: k for k, v in form.subject.choices}

    # WORKAROUND: Si el valor recibido es el texto visible en lugar del valor interno,
    # lo mapeamos al valor interno correcto ANTES de la validación del formulario.
    if raw_subject_from_request in display_to_value_map:
        # Si el valor recibido coincide con un texto visible,
        # sobrescribe form.subject.data con el valor interno esperado.
        form.subject.data = display_to_value_map[raw_subject_from_request]
        print(f"DEBUG: Mapeado '{raw_subject_from_request}' a '{form.subject.data}' para validación.")
    elif raw_subject_from_request and raw_subject_from_request not in [c[0] for c in form.subject.choices]:
        # Esto es para depurar si se recibe algo que no es ni valor ni texto visible
        print(
            f"WARNING: Valor de subject '{raw_subject_from_request}' no es un valor ni un texto de elección conocido.")
    # --- FIN DE LA SECCIÓN DE DEBUG Y WORKAROUND ---

    # Ahora, se procede con la validación. form.subject.data ya debería tener el valor correcto
    if form.validate_on_submit():
        user_name = form.name.data.strip()
        user_email = form.email.data.strip()
        user_phone = form.phone.data.strip() if form.phone.data else ''

        # user_subject ahora usará el valor interno (ej. 'consulta')
        # Si necesitas el texto visible para el correo, lo obtienes del mapeo original
        user_subject_display_text = dict(form.subject.choices).get(form.subject.data, form.subject.data)
        user_message = form.message.data.strip()

        # Sanitiza entrada básica para prevenir inyección (buena práctica)
        safe = lambda s: re.sub(r'[<>]', '', s)

        # Correo de notificación al administrador
        msg = Message(
            subject="Nuevo mensaje desde tu sitio web",
            recipients=[os.getenv("MAIL_RECIPIENT", "tucorreo@gmail.com")],
            # Asegúrate de configurar MAIL_RECIPIENT en tu .env
            body=f"""
Nombre: {safe(user_name)}
Email: {safe(user_email)}
Teléfono: {safe(user_phone)}
Motivo: {safe(user_subject_display_text)}
Mensaje:
{safe(user_message)}
            """
        )
        mail.send(msg)

        # Autorespuesta HTML al usuario
        if user_email:
            if lang == 'es':
                html = render_template("email_respuesta_es.html", name=user_name, subject=user_subject_display_text,
                                       message=user_message)
                subject = "¡Muchas gracias por tu mensaje!"
            else:
                html = render_template("email_respuesta_en.html", name=user_name, subject=user_subject_display_text,
                                       message=user_message)
                subject = "Thanks for your message!"

            confirmation = Message(
                subject=subject,
                recipients=[user_email],
                html=html
            )
            print("Enviando mensaje a:", user_email)
            mail.send(confirmation)

        flash(_("Mensaje enviado con éxito"))
        return redirect(url_for('contact', lang=lang))

    # Imprime el estado del formulario y los errores si no es válido
    print("¿Formulario enviado?:", form.is_submitted())
    print("¿Formulario válido?:", form.validate())
    print("Errores del formulario:", form.errors)

    return render_template("contact.html", form=form)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/admin")
def admin():
    contacts = Contact.query.order_by(Contact.id.desc()).all()
    return render_template("admin.html", contacts=contacts)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea las tablas de la base de datos si no existen
    app.run(debug=False)  # Ejecuta la aplicación en modo producción (debug=False)
