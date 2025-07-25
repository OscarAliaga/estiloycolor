from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_babel import Babel, _, get_locale
from flask_mail import Mail, Message
from dotenv import load_dotenv
from config import Config
from models import db, Contact
from forms import ContactForm
import os

# 🧪 Carga variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'en']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
def get_locale():
    lang = request.args.get('lang')
    if lang:
        session['lang'] = lang
    return session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals['get_locale'] = get_locale

# Base de datos
db.init_app(app)

# Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)

# 🌐 Ruta dinámica con o sin idioma
@app.route('/contact', methods=["GET", "POST"])
@app.route('/<lang>/contact', methods=["GET", "POST"])
def contact(lang=None):
    if lang:
        session['lang'] = lang
    lang = session.get('lang', 'es')

    form = ContactForm()
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        user_phone = request.form.get('phone')
        user_subject = request.form.get('subject')
        user_message = request.form.get('message')

        # Correo para ti
        msg = Message(
            subject="Nuevo mensaje desde tu sitio web",
            recipients=["tucorreo@gmail.com"],
            body=f"""
Nombre: {user_name}
Email: {user_email}
Teléfono: {user_phone}
Motivo: {user_subject}
Mensaje:
{user_message}
            """
        )
        mail.send(msg)

        # Autorespuesta HTML
        if user_email:
            if lang == 'es':
                html = f"""<html><body>
                <div style="text-align:center;margin-bottom:20px;">
                <img src="http://127.0.0.1:5000/static/img/logo_acuarelas-2.png" style="max-width:150px;">
                </div>
                <p>Hola <strong>{user_name}</strong>,</p>
                <p>Gracias por contactarme. He recibido tu mensaje.</p>
                <p><strong>Motivo:</strong> {user_subject}<br><strong>Mensaje:</strong><br>{user_message}</p>
                <p>Un abrazo,<br><strong>Eli Llantén</strong></p></body></html>"""
                subject = "¡Gracias por tu mensaje!"
            else:
                html = f"""<html><body>
                <p>Hi <strong>{user_name}</strong>,</p>
                <p>Thank you for contacting me. I’ve received your message.</p>
                <p><strong>Subject:</strong> {user_subject}<br><strong>Message:</strong><br>{user_message}</p>
                <p>Best regards,<br><strong>Eli Llantén</strong></p></body></html>"""
                subject = "Thanks for your message!"

            confirmation = Message(
                subject=subject,
                recipients=[user_email],
                html=html
            )
            mail.send(confirmation)

        flash(_("Mensaje enviado con éxito"))
        return redirect(url_for('contact', lang=lang))

    return render_template("contact.html", form=form)

# 🧭 Rutas principales
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

# 🏁 Inicialización
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
