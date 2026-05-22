import base64
import json
import os

import github

from giphousewebsite.settings.base import *

from .base import *
ROOT_URLCONF = 'giphousewebsite.urls'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "fnm1xg4jbokf^=x9m6covu2o5)qc0txurb6@k*u3$u9u$@v)7-"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} ({levelname}) {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "ERROR"),
            "propagate": False,
        },
        "gsuitesync": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },
        "github": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },
        "automaticteams": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },
    },
}
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# GitHub App Settings
DJANGO_GITHUB_CLIENT_ID = "Iv23liE9mYKxrugudlw2"
DJANGO_GITHUB_CLIENT_SECRET = "46d2a1224e52f60133d2c291eae9dbda35b5b91d"
DJANGO_GITHUB_SYNC_ORGANIZATION_NAME = "fence-sitters-dev"
DJANGO_GITHUB_SYNC_APP_ID = "2842948"
DJANGO_GITHUB_SYNC_APP_PRIVATE_KEY_BASE64 = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBdzJKVmYrVnl4NkRjdEdoTDJHYStvSzczVTdOK1RVTHp5QXcwZDZOdExnUzB1S0tCCjNlN3VzOEV6dnNXYWxGU3VKL1NmVXJzU0NydGduOVhUWWVKSXN5Zk1wb0kvSTNaVjFxVXorRDdmdVN0S3dJby8KRlNPZG9wdFdxUDhiSUJqVnJiKzVNVVR3ZFNwS3lUaG5jQ1ZObnUwcmhsdHJ1d2JyYlRlUFA2dlQ3T2ZaNzRtKwpjV2I2L2FvVnRkYTRmRDlXdHZZanBGek9UalJEeE9ORmwxVVhjdVQyNUNnTzZyN3AwNlBydm5GaTBsY0JtTEFCCkxBaXZNY0FtUks3NWVIQTZYUGRQSDdKZUpJRlRzZzJFcFozWFhaV2Zuejk4NjZla21QcFlvWDkrSHFTY1p4TEoKZVVMUjlITE9ZMHJqb1RYL1lLdDFTQkxnMlRud0ZPbDRxaTRhMXdJREFRQUJBb0lCQVFDUEgwNHdOTnlpZlNTUApCc05nVHNzZkcydlRKVzNFbk9IRXphUDFhNEtEcmpEUCswS1VWdjBHTWVWOHZuVmdhTE4yVTB3T0p6aXRJZHRDCjJqaFF3Sml1bTkzZXJ4UWZId1Q4Q2VJSzI4dTRjWXo5ZzRkNExiSEFObmdCclhXcVNtYmtNc2d1M2lnaU80dXkKNEoxczJmYUZENGpOajlSWG1WY0ZseWhZNUw2R0QzeEdxdTVtYTZQWDJJTFp2VlFwRU9JdnQyYzhTN3Q0RlIwRgpRWTNHeHRkZHVQaERTa1RUNFZ1K2JLRE1LRGFNMXFEYytNQzdDcnR0NFNYTUsyakdLelU4M01VTk0wR0NIRmxMCmsvQ2tFQTNMbHoxdjRlM2FFWm9MVEVkYThKRHVUYm9ZbUJZODdjYzVlU3dTNVJ2STBiRXMzSXllbVVkZVdFRXUKdUxBYlRoUFJBb0dCQU92cDhPT095NVRjSXhmQ01HcS9kWjZ4UE1iMTl4TWh6QnRubXNpaWZNZzllTEhmZXlQcQpGY3hVbHhjQTZOTTlXdDdRS2pyWlk3M2gwejlqa1FMb0p6UHN1TU5XVi9yOVlrZ29mNURyZHdLNEtxKzJuVGhECkIvZEhsczFQdVkyWk5YSlpJcUUrVU1DbHdNYkNtclAwaDJyQXZWQUFBN2h5YVhwYlc2ZHBrOEgvQW9HQkFOUUUKL2svV1FGUUNJMVFCMkF2WXBudzhZb3hjZVRleDZOMGFvNThPYldGWGVZN3o2RFhGQVJxNWVobG5TNWhtMk1Bbwo2Um00UWs4bFc1emZXZEpGd2U3d0FHd1hDVDVOaXdoUkhRek9YOVlnQzRRb2tGem1odWJBQllzMHpxTTdXeSszClJiN2RQSXFRSThmc3MrMFNRUUhhbGFJZ1lWVXFROS80aFgvZ3FmY3BBb0dBV2dPalJGQ0I0VVMxcHlVVE1FZnAKYXltWlZSa1lzeFljT1FDcEVKRGZKOUE4c3pIZ1hHMis3MzMvUUdtNmJJOW1rc20rczBHclN4SlZka1JaV2xDVwpWTHVvSy9CUUZaYUUzNStFUFJsN0NYQ1g2UCsyc1hieUhTb1ZvalVmU2FZQnZLWENEdUFtRTd1cStLdmNOM25BCkNiMk0vbTlpL0FlN3MxSVVnS1pLR0tVQ2dZQkxnNVBJZjdqZHN2MCtPSUhvaGp1VjJEUUpaZzVPaGZFNGZ2cHoKOWtHREFCTHRsWFhKWU9kcHkxSHZwbGpJYVNrZUYvUWVFd0NiQytVN1ZGbTdpTmp2NzA5WE1FVThpWVhSYW9KOApReXpqS1BxeEVYbUpmUm5qS2RWUHBYbExyaUptTmxLRERtMDN0T3JwbENicGN5endLaGhOYkZiK2JGVk1la21pCktEU2hNUUtCZ0FlY0w1bys4U1l0Mm9HdDVHdHNydjI0STMzN1k3TWJVYWpQelJzZXM3KzF4S1VUMEFSSXMxU04KR1RVZG1sbEp4SDV5T3hlRFA3MzN6ZXBKVGIwM1RjUFE1MVp5SDZCN0RVUDFJTndKQlQvZkY2RUVxVlp5M2FWYgo2SXp1eW5rQ3Q1RlN1bit4eTNPNHVDRzRDaDdzejM5emRGQk82VVF1Y0xvYjZKRGlpekxiCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg=="

DJANGO_GITHUB_SYNC_APP_INSTALLATION_ID = "112553340"



# Use debug-level logging for GitHub synchronisation
github.enable_console_debug_logging()

# GSuite service account credentials
GSUITE_ADMIN_USER = os.environ.get("DJANGO_GSUITE_ADMIN_USER", "")
GSUITE_ADMIN_CREDENTIALS_BASE64 = os.environ.get(
    "DJANGO_GSUITE_ADMIN_CREDENTIALS_BASE64", base64.urlsafe_b64encode(b"{}")
)
GSUITE_ADMIN_CREDENTIALS = base64.urlsafe_b64decode(
    GSUITE_ADMIN_CREDENTIALS_BASE64
)
GSUITE_ADMIN_CREDENTIALS = json.loads(GSUITE_ADMIN_CREDENTIALS)
