# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime, time
from odoo.exceptions import UserError,ValidationError

class RequestForQuotaion(models.Model):
	_name = 'purchase.rfq'
	_description = 'RFQ'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_order = "id desc"

	READONLY_STATES = {
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	sequence = fields.Char('Request ID', readonly=True)
	name = fields.Char('Description',required=True,states=READONLY_STATES)
	user_id = fields.Many2one('res.users', string='Requester',default=lambda self: self.env.user, readonly="1")
	admin_id = fields.Many2one('hr.department', string="Administration", states=READONLY_STATES, default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.parent_id, readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', states=READONLY_STATES, default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id, readonly="1")
	ordering_date = fields.Date('Ordering Date', default=fields.Date.today(), states=READONLY_STATES, required="1")
	state = fields.Selection([
							('purchase_department','Purchase Department'),
							('purchase_department_branch','Purchase Department of Branch'),
							('bransh','Branch'),
							('done','Done'),
							('cancel','Cancel'),
							],default='purchase_department', track_visibility='onchange')
	type = fields.Selection([
							('request_for_quotaion','Request For Quotaion(RFQs)'),
							('direct_purchase','Direct Purchase')
							],'Type', states=READONLY_STATES)

	line_ids = fields.One2many('purchase.rfq.line','rfq_id', states=READONLY_STATES)
	purchase_ids = fields.One2many('purchase.order','rfq_id',string="RFQ")
	order_count = fields.Integer(compute='_compute_orders_number')
	partner_id = fields.Many2one('res.partner', 'Vendor')
	finance_approv_attach = fields.Binary('Finance Approval Attchement')
	company_id = fields.Many2one('res.company', string='Branch', required=True, default=lambda self: self.env.user.company_id.id)
	ref = fields.Char('Refrance')
	request_ids = fields.Many2many('purchase.request',string='Requests')


	@api.multi
	@api.depends('purchase_ids')
	def _compute_orders_number(self):
		for request in self:
			request.order_count = len(request.purchase_ids)


	@api.multi
	def action_branch_manager(self):
		self.write({'state':'gen_man_appr'})


	@api.model
	def create(self, vals):
		if vals['type'] == 'request_for_quotaion':
			seq_code = 'rfq'
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :'RFQ',
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['sequence'] = seq 
		else:
			seq_code = 'direct.purchase'
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' : 'DR' ,
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['sequence'] = seq  
			
		return super(RequestForQuotaion, self).create(vals)



	@api.multi
	def action_confirm_pd(self):
		if not any(rec.request_ids for rec in self):
			raise UserError(_('You have to set at least one product from request !'))

		if not any(rec.state in ['purchase'] for rec in self.purchase_ids):
			raise UserError(_('You have to set at least one invoice confirmed !!'))
		
		length = len(self.purchase_ids)
		if self.type == 'request_for_quotaion':
			if not any(rec.purchase_ids for rec in self) or length < 3:
				raise UserError(_('You have to set at least three invoice from request !'))
		else:
			if not any(rec.purchase_ids for rec in self):
				raise UserError(_('You have to set at least one invoice from request !'))
		for record in self:
			for line in record.request_ids:
				line.state = 'done'
			for line in record.purchase_ids:
				if line.state != 'purchase':
					line.state = 'cancel'
					
		self.write({'state':'done'})

	@api.multi
	def action_branch_purchase_department(self):
		self.write({'state':'bransh'})

	def action_purchase_order_to_so(self):
		if not any(rec.request_ids for rec in self):
			raise UserError(_('You have to set at least one product from request !'))
		return{
			'name':'Purchase Order',
			'type':'ir.actions.act_window',
			'res_model':'purchase.order',
			'view_mode':'form',
			'target':'current',
			'context':{
				'default_rfq_id':self.id,
				'default_origin':self.sequence,
				'default_type':self.type,
				'default_partner_id':self.partner_id.id}
		}

	def action_cancel(self):
		self.write({'state':'cancel'})


	@api.multi
	def unlink(self):
		if any(rec.state == 'done' for rec in self):
			raise ValidationError(_("You can not delete request  in 'done' state!!!"))
		if any(rec.user_id.id != self.env.uid for rec in self):
			raise ValidationError(_('You can not delete request ,only the user created have permission!!!'))
		return super(RequestForQuotaion, self).unlink()



class PurchaseRfqLine(models.Model):

	_name = 'purchase.rfq.line'

	name = fields.Char(string='Description')
	product_id = fields.Many2one('product.product', string="Product", required="1")
	product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure')
	categ_id = fields.Many2one('product.category', 'Product Category' , related="product_id.categ_id", readonly="1")
	product_qty = fields.Float('Quantity')
	price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
	note = fields.Text('Purchase Purpose')
	account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
	schedule_date = fields.Date(string='Scheduled Date')
	move_dest_id = fields.Many2one('stock.move', 'Downstream Move')
	rfq_id = fields.Many2one('purchase.rfq')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)




	@api.multi
	def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0):
		self.ensure_one()

		request = self.rfq_id
		if self.schedule_date:
			date_planned = datetime.combine(self.schedule_date, time.min)
		else:
			date_planned = datetime.now()
		
		return {
			'name': name,
			'product_id': self.product_id.id,
			'product_uom': self.product_id.uom_po_id.id,
			'product_qty': product_qty,
			'price_unit': price_unit,
			'date_planned': date_planned,
			'account_analytic_id': self.account_analytic_id.id,
			'analytic_tag_ids': self.analytic_tag_ids.ids,
			'move_dest_ids': self.move_dest_id and [(4, self.move_dest_id.id)] or [],
		}

	@api.onchange('product_id')
	def _onchange_product_id(self):
		if self.product_id:
			self.product_uom_id = self.product_id.uom_id
			self.product_qty = 1.0
	



