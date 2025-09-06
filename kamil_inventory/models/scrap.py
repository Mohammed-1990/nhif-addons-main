# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo.exceptions import ValidationError, Warning

class KamilScrapRequest(models.Model):
	_name = 'scrap.inventory'
	_rec_name = 'scrap_id'


	def _compute_committee_members(self):
		committee = self.env['committee.committee'].search([('committee_type.name','ilike','Scrap')], limit=1)
		self.scrap_committee_id = committee.id

	def get_company_id(self):
		return self.env.user.company_id.id

	scrap_id = fields.Char(string='Request ID')
	date = fields.Date(string='Request Date', default=datetime.now().date())
	location_id = fields.Many2one('stock.location', string='Stock Location', required=True, domain=[('usage','in',['internal'])])
	responsible = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
	item_lines = fields.One2many('scrap.inventory.line','product_scraps',string='Scrapping Items')
	check_date = fields.Date(string='Check Date')
	company_id = fields.Many2one('res.company','Branch', default=get_company_id)
	scrap_committee_id = fields.Many2one('committee.committee', string='Scrap committee')
	scrap_committee_member_ids = fields.One2many(related='scrap_committee_id.committee_member')
	scarp_check_file = fields.Binary('Check Result File', copy=False)
	scarp_check_result = fields.Text('Check Result', copy=False)
	state = fields.Selection([('draft','Draft'),
		('inv_reposnsible','Inventory Responsible'),('admin_manager','Administration Manager'),('finan_admin_manager','Finance and Administration Manager'),('scarp_commitee','Scarp Committee'),('done','Done'),('cancel','Cancelled')], default='draft')



	@api.multi
	def action_draft(self):
		if self.state == 'draft':
			self.write({'state':'inv_reposnsible'})
		
	@api.multi
	def action_inv_reposnsible(self):
		if self.state == 'inv_reposnsible':
			self.write({'state':'admin_manager'})

	@api.multi
	def action_admin_manger(self):
		if self.state == 'admin_manager':
			self.write({'state':'finan_admin_manager'})

	@api.multi
	def action_finan_admin_manager(self):
		if self.state == 'finan_admin_manager':
			self._compute_committee_members()
			self.write({'state':'scarp_commitee'})

	@api.multi
	def cancel(self):	
		self.write({'state':'cancel'})


	@api.multi
	# @api.onchange('item_lines')
	def check_done_state(self):
		if all(x.state == 'done' for x in self.item_lines):
			self.state = 'done'


	# @api.model
	# def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
	# 	res = super(KamilScrapRequest, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
	# 	current_uid = self._context.get('uid')
	# 	user = self.env['res.users'].browse(current_uid)
	# 	if view_type == "form" and res['name']=="view.scrap.request.form":
	# 		doc = etree.XML(res['arch'])
	# 		all_scrap_record = self.env['scrap.request'].search([])

	# 		# To readonly 0/1 of Date field between Scrap committee Chairman and others
	# 		# for all_scrap in all_scrap_record:
	# 		# 	for scraps in all_scrap.scrap_committee_id.committee_member:
	# 		# 		if scraps.role == 'chairman':
	# 		# 			node = doc.xpath("/form/sheet/group/group/field[@name='check_date']") #If attribute is in main form
	# 		# 			if user.id == scraps.employee.user_id.id:
	# 		# 				node[0].set("readonly", "0")
	# 		# 			else:
	# 		# 				node[0].set("readonly", "1")
	# 		# 			setup_modifiers(node[0], res['fields']['check_date'])
	# 		# 			res['arch'] = etree.tostring(doc)

	# 		# To readonly 0/1 for scrap lines between Responsible and Scrap committee
	# 		doc = etree.XML(res['fields']['item_lines']['views']['tree']['arch']) #If attribute is in related field
	# 		node2 = doc.xpath("/tree/field[@name='product']")
	# 		node3 = doc.xpath("/tree/field[@name='qty_2_scrap']")
	# 		node4 = doc.xpath("/tree/field[@name='approved_qty']")
	# 		node5 = doc.xpath("/tree/field[@name='approved']")
	# 		user_ids = []
	# 		for all_scrap in all_scrap_record:
	# 			for users in all_scrap.scrap_committee_id.committee_member:
	# 				user_ids.append(users.employee.user_id.id)
	# 			if user.id in user_ids:
	# 				node2[0].set("readonly", "1")
	# 				setup_modifiers(node2[0], res['fields']['item_lines']['views']['tree']['fields']['product'])
	# 				node3[0].set("readonly", "1")
	# 				setup_modifiers(node3[0], res['fields']['item_lines']['views']['tree']['fields']['qty_2_scrap'])
	# 				node4[0].set("readonly", "0")
	# 				setup_modifiers(node4[0], res['fields']['item_lines']['views']['tree']['fields']['approved_qty'])
	# 				node5[0].set("readonly", "0")
	# 				setup_modifiers(node5[0], res['fields']['item_lines']['views']['tree']['fields']['approved'])
	# 			elif user.id not in user_ids:
	# 				node2[0].set("readonly", "0")
	# 				setup_modifiers(node2[0], res['fields']['item_lines']['views']['tree']['fields']['product'])
	# 				node3[0].set("readonly", "0")
	# 				setup_modifiers(node3[0], res['fields']['item_lines']['views']['tree']['fields']['qty_2_scrap'])
	# 				node4[0].set("readonly", "1")
	# 				setup_modifiers(node4[0], res['fields']['item_lines']['views']['tree']['fields']['approved_qty'])
	# 				node5[0].set("readonly", "1")
	# 				setup_modifiers(node5[0], res['fields']['item_lines']['views']['tree']['fields']['approved'])
	# 			res['fields']['item_lines']['views']['tree']['arch'] = etree.tostring(doc)
	# 	return res


	@api.model
	def create(self, vals):
		seq = self.env['ir.sequence'].next_by_code('scrap.inventory')
		context = self._context
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		employee = self.env['hr.employee'].search([('user_id.id','=',user.id)],limit=1)
		department = employee.department_id
		vals['scrap_id'] = seq + " / " +str(user.name) 
		res = super(KamilScrapRequest, self).create(vals)
		return res

