# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class KamilNewProductLines(models.Model):
	_name = 'new.product.line'

	product_name = fields.Char(string='Product Name')
	types = fields.Selection([('consu','Consumable'),('service','Service'),('product','Storable')], default='product')
	category_id = fields.Many2one('product.category', 'Product Category')
	cost = fields.Float(string='Cost Price')
	sale = fields.Float(string='Sale Price')
	uom = fields.Many2one('uom.uom', string='UOM')
	new_product = fields.Many2one('new.product')
	created_prod = fields.Many2one('product.template')
	state = fields.Selection([('draft','Draft'),('created','Created')], default='draft', string='State')
	is_manager = fields.Boolean(string='Manager', default=False, compute="_check_user_group")




	@api.multi
	def _check_user_group(self):
		for rec in self:
			if rec.new_product.state != "draft":
				if rec.new_product.is_manager:
					rec.is_manager = True
				else:
					rec.is_manager = False



	@api.multi
	def create_product(self):
		vals = {
				'name': self.product_name,
				'type': self.types,
				'categ_id':self.category_id.id,
				'list_price': self.sale,
				'standard_price': self.cost,
				'uom_id': self.uom.id,
				'uom_po_id':self.uom.id}
		self.created_prod = self.env['product.template'].with_context({'need_request':True}).create(vals)
		self.write({'state':'created'})

	@api.multi
	def open_product(self):
		return{
				'type':'ir.actions.act_window',
				'res_model':'product.template',
				'res_id':self.created_prod.id,
				'view_type':'form',
				'view_mode':'form'
			}


class KamilNewProduct(models.Model):
	_name = 'new.product'
	_rec_name = 'new_request'
	_order ='id desc'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

	def get_company_id(self):
		return self.env.user.company_id.id

	responsible = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
	date = fields.Datetime(string='Request Date', default=datetime.now())
	new_request = fields.Char(string='Request ID')
	item_lines = fields.One2many('new.product.line','new_product',string='New Items')
	is_manager = fields.Boolean(string='Manager', default=False, compute="_check_user_group")
	state = fields.Selection([('draft','Draft'),('approval','Inventory Responsible Approval'),('done','Done'),('cancel','Cancel')], default='draft', string='State',track_visibility='onchange')
	company_id = fields.Many2one('res.company','Branch',default=get_company_id)
	


	@api.multi
	def _check_user_group(self):
		user_id = self._context.get('uid')
		user = self.env['res.users'].browse(user_id)
		if user.has_group('stock.group_stock_manager'):
			self.is_manager = True
		else:
			self.is_manager = False


	@api.model
	def create(self, vals):
		seq_code = 'add.new.product' 
		seq = self.env['ir.sequence'].next_by_code( seq_code )
		if not seq:
			self.env['ir.sequence'].create({
				'name' : seq_code,
				'code' : seq_code,
				'prefix' : 'NI',
				'number_next' : 1,
				'number_increment' : 1,
				'use_date_range' : True,
				'padding' : 4,
				})
		seq = self.env['ir.sequence'].next_by_code( seq_code )
		# seq = self.env['ir.sequence'].next_by_code('add.new.product')
		# context = self._context
		# current_uid = context.get('uid')
		# user = self.env['res.users'].browse(current_uid)
		# employee = self.env['hr.employee'].search([('user_id.id','=',user.id)],limit=1)
		# department = employee.department_id
		# vals['new_request'] = seq + " / " +str(user.name) 
		vals['new_request'] = seq
		res = super(KamilNewProduct, self).create(vals)
		return res


	@api.multi
	def submit_to_approval(self):
		# for record in self:
			# if any(x.created_prod for x in record.item_lines) == False:
		if not any(line.item_lines for line in self):
			raise UserError(_('You have to set at least one product from request !'))
		self.write({'state':'approval'})

	@api.multi
	def action_confirm(self):
		self.write({'state':'done'})

	@api.multi
	def action_cancel(self):
		self.write({'state':'cancel'})

	def unlink(self):
		if any(item.state in ('done') for item in self):
			raise UserError(_('You cannot delete done itme.'))
		return super(KamilNewProduct, self).unlink()