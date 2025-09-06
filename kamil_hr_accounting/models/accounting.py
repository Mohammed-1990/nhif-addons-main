# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from odoo.exceptions import except_orm, Warning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
class ratificationListHR(models.Model):
	_inherit = 'ratification.list'
	
	from_hr = fields.Boolean()
	allowance_id = fields.Many2one('allowance.allowance',)
	meal_allowance_id = fields.Many2one('meal.allowance',)
	inclination_allowance_id = fields.Many2one('inclination.allowance',)
	incentive_id = fields.Many2one('hr.incentive',)
	mission_allowance_id = fields.Many2one('mission.allowance',)
	training_allowance_id = fields.Many2one('training.allowance',)
	payslip_id = fields.Many2one('hr.payslip.run',)


	def return_to_ia(self):
		if self.ratification_ids and (self.ratification_ids.state != 'draft' and self.ratification_ids != 'canceled'):
			raise ValidationError(_('The financial ratification must be canceled or draft'))
		self.ratification_ids.unlink()
		#Allowances
		if self.allowance_id and self.from_hr == True:
			for line in self.allowance_id.line_ids:
				line.write({'state':'internal_auditor'})
			self.allowance_id.write({'state':'internal_auditor'})
		#Meal Allowance
		if self.meal_allowance_id and self.from_hr == True:
			for line in self.meal_allowance_id.line_ids:
				line.write({'state':'internal_auditor'})
			self.meal_allowance_id.write({'state':'internal_auditor'})
		#Inclination Allowance
		if self.inclination_allowance_id and self.from_hr == True:
			for line in self.inclination_allowance_id.line_ids:
				line.write({'state':'internal_auditor'})
			self.inclination_allowance_id.write({'state':'internal_auditor'})
		#Incentive
		if self.incentive_id and self.from_hr == True:
			for line in self.incentive_id.line_ids:
				line.write({'state':'internal_auditor'})
			self.incentive_id.write({'state':'internal_auditor'})
		#Mission Allowance
		if self.mission_allowance_id and self.from_hr == True:
			self.mission_allowance_id.write({'state':'internal_auditor'})
		#Training Allowance
		if self.training_allowance_id and self.from_hr == True:
			self.training_allowance_id.write({'state':'internal_auditor'})
		#Incentive
		if self.payslip_id and self.from_hr == True:
			for line in self.payslip_id.slip_ids:
				line.sudo().write({'state':'internal_auditor'})
			self.payslip_id.sudo().write({'state':'internal_auditor'})
		#Change ratification list state
		self.state = 'send_to_ia'

class ratificationHR(models.Model):
	_inherit = 'ratification.ratification'
	
	from_hr = fields.Boolean()	
	loan_id = fields.Many2one('hr.loan',)	
	special_allowance_id = fields.Many2one('special.allowance',)
	removing_differences_id = fields.Many2one('removing.differences',)
	incentive_id = fields.Many2one('hr.incentive',)
	payslip_id = fields.Many2one('hr.payslip.run',)

	@api.multi
	@api.onchange('ratification_list_id')
	def onchange_ratification_list_id(self):
		super(ratificationHR, self).onchange_ratification_list_id()
		if self.ratification_list_id.incentive_id:
			self.incentive_id = self.ratification_list_id.incentive_id.id
		if self.ratification_list_id.payslip_id:
			self.payslip_id = self.ratification_list_id.payslip_id.id
	
	
	def return_to_ia(self):
		#Secial Allowance
		if self.special_allowance_id and self.from_hr == True:
			self.special_allowance_id.write({'state':'internal_auditor'})
		#Removing differences
		if self.removing_differences_id and self.from_hr == True:
			self.removing_differences_id.write({'state':'internal_auditor'})
		#Change ratification list state
		self.state = 'send_to_ia'

class ratificationLineHR(models.Model):
	_inherit = 'ratification.line'
	
	loan_id = fields.Many2one('hr.loan',)	

class ratificationPaymentHR(models.Model):
	_inherit = 'ratification.payment'
	loan_id = fields.Many2one('hr.loan', string="Loan", ondelete='cascade')
	incentive_id = fields.Many2one('hr.incentive',)
	payslip_id = fields.Many2one('hr.payslip.run',)

	@api.multi
	@api.onchange('ratification_id')
	def onchange_ratification(self):
		super(ratificationPaymentHR, self).onchange_ratification()
		if self.ratification_id.ratification_list_id.from_complex == True:
			for line in self.ratification_id.line_ids:
				if line.loan_id:
					payment_line = self.env['payment.ratification.line'].search([('ratification_line_id','=',line.id),('ratification_id','=',self.ratification_id.id)],limit=1)
					payment_line.write({'loan_id': line.loan_id.id})

		if self.ratification_id.loan_id:
			self.loan_id = self.ratification_id.loan_id.id
		if self.ratification_id.incentive_id:
			self.incentive_id = self.ratification_id.incentive_id.id
		if self.ratification_id.payslip_id:
			self.payslip_id = self.ratification_id.payslip_id.id
		
	@api.multi
	def do_approve(self):
		super(ratificationPaymentHR, self).do_approve()
		if self.ratification_id.ratification_list_id.from_complex == True:
			for line in self.line_ids:
				if line.loan_id:
					line.loan_id.write({'state':'done_registered_payment','register_payment_date':date.today()})
		if self.loan_id:
			self.loan_id.write({'state':'done_registered_payment','register_payment_date':date.today()})
		if self.incentive_id:
			self.incentive_id.register_payment(self.incentive_id)
		if self.payslip_id:
			self.payslip_id.register_payment(self.payslip_id)

class PaymentRatificationLineHR(models.Model):
	_inherit = 'payment.ratification.line'
	
	loan_id = fields.Many2one('hr.loan',)	

class CancelPaymenWizardHR(models.TransientModel):
	_inherit = 'wizard.payment.cancel'
	
	@api.multi
	def do_cancel(self):
		payment_id = self.env['ratification.payment'].search([('id','=', self.env.context.get('payment_id',0))])
		if payment_id.ratification_id and payment_id.ratification_id.incentive_id:
			payment_id.ratification_id.incentive_id.canceled_register_payment(payment_id.ratification_id.incentive_id)
		if payment_id.ratification_id and payment_id.ratification_id.payslip_id:
			payment_id.ratification_id.payslip_id.canceled_register_payment(payment_id.ratification_id.payslip_id)
		super(CancelPaymenWizardHR, self).do_cancel()