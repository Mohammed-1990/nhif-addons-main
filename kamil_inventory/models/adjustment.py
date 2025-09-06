# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare
from datetime import datetime
from dateutil.relativedelta import relativedelta


class KamilInventoryAdjustmentTypes(models.Model):
    _inherit = 'stock.inventory'

    adjust_type = fields.Selection([('annual','Annual'),('periodic','Periodic'),('surprising','Surprising')], string='Adjustment')
    periodic_interval = fields.Integer(string='Month Interval')	
    adjustment_committee_id = fields.Many2one('committee.committee', string='Inventory adjustement committee', compute='_compute_committee_members')
    adjustment_committee_member_ids = fields.One2many(related='adjustment_committee_id.committee_member')
    active_id = fields.Boolean(string='Active', compute='_compute_user_id', default=False)


    @api.multi
    def set_confirm(self):
        self.write({'state':'confirm'})


    @api.multi
    def _compute_user_id(self):
    	context = self._context
    	current_uid = context.get('uid')
    	user = self.env['res.users'].browse(current_uid)
    	print (self.adjustment_committee_id.committee_member)
    	for vals in self.adjustment_committee_id.committee_member:
    		if vals.employee.user_id.id == user.id:
    			self.active_id = True
    			


    def _compute_committee_members(self):
    	committee = self.env['committee.committee'].search([('committee_type.name','ilike','Inventory'),('state','=','active')], limit=1)
    	self.adjustment_committee_id = committee.id


    # def unlink(self):
    #     if any(request.state not in ['done'] for request in self):
    #         raise UserError(_("You cannot delete request in '%s' state , only on 'draft' or 'cancel' .") % self.state)
    #     return super(KamilInventoryAdjustmentTypes, self).unlink()       

class KamilAutoadjust(models.Model):
	_name = 'auto.adjust'

	@api.multi
	def create_periodic_adjust(self):
		vals = {'name': "Periodic Inventory Adjustment on " + str(datetime.now().date()),
				'adjust_type':'periodic'}
		adjustemnt_id = self.env['stock.inventory'].create(vals)
		adjustemnt_id.action_start()


	@api.multi
	def create_annual_adjust(self):
		vals = {'name': "Annual Inventory Adjustment on " + str(datetime.now().date()),
				'adjust_type':'annual'}
		adjustemnt_id = self.env['stock.inventory'].create(vals)
		adjustemnt_id.action_start()