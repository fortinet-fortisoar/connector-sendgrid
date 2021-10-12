""" Copyright start
  Copyright (C) 2008 - 2021 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

from connectors.core.connector import Connector, ConnectorError, get_logger
from .operations import operations, check_health
logger = get_logger('sendgrid')


class Sendgrid(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            action = operations.get(operation)
            return action(config, params)
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



