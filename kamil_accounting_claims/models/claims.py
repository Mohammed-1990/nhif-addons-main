from odoo import models,fields,api,_ 


class Claims(models.Model):
	_name = 'claims.claims'
	_description = 'Claims Handling'
	

	orgnization_id = fields.Char('Orgnization')
	year_id = fields.Char('Year')
	month = fields.Selection([('january','January'),('february','February'),('march','March'),('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),('september','September'),('october','October'),('november','November'),('december','December')])
	value_claim_before_review = fields.Char('Value of claim before review')
	value_claim_after_review = fields.Char('Value of claim after review')
	branch = fields.Char('Branch')
	state = fields.Selection([('draft','Draft'),('confirm','Confirmed')], default='draft')
	item_line_ids = fields.One2many('claim.items.line','claim_id')
	detail_line_ids = fields.One2many('claim.details.line','claim_id')



class ClaimItemsLine(models.Model):
	_name = 'claim.items.line'
	_description = 'Claims Handling Items Line'

	branch_id = fields.Many2one('res.company', string='Branch',track_visibility='always')
	amount = fields.Float('Amount')
	cost_center_id = fields.Many2one('kamil.account.cost.center',string='Cost Center')
	claim_id = fields.Many2one('claims.claims')


	
class ClaimDetailsLine(models.Model):
	_name = 'claim.details.line'
	_description = 'Claims Handling details Line'

	branch_id = fields.Many2one('res.company', string='Branch',track_visibility='always')
	analytic_account_id = fields.Many2one('account.analytic.account',string='Budget Item')
	amount = fields.Float('Amount')
	partner_id = fields.Many2one('res.partner', string='Subscriber',track_visibility='always')
	claim_id = fields.Many2one('claims.claims')
