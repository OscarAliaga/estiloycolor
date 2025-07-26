import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY no configurada. Define una en tu entorno (.env)")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad para cookies y sesiones
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Asegúrate de usar HTTPS en producción
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 días

    # Configuración de correo
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    if not all([MAIL_USERNAME, MAIL_PASSWORD]):
        raise ValueError("MAIL_USERNAME o MAIL_PASSWORD no configurados. Verifica tu archivo .env")
