#! -*- coding: utf-8 -*-
import logging
import logging.config
import tempfile

__author__ = 'wilfman'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(module)s - %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },

        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            "filename": tempfile.gettempdir() + '/gitPushNotify.log'
        },
    },
    'loggers': {
        'notifaer': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('notifaer')