class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	rfq_id = fields.Many2one('purchase.rfq','Purchase RFQ',track_visibility='o')
	purchase_department_attch = fields.Binary('Purchase Department Attach')
	is_contract = fields.Boolean('Is Contact', default=False)

		
	@api.onchange('rfq_id')
	def onchange_rfq_id(self):
		self.origin = self.rfq_id.sequence

		if self.rfq_id.partner_id:
			self.partner_id = self.rfq_id.partner_id.id
		if not self.rfq_id:
			return 
		request = self.rfq_id
		# self.partner_id = request.partner_id.id
		# Create PO lines if nessasary
		order_lines = []
		for line in request.line_ids:
			name = line.product_id.display_name

			# Compute quantity and price_unit
			if line.product_uom_id != line.product_id.uom_po_id:
				product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
				price_unit = 0.0
			else:
				product_qty = line.product_qty
				price_unit = line.price_unit

			# Create PO line
			order_line_values = line._prepare_purchase_order_line(
				name=name, product_qty=product_qty, price_unit=price_unit)

			order_lines.append((0, 0, order_line_values))
		self.order_line = order_lines


	@api.multi
	def confirm_rfq(self):
		self.write({'state':'purchase_department'})

	@api.multi
	def confirm_purchase_department(self):
		self.write({'state':'finance_manager'})


	@api.multi
	def action_brnach_manager(self):
		self.write({'state':'gen_man_appr'})
		

	@api.multi
	def action_gm_manager(self):
		self.write({'state':'finance_admin_manager'})


	@api.multi
	def action_finance_admin_manager(self):
		self.write({'state':'finance_manager'})

	@api.multi
	def action_finance_manager(self):
		self.write({'state':'purchase'})


	@api.multi
	def button_confirm(self):
		res = super(PurchaseOrder,self).button_confirm()
		for order in self:
			# if order.state not in ['draft', 'sent']:
			# 	continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if order.company_id.po_double_validation == 'one_step'\
					or (order.company_id.po_double_validation == 'two_step'\
						and order.amount_total < self.env.user.company_id.currency_id._convert(
							order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
					or order.user_has_groups('purchase.group_purchase_manager'):
				self.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
				self._create_picking()
				# order.button_approve()
				# self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
			else:
				order.write({'state': 'to approve'})
		return True


	@api.multi
	def print_quotation(self):
		# self.write({'state': "sent"})
		return self.env.ref('purchase.report_purchase_quotation').report_action(self)


	@api.multi
	@api.returns('mail.message', lambda value: value.id)
	def message_post(self, **kwargs):
		# if self.env.context.get('mark_rfq_as_sent'):
			# self.filtered(lambda o: o.state == 'draft').write({'state': 'sent'})
		return super(PurchaseOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)


	@api.multi
	def action_rfq_send(self):
		'''
		This function opens a window to compose an email, with the edi purchase template message loaded by default
		'''
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			if self.env.context.get('send_rfq', False):
				template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
			else:
				template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = dict(self.env.context or {})
		ctx.update({
			'default_model': 'purchase.order',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'custom_layout': "mail.mail_notification_paynow",
			'force_email': True,
		})


	@api.multi
	def action_create_contract(self):
		name = ''
		if self.type == 'direct_purchase':
			name = self.rfq_id.name
		ctx = {
			'default_name':name,
			'default_purchase_order_id':self.id,
			'default_contract_type':'Goods',
			'default_contract_amount':self.amount_total,
			'default_ntfs':self.company_id.id,
			'default_second_party_ch':self.partner_id.id,
			'default_second_party_name':self.partner_id.id,

			}
		
		return {
			'name':_('Contacts'),
			'type':'ir.actions.act_window',
			'res_model':'kamil.contracts.contract',
			'view_mode':'form',
			'target':'current',
			'context':ctx
			}
		self.is_contract = True
		self.write({'state':'contact'})
