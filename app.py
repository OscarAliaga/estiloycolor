from flask import Flask, render_template, redirect, url_for, flash, request
from flask_babel import Babel, _, get_locale
from forms import ContactForm
from models import db, Contact
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Configuración de Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'en']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# ✅ Versión moderna y correcta: usar locale_selector directamente
def get_locale():
    lang = request.args.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        return lang
    return app.config['BABEL_DEFAULT_LOCALE']

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals['get_locale'] = get_locale

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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
