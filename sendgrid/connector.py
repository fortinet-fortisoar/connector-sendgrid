"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

from connectors.core.connector import Connector, ConnectorError, get_logger
from .operations import operations, check_health
logger = get_logger('sendgrid')


class Sendgrid(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            action = operations.get(operation)
            return action(config, params, **kwargs)
        except Exception as err:
            logger.exception(str(err))
            raise ConnectorError(str(err))

    def check_health(self, config):
        try:
            logger.info('executing check health')
            connection_response = check_health(config)
            return connection_response
        except Exception as err:
            logger.exception(str(err))
            raise ConnectorError(str(err))



