from odoo import models,fields, api,_ 
from odoo.exceptions import ValidationError

class MoneyShotageNotification(models.Model):
	_name = 'money.shotage.notification'
	_order = 'id desc'

	name = fields.Many2one('account.journal', string='Bank/Cash', required=True,domain=[('type','in',['cash','bank'])])
	notification_amount = fields.Float(required=True)
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], default='draft')

	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)


	@api.model 
	def create(self, vals):
		for record in self.env['money.shotage.notification'].search([('name','=', vals.get('name',False))]):
			raise ValidationError(_('There is Limit set for this Bank/Cash'))
		return super(MoneyShotageNotification, self).create(vals)

	

class Payments(models.Model):
	_inherit = 'ratification.payment'

	@api.multi
	@api.onchange('journal_id')
	def onchange_journal_id_in_money_shortage(self):
		date_to = fields.Date.today()
		if self.date:
			date_to = self.date
		if self.journal_id:
			self._cr.execute("select sum(COALESCE( debit, 0 ))-sum(COALESCE( credit, 0 )) from account_move_line where account_id="  + str(self.journal_id.default_credit_account_id.id) + " AND date <= '" + str(date_to) + "'  " )
			balance = self.env.cr.fetchone()[0] or 0.0
			limit_amount = 0
			for record in self.env['money.shotage.notification'].sudo().search([('name','=',self.journal_id.id)]):
				limit_amount = record.notification_amount
			str_limit_amount = str('{:,.2f}'.format(limit_amount))
			if limit_amount > 0 :
				if (balance + self.net_amount) <= limit_amount:
					warning_mess = {
						'title': _('الرصيد شارف على النفاذ'),
						'message' : _( 'رصيد الخزينة/البنك شارف على النفاذ وسيصبح اقل من ' + str_limit_amount  ),
					}
					return {'warning' : warning_mess}
