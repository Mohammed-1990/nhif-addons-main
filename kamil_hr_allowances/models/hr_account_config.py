# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class hrAccountConfig(models.Model):
	_inherit = ['mail.thread','mail.activity.mixin']
	_name="hr.account.config"

	name = fields.Char()
	after_service_benefits = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	merit_cash_alternative = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')], string="Cash Alternative")
	merit_baggage_relay = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')], string="Baggage Relay")
	end_service_rewards = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')], string="End of service benefits")
	meal_allowance = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	meal_leave_deduction = fields.Many2one('account.tax',track_visibility="onchange",)
	meal_allowance_honesty = fields.Many2one('account.tax',track_visibility="onchange",)
	deduction_amount = fields.Many2one('account.tax',track_visibility="onchange",)
	inclination_allowance = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	special_allowance = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	mission_petty_cash = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	mission_allowance = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	remove_diffrences = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	training_expenses = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	training_allowance = fields.Many2one('account.account',track_visibility="onchange", domain=[('is_group','=','sub_account')])
	company_id = fields.Many2one('res.company',string='Branch',default=lambda self: self.env.user.company_id,readonly=True, track_visibility="onchange")

	@api.model
	def create(self, values):
		res = super(hrAccountConfig, self).create(values)
		res.name = 'اعدادات حسابات الموارد البشرية فرع ('+res.company_id.name+')'
		if self.env['hr.account.config'].search([('id','!=',res.id),('company_id','=',res.company_id.id)]):
			raise Warning(_('It is not possible to create more than one account preparation record for branch (%s)')%(res.company_id.name))
		return res