class KamilScrapInventorytLines(models.Model):
	_name = 'scrap.inventory.line'


	product = fields.Many2one('product.product', string='Items')
	product_scraps = fields.Many2one('scrap.inventory')
	qty_2_scrap = fields.Integer(string='Quantity to Scrap')
	approved_qty = fields.Integer(string='Approved Quantity')
	approved = fields.Boolean(string='Approved')
	scarp_created = fields.Boolean(default=False)
	state = fields.Selection([('draft','New'),
							('progress','In progress'),
							('done','Done')], default='draft', readonly=True)


	@api.multi
	def initiate_scrap(self):
		current_uid = self._context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		if not user.id == self.product_scraps.responsible.id:
			raise ValidationError(_("Only %s can create a Scrap Initiation Order")%(self.product_scraps.responsible.name))
		if int(self.approved_qty) !=0:
			if not self.scarp_created:
				vals = {'product_id': self.product.id,
						'scrap_qty': self.approved_qty,
						'origin': self.product_scraps.scrap_id,
						'location_id': self.product_scraps.location_id.id,
						'date_expected': datetime.now().date(),
						'product_uom_id': self.product.uom_id.id,
						'request_id': self.product_scraps.id
						}
				scrap_rec = self.env['stock.scrap'].create(vals)
				self.scarp_created = True
				self.state = 'progress'
			else:
				raise ValidationError(_("A scrap process has already been created for this product!"))
			return{
				'type':'ir.actions.act_window',
				'res_model':'stock.scrap',
				'res_id':scrap_rec.id,
				'view_type':'form',
				'view_mode':'form'
			}
		else:
			raise ValidationError(_("Cannot Create a Scrap order with 0 approved quantity"))

	@api.multi
	def open_scrap(self):
		scrap_rec = self.env['stock.scrap'].search([('request_id','=',self.product_scraps.id),('product_id','=',self.product.id)],limit=1)
		if scrap_rec:
			return{
				'type':'ir.actions.act_window',
				'res_model':'stock.scrap',
				'res_id':scrap_rec.id,
				'view_type':'form',
				'view_mode':'form'
			}
		else:
			raise ValidationError(_('It seems like the scarp process for this line has been deleted from the system!\nPlease Contact the system administartor.'))		


class stockScarp(models.Model):

	_inherit = 'stock.scrap'


	request_id = fields.Many2one('scrap.inventory')


	@api.multi
	def do_scrap(self):
		res = super(stockScarp, self).do_scrap()
		if self.request_id:
			request_line_id = self.env['scrap.inventory.line'].search([('product_scraps','=',self.request_id.id),('product','=',self.product_id.id)],limit=1)
			if request_line_id:
				request_line_id.write({'state': 'done'})
				self.request_id.check_done_state()

	@api.multi
	def unlink(self):
		if self.request_id:
			request_line_id = self.env['scrap.inventory.line'].search([('product_scraps','=',self.request_id.id),('product','=',self.product_id.id)],limit=1)
			if request_line_id:
				request_line_id.write({'state': 'draft','scarp_created':False})
		res = super(stockScarp, self).unlink()
		return res
