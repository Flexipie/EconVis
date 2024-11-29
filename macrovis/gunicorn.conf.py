workers = 4

bind = "0.0.0.0:8000"

# Restart workers when code changes (development only!)
reload = False

# Access log - records incoming HTTP requests
accesslog = "-"

# Error log - records Gunicorn server errors
errorlog = "-"

# How verbose the Gunicorn error logs should be
loglevel = "info"