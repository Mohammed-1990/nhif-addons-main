# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class PurchaseOrder(models.Model):
	
	_inherit = 'purchase.order'
	_order = 'amount_total asc'


	READONLY_STATES = {
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	PURCHASE_STATES = [
		('draft', 'draft'),
		('sent', 'RFQ Sent'),
		('general_conditions_selection','General Conditions Selection'),
		('technical_selection','Technical Selection'),
		('to approve', 'To Approve'),
		('purchase', 'Purchase Order'),
		('done', 'Locked'),
		('cancel', 'Cancel'),
		('purchase_department','Purchase Department'),
		('contact','Contact'),
		# ('gen_man_appr','General Manager Approve'),
		# ('finance_admin_manager','Finance Admin Manager'),
		('finance_manager','Finance Manager')
	]
	
	type = fields.Selection([
						('public_tender','Public Tender'),
						('limited_tender','Limited Tender'),
						('request_for_quotaion','Request For Quotaion(RFQs)'),
						('direct_purchase','Direct Purchase')
						],'Type',default="request_for_quotaion")
	email = fields.Char('Email', help="Email address of the contact", track_visibility='onchange', track_sequence=4, index=True, related='partner_id.email')
	phone = fields.Char('Phone', track_visibility='onchange', track_sequence=5, related='partner_id.phone')
	
	state_ids = fields.Many2many("res.country.state", string='State')
	country_ids = fields.Many2many('res.country', string='Country')

	state = fields.Selection(PURCHASE_STATES, string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
	state_tender = fields.Selection(PURCHASE_STATES, compute='_set_state')
	state_rfq = fields.Selection(PURCHASE_STATES, compute='_set_state')
	state_dp = fields.Selection(PURCHASE_STATES, compute='_set_state')
	terms = fields.Text(states=READONLY_STATES)
	general_conditions_ids =fields.Many2many('pr.general.conditions', string='General Conditions',readonly="1")
	private_conditions = fields.Text('Private Conditions', related="requisition_id.private_conditions",readonly="1") 
	other_features = fields.Text('Other Features',states=READONLY_STATES)
	technical_report = fields.Binary('Technical Report')
	reason = fields.Text()
	active = fields.Boolean('Active', default=True)
	collection_id = fields.Many2one('collection.collection', string='Book Fees')
	ratification_count = fields.Integer(compute='_compuet_rat_count')
	company_id = fields.Many2one('res.company', 'Branch', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)
	is_raft =fields.Boolean(default=False)
	is_contract = fields.Boolean('Is Contact', default=False)
	picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=READONLY_STATES, required=True,help="This will determine operation type of incoming shipment", default=[])



	@api.multi
	def _compuet_rat_count(self):
		for rec in self:
			rec.ratification_count = self.env['ratification.ratification'].search_count([('purchase_id','=',rec.id)])


	@api.model
	def default_get(self, default_fields):
		res = super(PurchaseOrder, self).default_get(default_fields)
		res['state_ids'] = [v.id for v in self.env['res.country.state'].search([])]
		res['country_ids'] = [v.id for v in self.env['res.country'].search([])]	
		return res 

	@api.depends('state')
	def _set_state(self):
		self.state_tender = self.state
		self.state_rfq = self.state
		self.state_dp = self.state

	@api.multi
	def action_check_general_conditions(self):
		self.write({'state':'general_conditions_selection'})

	@api.multi
	def action_technical_selection(self):
		self.write({'state':'technical_selection'})


	@api.multi
	def action_to_approve(self):
		self.write({'state':'to approve'})

	@api.multi
	def toggle_active(self):
		self.active = not self.active

	@api.multi
	def open_url(self):
		q = "sun"
		id = self.id
		return{
			'type': 'ir.actions.act_url',
			 # 'url': "http://www.google.bg/?q=%d" % id,
			 'url':"/book/" + str(id),
			  'target': 'new', # open in a new tab
		}

	
	@api.model
	def create(self, vals):
		create_id = super(PurchaseOrder, self).create(vals)
		seq_code = 'purchase.order'
		prefix = 'PO'

		if self._context.get('type') in ['public_tender','limited_tender']:
			seq_code = 'purchase.order' + ' / ' + str(self._context.get('requisition')) + '.'
			prefix = str(self._context.get('requisition')) + ' / TB'
		
		seq = self.env['ir.sequence'].next_by_code( seq_code )
		if not seq:
			self.env['ir.sequence'].create({
				'name' : seq_code,
				'code' : seq_code,
				'prefix' : prefix,
				'number_next' : 1,
				'number_increment' : 1,
				'use_date_range' : True,
				'padding' : 4,
				})
			seq = self.env['ir.sequence'].next_by_code( seq_code )
		create_id.name = seq 

		return create_id


	# @api.model
	# def create(self, vals):
	# 	vals['name'] = self.env['ir.sequence'].next_by_code('tender.book')
	# 	return super(, self).create(vals)

	@api.multi
	def send_book_email(self):
		template_id = self.env.ref('kamil_purchase_public_tender.email_template_tender_book', False)
		mail_template = self.env['mail.template'].browse(template_id.id)
		mail_template.send_mail(self.id, force_send=True, raise_exception=True)

	@api.multi
	def send_email_done(self):
		template_id = self.env.ref('kamil_purchase_public_tender.email_template_done_tender_book', False)
		mail_template = self.env['mail.template'].browse(template_id.id)
		mail_template.send_mail(self.id, force_send=True, raise_exception=True)
		


	@api.multi
	def create_ratification(self):
		vals = []
		tax_data = []
		for line in self.order_line:
			account_id = ''
			the_type = ''
			accounts_receivable = ''
			parent_budget_item_id = ''
			company_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).company_id
			
			if line.product_id.type == 'product':
				# account = self.env['stock.location'].search([('company_id','=',company_id.id),('usage','=','internal')],limit=1).account_id
				account_id = self.picking_type_id.default_location_dest_id.account_id.id

				if account_id == False:
					raise UserError(_("The location is not account please insert !! "))

				the_type = 'accounts_receivable'
				accounts_receivable = 'accounts_receivable'
			else:
				the_type = 'budget'

				account_id = line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id or False
				parent_budget_item_id = line.product_id.property_account_expense_id.budget_item_id.id or line.product_id.categ_id.property_account_expense_categ_id.budget_item_id.id or False
				
				if not account_id:
					raise UserError(_("The Product is not expenses account please insert !! "))
			for tax in line.taxes_id:
				tax_amount = line.price_subtotal * tax.amount
				if tax.amount_type == 'percent':
					tax_amount = tax_amount/100
				if tax.tax_type == 'addition':
					vals.append((0,0,{
						'name':tax.name,
						# 'account_id':line.account_analytic_id.id,
						'amount':tax_amount,
						# 'the_type': 'accounts_payable',
						# 'account_id':tax.account_id.id or False,
						# 'accounts_payable_types':'accounts_payable',
						'the_type': the_type,
						'account_id':account_id or False,
						'parent_budget_item_id':parent_budget_item_id,
						'accounts_receivable_types':accounts_receivable,
						'branch_id':company_id.id,
						}))
				else:
					tax_data.append((0,0,{
						'tax_id':tax.id,
						'name':tax.name,
						'amount':tax_amount
						}))
						


			vals.append((0,0,{
					'name':line.product_id.name + '('+ line.product_uom.name +') - الكمية( ' + str(line.price_subtotal) +' )',
					# 'account_id':line.account_analytic_id.id,
					'amount':line.price_subtotal,
					'the_type': the_type,
					'account_id':account_id or False,
					'parent_budget_item_id':parent_budget_item_id,
					'accounts_receivable_types':accounts_receivable,
					'branch_id':company_id.id,
					'deduction_ids':tax_data
					}))
			self.is_raft = True
		ctx = {
			'default_partner_id':self.partner_id.id,
			'default_ratification_type':'purchases_and_inventory',
			'default_purchase_id':self.id,
			'default_line_ids':vals
			}
		return{
			'name':'Ratification',
			'type':'ir.actions.act_window',
			'res_model':'ratification.ratification',
			'view_mode':'form',
			'target':'current',
			'context':ctx
		}

	@api.multi
	@api.returns('mail.message', lambda value: value.id)
	def message_post(self, **kwargs):
		return super(PurchaseOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
		


class Ratification(models.Model):
	_inherit = 'ratification.ratification'

	purchase_id = fields.Many2one('purchase.order', 'Purchase')

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	type = fields.Selection(related='order_id.type')
		