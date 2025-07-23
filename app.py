from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_babel import Babel, _, get_locale
from forms import ContactForm
from models import db, Contact
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Necesario para usar sesiones (como guardar idioma)
app.config['SECRET_KEY'] = 'cambia_esto_por_una_clave_secreta_segura'

# Configuración de Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'en']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

db.init_app(app)

# ✅ Selección dinámica del idioma
def get_locale():
    lang = request.args.get('lang')
    if lang:
        session['lang'] = lang
    return session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

# Flask-Babel 2.0+
babel = Babel(app, locale_selector=get_locale)

# Hace accesible get_locale en las plantillas Jinja
app.jinja_env.globals['get_locale'] = get_locale

# 🧭 Rutas
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

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        new_contact = Contact(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(new_contact)
        db.session.commit()
        flash(_("Mensaje enviado con éxito"), "success")
        return redirect(url_for("contact", lang=get_locale()))
    return render_template("contact.html", form=form)

@app.route("/admin")
def admin():
    contacts = Contact.query.order_by(Contact.id.desc()).all()
    return render_template("admin.html", contacts=contacts)

# 🏁 Inicialización
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
