# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from lxml import etree
from odoo.exceptions import UserError, ValidationError


class KamilNeedRequisition(models.Model):
	_name = 'need.requisition'
	_rec_name = 'request'
	_order = 'request_date desc'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']


	def _get_employee_id(self):
		context = self._context
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		employee = self.env['hr.employee'].search([('user_id.id','=',user.id)],limit=1)
		department = employee.department_id.id
		return department

	def get_company_id(self):
		return self.env.user.company_id.id

	@api.multi
	def issuing_order_on(self):
		sp = self.env['stock.picking'].search([('need_request_id','=',self.id)])
		if sp:
			self.show_issuing_order = True

	@api.multi
	def purchase_request_on(self):
		pr = self.env['purchase.request'].search([('need_request_id','=',self.id)])
		if pr:
			self.show_purchase_request = True



	request = fields.Char(string="Request ID", default='New')
	request_date = fields.Datetime(string="Date",default=datetime.now())
	department_id = fields.Many2one('hr.department', string="Department", default=_get_employee_id)
	responsible_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
	state = fields.Selection([('draft','Draft'),
							  ('dept_manager','Department Manager Approval'),
							  ('finance_admin_manager','Finance and Administration Manager Approval'),
							  ('admin_manger','Administration Manager Approval'),
							  ('inventory_manager','Inventory Responsible Approval'),
							  ('inventory_employee','Inventory Manager Approval'),
							  ('available','Available'),
							  ('partially_available','Partially Available'),
							  ('purchase','Purchase'),
							  ('done','Done'),
							  ('cancel','Cancel')], string="State", default="draft",  track_visibility='onchange')
	current_user_logged = fields.Many2one('res.users',string="Current Login", default=lambda self: self.env.user)
		# user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange', default=lambda self: self.env.user)

	requests_line = fields.Many2one('need.requisition.line')
	line_ids = fields.One2many('need.requisition.line','requests',string="Request Lines")
	company_id = fields.Many2one('res.company','Branch', default=get_company_id)
	form_46 = fields.Binary('Form 46')
	license_no = fields.Integer('License Number')
	show_purchase_request = fields.Boolean(default=False, compute='purchase_request_on')
	show_issuing_order = fields.Boolean(default=False, compute='issuing_order_on')
	location_id = fields.Many2one('stock.location','Location',domain=lambda self:self._domain_location())

	def _domain_location(self):
		return [('usage','=','internal'),('company_id','=',self.get_company_id())]

	def current_user(self):
		context = self._context
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		self.update({'current_user_logged': user.id})



	# @api.model
	# def create(self, vals):
	# 	create_id = super(KamilNeedRequisition, self).create(vals)
	# 	if create_id.request_date:

	# 		context = self._context
	# 		current_uid = context.get('uid')
	# 		user = self.env['res.users'].browse(current_uid)
	# 		employee = self.env['hr.employee'].search([('user_id.id','=',user.id)],limit=1)
	# 		department = employee.department_id
	# 		seq_code = 'need.requisition.' + str(user.name or False) + ' / '+ '.' +  str(department.name or False) 
	# 		seq = self.env['ir.sequence'].next_by_code( seq_code )
	# 		if not seq:
	# 			self.env['ir.sequence'].create({
	# 				'name' : seq_code,
	# 				'code' : seq_code,
	# 				'prefix' : str(user.name or False) + ' / ' +  str(department.name or False) + ' / ' ,
	# 				'number_next' : 1,
	# 				'number_increment' : 1,
	# 				'use_date_range' : True,
	# 				'padding' : 4,
	# 				})
	# 			seq = self.env['ir.sequence'].next_by_code( seq_code )
	# 		create_id.request = seq 

	# 	return create_id

	@api.multi
	def action_draft(self):		
		if self.state == 'draft':
			if not any(line.line_ids for line in self):
				raise UserError(_('You have to set at least one product from request !'))

			if self.request == 'New':
				seq_code = 'need.requisition.seq' 
				seq = self.env['ir.sequence'].next_by_code( seq_code )
				if not seq:
					self.env['ir.sequence'].create({
						'name' : seq_code,
						'code' : seq_code,
						'prefix' : 'NR',
						'number_next' : 1,
						'number_increment' : 1,
						'use_date_range' : True,
						'padding' : 4,
						})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
				self.request = seq
				# self.request = self.env['ir.sequence'].next_by_code('need.requisition.seq')			
			self.write({'state' : 'dept_manager'})

	@api.multi
	def action_dept_manger(self):
		if self.state == 'dept_manager':
			self.write({'state' : 'finance_admin_manager'})

	@api.multi
	def action_finance_admin_manager(self):
		if self.state == 'finance_admin_manager':
			self.write({'state' : 'admin_manger'})

	@api.multi
	def action_admin_manger(self):
		if self.state == 'admin_manger':
			self.write({'state' : 'inventory_manager'})

	@api.multi
	def action_inventory_manger(self):
		if self.state == 'inventory_manager':
			self.write({'state' : 'inventory_employee'})

	@api.multi
	def action_cancel(self):
		self.write({'state' : 'cancel'})

	@api.multi
	def action_reset_draft(self):
		self.write({'state' : 'draft'})


	def _prepare_po_lines(self):
		# location_id = self.env['stock.location'].search([('usage','=','internal'),('company_id','=',self.company_id.id)],limit=1)
		po_lines = []
		for rec in self:
			location_id = rec.location_id
			if rec.line_ids:
				for line in rec.line_ids:
					product_quant = rec.env['stock.quant'].search([('company_id','=',rec.company_id.id),('location_id','=',location_id.id),('product_id','=',line.item_id.id)])
					quant_locs = rec.env['stock.quant'].search([('product_id', '=', line.item_id.id),('location_id','=',rec.location_id.id)], limit=1)

					
					if line.qty > quant_locs.quantity:
						po_lines.append((0,0,{
							'product_id':line.item_id.id,
							'product_qty': abs(line.qty - quant_locs.quantity),
							'planned_date':line.date,
							}))
		return po_lines


	def _prepare_sp_lines(self):

		picking_lines = []
		for rec in self:
			warehouse = rec.env['stock.warehouse'].search([('company_id','=',rec.company_id.id)],limit=1)
			picking_type_id = rec.env['stock.picking.type'].search([('code','ilike','outgoing'),('warehouse_id','=',warehouse.id),('for_emloyees_request','=',True),('default_location_src_id','=',rec.location_id.id)],limit=1)
			if not picking_type_id:
				raise ValidationError(_('There\'s a problem with the configuration. No picking type is found to handle employees need requests!!'))
			

			# location_id = self.env['stock.location'].search([('usage','=','internal'),('company_id','=',self.company_id.id)],limit=1)
			location_id = rec.location_id

			location_dest_id = rec.env['stock.location'].search([('usage','=','employees')], limit=1)


			if rec.line_ids:
				for line in rec.line_ids:
					quant_locs = rec.env['stock.quant'].search([('product_id', '=', line.item_id.id),('location_id','=',rec.location_id.id)],limit=1)
					quantity = 0.0
					if quant_locs.quantity >= line.qty:
						quantity = line.qty
					else:
						quantity = quant_locs.quantity

					picking_lines.append((0,0,{
						'name':_('Product ')+line.item_id.name,
						'product_uom':line.item_id.uom_id.id,
						'product_id':line.item_id.id,
						'product_uom_qty': line.qty,
						'reserved_availability':quantity,
						'date_expected':line.date,
						'picking_type_id':picking_type_id.id,
						'location_id':location_id.id,
						'location_dest_id':location_dest_id.id,
						'state':'draft'
									}))
		return picking_lines


	@api.one
	def action_process(self):
		for rec in self:
			po_lines = rec._prepare_po_lines()
			sp_lines = rec._prepare_sp_lines()
			po = rec.env['purchase.request']
			sp = rec.env['stock.picking']
		
			if sp_lines:
				warehouse = rec.env['stock.warehouse'].search([('company_id','=',rec.company_id.id)],limit=1)
				picking_type_id = rec.env['stock.picking.type'].search([('code','ilike','outgoing'),('for_emloyees_request','=',True),('warehouse_id','=',warehouse.id),('default_location_src_id','=',rec.location_id.id)],limit=1)

				if not picking_type_id:
					raise ValidationError(_('There\'s a problem with the configuration. No picking type is found to handle employees need requests!\n Please contact the system administration.'))

				location_id = rec.location_id

				if not location_id:
					raise ValidationError(_('There\'s a problem with the configuration. No stock location is found for this company/branch.\n Please contact the system administration.'))

				location_dest_id = rec.env['stock.location'].search([('usage','=','employees')],limit=1)

				if not location_dest_id:
					raise ValidationError(_('There\'s a problem with the configuration. No employees location is defined in the system.\n Please contact the system administration.'))
				sp = sp.create({
							'partner_id':rec.responsible_id.partner_id.id,
							'origin': str(rec.request),
							'scheduled_date':str(datetime.now().date()),
							'state':'draft',
							'picking_type_id':picking_type_id.id,
							'location_id':location_id.id,
							'location_dest_id':location_dest_id.id,
							'move_ids_without_package':sp_lines,
							'need_request_id':rec.id})
				sp.action_assign()
			
			if po_lines:
				po = po.create({
							'company_id':rec.company_id.id,
							'admin_id':rec.department_id.parent_id.id or False,
							'dept_id': rec.department_id.id or False,
							'date':datetime.now().date(),
							'state':'purchase_department',
							'line_ids':po_lines,
							'need_request_id':rec.id,
							})

			if sp and not po:
				rec.state = 'available'
			elif po and all(x.reserved_availability == 0 for x in sp.move_ids_without_package):
				rec.state = 'purchase'
			elif po and sp:
				rec.state = 'partially_available'

	def action_view_picking(self):
		sp = self.env['stock.picking'].search([('need_request_id','=',self.id)])
		if sp:	
			return {
			'name':_('Issuing Order'),
			'type':'ir.actions.act_window',
			'res_model':'stock.picking',
			'view_type': 'form',
			'view_mode': 'tree,form',
			# 'view_id':self.env.ref('stock.view_picking_form').id,
			'domain': [('need_request_id','=',self.id)]
			}
		else:
			raise UserError(_('There\'s no associated issuing order to this need request, please check with Inventory Keeper!!'))

	def action_view_purchase(self):
		pr = self.env['purchase.request'].search([('need_request_id','=',self.id)])
		if pr:	
			return {
			'name':_('Purchase Request'),
			'type':'ir.actions.act_window',
			'res_model':'purchase.request',
			'view_type': 'form',
			'view_mode': 'form',
			'view_id':self.env.ref('kamil_purchase_request.view_purchase_request_form').id,
			'res_id': pr.id
			}
		else:
			raise UserError(_('There\'s no associated purchase request to this need request, please check with purchasing department!!'))
		


	def unlink(self):
		if any(request.state not in ['draft'] for request in self):
			raise UserError(_("You cannot delete request in '%s' state , only on 'draft' or 'cancel' .") % self.state)
		return super(KamilNeedRequisition, self).unlink()





class KamilNeedRequisitionLine(models.Model):
	_name = 'need.requisition.line'

	item_id = fields.Many2one('product.product', string="Item", required=True, domain="[('type','=','product')]")
	uom = fields.Many2one('uom.uom', related="item_id.uom_id",string="UOM", readonly=True)
	qty = fields.Integer(string="Quantity", required=True)
	date = fields.Date(string="Scheduled Date", required=True)
	requests = fields.Many2one('need.requisition')

