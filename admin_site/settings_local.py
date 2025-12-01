# admin_site/settings_local.py

# ====================================================================
# DEVELOPMENT DATABASE CONFIGURATION (SQLite)
#
# This overrides the PostgreSQL settings in settings.py to allow the 
# server to start without external driver issues.
# ====================================================================

# NOTE: 'BASE_DIR' must be imported from the main settings.py if used here, 
# but for simplicity, we just define the DATABASES dict.
# BASE_DIR is expected to be available in the context of the main settings file.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smart_sight',
        'USER': 'capstone',
        'PASSWORD': 'capstone',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}