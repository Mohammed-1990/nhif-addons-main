import base64
import datetime
import dateutil
import email
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
from odoo import _, api, exceptions, fields, models, tools

import time
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib
from collections import namedtuple
from email.message import Message
from email.utils import formataddr
from lxml import etree
from werkzeug import url_encode
from werkzeug import urls

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools import pycompat, ustr
from odoo.tools.misc import clean_context
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class Message_inhireted(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'
    

    @api.model
    def _get_default_from(self):
        if self.env.user.email:
            return formataddr((self.env.user.name, self.env.user.email))
        # raise UserError(_("Unable to post message, please configure the sender's email address."))


class Message_message_log(models.AbstractModel):
    _inherit = 'mail.thread'
    def _message_log(self, body='', subject=False, message_type='notification', **kwargs):
        """ Shortcut allowing to post note on a document. It does not perform
        any notification and pre-computes some values to have a short code
        as optimized as possible. This method is private as it does not check
        access rights and perform the message creation as sudo to speedup
        the log process. This method should be called within methods where
        access rights are already granted to avoid privilege escalation. """
        if len(self.ids) > 1:
            raise exceptions.Warning(_('Invalid record set: should be called as model (without records) or on single-record recordset'))

        kw_author = kwargs.pop('author_id', False)
        if kw_author:
            author = self.env['res.partner'].sudo().browse(kw_author)
        else:
            author = self.env.user.partner_id
        # if not author.email:
            # raise exceptions.UserError(_("Unable to log message, please configure the sender's email address."))
        # email_from = formataddr((author.name, author.email))

        email_from='exam@gmail.com'

        message_values = {
            'subject': subject,
            'body': body,
            'author_id': author.id,
            'email_from': email_from,
            'message_type': message_type,
            'model': kwargs.get('model', self._name),
            'res_id': self.ids[0] if self.ids else False,
            'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'record_name': False,
            'reply_to': self.env['mail.thread']._notify_get_reply_to(default=email_from, records=None)[False],
            'message_id': tools.generate_tracking_message_id('message-notify'),
        }
        message_values.update(kwargs)
        message = self.env['mail.message'].sudo().create(message_values)
        return message
