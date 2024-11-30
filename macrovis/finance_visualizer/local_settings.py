from .settings import *

# Override settings for local development
DEBUG = True

# Allow both HTTP and HTTPS
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Additional security settings to disable
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Ensure we accept both HTTP and HTTPS
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
USE_X_FORWARDED_PROTO = False