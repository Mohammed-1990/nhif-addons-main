# *.* coding:utf-8  *.*

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime, time
from odoo.exceptions import UserError,ValidationError

class PurchaseRequest(models.Model):

	_name = 'purchase.request'
	_description = 'Purchase Request'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_order = "id desc"

	READONLY_STATES = {
		'done': [('readonly', True)],
		'in_process': [('readonly', True)],
		'branch_manager': [('readonly', True)],
		'gen_man_appr': [('readonly', True)],
		'director_finance_admin_comm_decided': [('readonly', True)],
		'purchase_department2': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	name = fields.Char('Request ID' )
	admin_id = fields.Many2one('hr.department', string="Administration", states=READONLY_STATES, default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.parent_id, readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', states=READONLY_STATES, default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id, readonly="1")
	ordering_date = fields.Date('Ordering Date', default=fields.Date.today(), states=READONLY_STATES, required="1")
	state = fields.Selection([
						# ('draft','Draft'),
						('purchase_department','Draft'),
						('branch_manager','Branch Manager'),
						('gen_man_appr','General Manager Approval'),
						('director_finance_admin_comm_decided','Director and finance and administrative or Committee Decided'),
						('purchase_department2','Purchase Department'),
						('purchase_department_branch','Purchase Department of Branch'),
						('bransh','Branch'),
						('in_process', 'Wainting Execution'),
						('done','Done'),
						('cancel','Cancel'),
						],default='purchase_department', track_visibility='onchange')
	type = fields.Selection([
						('public_tender','Public Tender'),
						('limited_tender','Limited Tender'),
						('request_for_quotaion','Request For Quotaion(RFQs)'),
						('direct_purchase','Direct Purchase')
						],'Type', 
						states={
						'done': [('readonly', True)],'cancel': [('readonly', True)]})

	line_ids = fields.One2many('purchase.request.line','request_id', states=READONLY_STATES, track_visibility='onchange')
	requisition_id = fields.Many2one('purchase.requisition', 'Tender' , ondelete='restrict')
	purchase_ids = fields.One2many('purchase.order','request_id',string="RFQ")
	order_count = fields.Integer(compute='_compute_orders_number')
	partner_id = fields.Many2one('res.partner', 'Vendor')
	company_id = fields.Many2one('res.company', string='Branch', required=True, default=lambda self: self.env.user.company_id.id)
	ref = fields.Char('Refrance')
	is_transfer = fields.Boolean(default=False, readonly=True)



	@api.model
	def create(self, vals):
		vals['state'] = 'purchase_department'
		seq_code = 'purchase.request.sequence' 
		seq = self.env['ir.sequence'].next_by_code( seq_code )
		if not seq:
			self.env['ir.sequence'].create({
				'name' : seq_code,
				'code' : seq_code,
				'prefix' : 'PR',
				'number_next' : 1,
				'number_increment' : 1,
				'use_date_range' : True,
				'padding' : 4,
				})
		vals['name'] = seq
		# vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.sequence')			
		return super(PurchaseRequest, self).create(vals)



		
	@api.multi
	def unlink(self):
		# if any(rec.user_id and rec.user_id.id != rec.env.uid and rec.state == 'purchase_department' for rec in self):
		# 	raise ValidationError(_('You can not delete request ,only the user created have permission!!!'))
		if any(rec.state in ['in_process','done'] for rec in self):
			raise ValidationError(_(
				"You can not delete a request that in 'Wainting Execution' or 'Done' state") )
		return super(PurchaseRequest, self).unlink()
	



	@api.multi
	@api.depends('purchase_ids')
	def _compute_orders_number(self):
		for request in self:
			request.order_count = len(request.purchase_ids)
		
	@api.multi
	def action_cancel(self):
		self.write({'state':'cancel'})
	
	@api.multi
	def action_reset_draft(self):
		self.write({'state':'purchase_department'})

	@api.multi
	def action_dept_approve(self):
		self.write({'state':'manager_director'})

	@api.multi
	def action_manager_dicrector(self):
		self.write({'state':'branch_manager'})

	@api.multi
	def action_branch_manager(self):
		self.write({'state':'director_finance_admin_comm_decided'})

	@api.multi
	def action_gen_man_appr(self):
		self.write({'state':'director_finance_admin_comm_decided'})

	@api.multi
	def action_confirm_order(self):
		if not self.type:
			raise UserError(_('Select Purchase Type !!'))
		if self.type in ('public_tender','limited_tender'):
			self.write({'state':'in_process'})
		else:
			self.write({'state':'purchase_department2'})

	@api.multi
	def action_confirm_pd(self):
		if not all(obj.line_ids for obj in self):
			raise UserError(_("You cannot confirm Request '%s' because there is no product line.") % self.name)
		context = self._context
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)

		if user.company_id.is_main_company:
			self.write({'state':'gen_man_appr'})
		else:
			self.write({'state':'branch_manager'})

	@api.multi
	def action_branch_purchase_department(self):
		self.is_transfer = True
		self.write({'state':'in_process'})


	@api.multi
	def action_purchase_department(self):
		self.write({'state':'in_process'})



class PurchaseRequestLine(models.Model):

	_name = 'purchase.request.line'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']


	name = fields.Char(string='Description')
	product_id = fields.Many2one('product.product', string="Product",  track_visibility='onchange', required="1")
	product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure')
	product_qty = fields.Float('Quantity', required=True, track_visibility='onchange',default=1)
	price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
	note = fields.Text('Purchase Purpose')
	account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
	planned_date = fields.Date(string='Planned Date')
	move_dest_id = fields.Many2one('stock.move', 'Downstream Move')
	request_id = fields.Many2one('purchase.request')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

	@api.onchange('product_id')
	def _onchange_product_id(self):
		self.product_uom_id = self.product_id.uom_po_id.id

class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	request_id = fields.Many2one('purchase.request','Purchase Request')
	type = fields.Selection([
						('public_tender','Public Tender'),
						('limited_tender','Limited Tender'),
						('request_for_quotaion','Request For Quotaion(RFQs)'),
						('direct_purchase','Direct purchase')
						],'Type',default="request_for_quotaion")
		
class Company(models.Model):
	_inherit = 'res.company'

	is_main_company = fields.Boolean('Main Company')
		

