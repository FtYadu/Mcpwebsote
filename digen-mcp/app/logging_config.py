"""Logging utilities with secret masking."""

from __future__ import annotations

import logging
from logging.config import dictConfig

SECRET_KEYS = {'authorization', 'token', 'password', 'cookie', 'session'}


class SecretMaskFilter(logging.Filter):
    """Mask obvious secrets from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        lower_message = message.lower()
        for key in SECRET_KEYS:
            if key in lower_message:
                record.msg = f'[masked-sensitive-log] {record.msg}'
                record.args = ()
                break
        return True


def configure_logging(level: str = 'INFO') -> None:
    """Configure structured console logging."""

    dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {'secret_mask': {'()': SecretMaskFilter}},
            'formatters': {
                'standard': {
                    'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s',
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'filters': ['secret_mask'],
                    'level': level,
                }
            },
            'root': {'handlers': ['console'], 'level': level},
        }
    )
