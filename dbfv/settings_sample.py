# Django settings for dbfv project.

from dbfv.settings_global import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# See http://www.google.com/recaptcha/api for details
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''


MEDIA_ROOT = '/path/to/media'

# Configure your email backend
# https://docs.djangoproject.com/en/dev/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Django debug toolbar
#MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#INSTALLED_APPS += ('debug_toolbar',)
#INTERNAL_IPS = ('127.0.0.1',)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''