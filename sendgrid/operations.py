""" Copyright start
  Copyright (C) 2008 - 2021 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import requests, json, base64
import mimetypes
from os.path import join
from .constants import *
from sendgrid import SendGridAPIClient
from connectors.cyops_utilities.builtins import download_file_from_cyops
from integrations.crudhub import make_request, make_file_upload_request
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, Disposition, BatchId, SendAt, To, Bcc, Cc, From, Content, Subject, FileType)


from connectors.core.connector import ConnectorError, get_logger

logger = get_logger('sendgrid')

class SendGrid(object):

    def __init__(self, config):
        self.url = config.get('url').strip(',') + '/v3'
        self.api_key = config.get('api_key')
        if not self.url.startswith('https://') and not self.url.startswith('http://'):
            self.url = 'https://{}'.format(self.url)
        self.verify_ssl = config.get('verify_ssl')

    def make_rest_call(self, url, method='GET', params = None, data=None, header=None):
        try:
            endpoint = self.url + url
            if not header:
                header = {"Authorization":'Bearer {}'.format(self.api_key)}
            response = requests.request(method, endpoint, headers=header, verify=self.verify_ssl, params=params,
                                        data=data)
            if response.ok:
                logger.info('Successfully got response for url {}'.format(url))
                if 'json' in str(response.headers):
                    return response.json()
                else:
                    try:
                        return json.loads(response.content)
                    except:
                        return response.content
            else:
                if 'json' in str(response.headers):
                    raise ConnectorError({'status_code': response.status_code, 'message': response.json()})
                else:
                    raise ConnectorError({'status_code': response.status_code, 'message': response.content})
        except requests.exceptions.SSLError:
            raise ConnectorError('SSL certificate validation failed')
        except requests.exceptions.ConnectTimeout:
            raise ConnectorError('The request timed out while trying to connect to the server')
        except requests.exceptions.ReadTimeout:
            raise ConnectorError('The server did not send any data in the allotted amount of time')
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Invalid endpoint or credentials')
        except Exception as err:
            raise ConnectorError(str(err))



def _add_attachment_to_email(iri, iri_type, inline=False):
    try:
        file_name = None
        if iri_type == 'attachment':
            attachment_data = make_request(iri, 'GET')
            file_iri = attachment_data['file']['@id']
            file_name = attachment_data['file']['filename']
        else:
            file_iri = iri
        file_download_response = download_file_from_cyops(file_iri)
        logger.info('file_download_response = {}'.format(file_download_response))
        if not file_name:
            file_name = file_download_response['filename']
        file_path = join('/tmp', file_download_response['cyops_file_path'])
        file_type = file_download_response['content_type']
        logger.info('file_type = {}'.format(file_type))
        with open(file_path, 'rb') as attachment:
            file_data = attachment.read()
            encoded_file = base64.b64encode(file_data).decode()
        if inline:
            attachedFile = Attachment(FileContent(encoded_file), FileName(file_name), FileType(file_type),
                                      Disposition('inline'))
        else:
            attachedFile = Attachment(FileContent(encoded_file), FileName(file_name), FileType(file_type),
                                      Disposition('attachment'))
        logger.info('attachedFile = {}'.format(attachedFile))
        return attachedFile
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError('could not find attachment with id {}'.format(str(iri)))


def str_to_list(input_str):
    if isinstance(input_str, str) and len(input_str) > 0:
        return [x.strip() for x in input_str.split(',')]
    elif isinstance(input_str, list):
        return input_str
    else:
        return []


def format_date(input_date):
    try:
        res = input_date.split('T')
        if len(res) > 0:
            return res[0]
        else:
            return None
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def _handle_attachments(iri_list, message, inline=False):
    try:
        for iri in iri_list:
            iri_type = 'attachment'
            if not iri.startswith('/api/3/'):
                iri = '/api/3/attachments/' + iri
            elif iri.startswith('/api/3/files'):
                iri_type = 'file'
            attachedFile = _add_attachment_to_email(iri, iri_type, inline)
            message.attachment = attachedFile
            logger.info('{} Attachment added to email'.format(iri))
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def send_email(config, params):
    try:
        params = {k: v for k, v in params.items() if v is not None and v != '' and v != {}}
        message = Mail()

        if not params.get('html_content') and not params.get('plain_text_content'):
            raise ConnectorError('At least one parameter is required from \'Plain Text Body Content\' or \'HTML Body Content\'')
        message.from_email = From(params.get('from_email'))
        if params.get('subject'):
            message.subject = Subject(params.get('subject'))

        if params.get('html_content'):
            message.content = Content('text/html', params.get('html_content'))

        if params.get('plain_text_content'):
            message.content = Content('text/plain', params.get('plain_text_content'))

        _handle_attachments(str_to_list(params.get('iri_list')), message)
        _handle_attachments(str_to_list(params.get('inline_iri_list')), message, True)
        sg = SendGridAPIClient(config.get('api_key'))
        if params.get('batch_id'):
            message.batch_id = BatchId(params.get('batch_id'))
        to_list = str_to_list(params.get('to_emails'))
        cc_list = str_to_list(params.get('cc_recipients'))
        bcc_list = str_to_list(params.get('bcc_recipients'))

        # add To recipients
        if len(to_list) > 0:
            for email_id in to_list:
                message.to = To(email_id)

        # add cc recipients
        if len(cc_list) > 0:
            for email_id in cc_list:
                message.cc = Cc(email_id)

        # add bcc recipients
        if len(bcc_list) > 0:
            for email_id in cc_list:
                message.bcc = Bcc(email_id)

        if params.get('send_at'):
            message.send_at = SendAt(int(params.get('send_at')))
        logger.info('message object = {}'.format(message))
        response = sg.send(message)
        logger.info(response.status_code, response.body, response.headers)
        if response.status_code == 202:
            logger.info('Email send successfully')
            return 'Email send successfully'
        else:
            logger.error('Failed to send email, error is = {0}'.format(response.body))
            raise ConnectorError('Failed to send email, error is = {0}'.format(response.body))
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def get_email_stats(config, params):
    try:
        endpoint = ENDPOINTS_DICT.get(params.pop('stats_by'))
        sendgrid_obj = SendGrid(config)
        params['start_date'] = format_date(params.get('start_date'))
        params['end_date'] = format_date(params.get('end_date', ''))
        param_dict = {k: v for k, v in params.items() if v is not None and v != '' and v != {}}
        from urllib.parse import urlencode
        query_string = urlencode(param_dict)
        res = sendgrid_obj.make_rest_call(endpoint, params=query_string)
        return res
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def search_email(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        endpoint = '/messages'
        res = sendgrid_obj.make_rest_call(endpoint, params=params)
        return res
    except Exception as err:
        logger.exception(str(err))
        if 'authorization required' in str(err):
            raise ConnectorError('You must purchase \'additional email activity history\' to gain access to the '
                                 'Email Activity Feed API.')

        raise ConnectorError(str(err))


def get_contact_list(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        return sendgrid_obj.make_rest_call(CONTACT_LIST_ENDPOINT)
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def get_alerts(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        return sendgrid_obj.make_rest_call(ALERT_ENDPOINT)
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def create_batch_id(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        return sendgrid_obj.make_rest_call(CREATE_BATCH_ENDPOINT, method='POST')
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def get_scheduled_send(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        if params.get('batch_id'):
            endpoint =SCHDULED_ENDPOINT + '/{batch_id}'.format(batch_id=params.get('batch_id'))
        else:
            endpoint = SCHDULED_ENDPOINT
        res = sendgrid_obj.make_rest_call(endpoint)
        return res
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def update_scheduled_send(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        data = {
            'batch_id': params.get('batch_id'),
            'status': PARAM_MAPPING.get(params.get('status'), 'pause')
        }
        return sendgrid_obj.make_rest_call(SCHDULED_ENDPOINT, method='POST', data=data)
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def delete_scheduled_send(config, params):
    try:
        sendgrid_obj = SendGrid(config)
        endpoint = SCHDULED_ENDPOINT + '/{batch_id}'.format(batch_id=params.get('batch_id'))
        return sendgrid_obj.make_rest_call(endpoint, method='DELETE')
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def check_health(config):
    try:
        sendgrid_obj = SendGrid(config)
        params = {'limit': 1}
        response = sendgrid_obj.make_rest_call('/api_keys', params= params)
        if response:
            return True
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


operations = {
    'send_email': send_email,
    'get_email_stats': get_email_stats,
    'search_email': search_email,     #not verified
    'get_contact_list': get_contact_list,
    'get_alerts': get_alerts,
    'create_batch_id': create_batch_id,
    'get_scheduled_send': get_scheduled_send,
    'update_scheduled_send': update_scheduled_send,   #not verified
    'delete_scheduled_send': delete_scheduled_send    #not verified
}
