# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class res_company(models.Model):
    _inherit = "res.company"

    custom_report_header = fields.Binary('Header', attachment=True)
    custom_report_footer = fields.Binary('Footer', attachment=True)

