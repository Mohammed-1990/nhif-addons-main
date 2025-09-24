from odoo import models, fields, api, _
from datetime import datetime , date
from lxml import etree
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons import decimal_precision as dp


READONLY_STATES = {
	'done': [('readonly', True)],
	'cancel': [('readonly', True)],
}


class stockPicking(models.Model):
	_inherit = 'stock.picking'


	@api.depends('picking_type_id','custome_state')
	def _compute_picking_type(self):
		if self.picking_type_id and self.picking_type_id.code == 'incoming':
			self.type_field = True
		if self.custome_state in ['final','done']:
			self.final_state = True

	@api.depends('custome_state','type_field','state')
	def _compute_view_validate_button(self):
		if (self.type_field and self.custome_state != 'final') or self.state == 'done':
			self.hide_validate_button = True




	@api.one
	@api.depends('company_id')
	def _compute_info_company_id(self):
		# self.ensure_one()
		self.info_company_id = self.company_id.id

	@api.one
	@api.depends('location_id')
	def _compute_info_location_id(self):
		# self.ensure_one()
		self.info_location_id = self.location_id.id

	custome_state = fields.Selection([('initial','Initial Reception'),
										('quality','Quality Check'),
										('final','Final Reception'),
										('done','Done')], default='initial', copy=False)

	type_field = fields.Boolean(default=False, compute='_compute_picking_type', copy=True)
	final_state = fields.Boolean(default=False, compute='_compute_picking_type', copy=True)
	qc_committee_id = fields.Many2one('committee.committee', string='QC committee', domain=lambda self:self._domain_commitee(), copy=True)
	qc_committee_member_ids = fields.One2many(related='qc_committee_id.committee_member')
	qc_file = fields.Binary('Result File', copy=False, states=READONLY_STATES)
	qc_result = fields.Text('Result', copy=False, states=READONLY_STATES)
	need_request_id = fields.Many2one('need.requisition', copy=False)
	vendor_invoice = fields.Char('Vendor invoice number', copy=False)
	vendor_invoice_file = fields.Binary('Vendor invoice file', copy=False)
	final_invoice = fields.Char('Final reception invoice number', copy=False)
	final_invoice_file = fields.Binary('Final reception invoice file', copy=False)
	twilve_seen = fields.Binary('12س وارد', copy=False)
	twilve_seen2 = fields.Binary('12س صادر', copy=False)

	hide_validate_button = fields.Boolean(default=False, compute='_compute_view_validate_button')
	branch_id = fields.Many2one('res.company','To branch')
	branch_location = fields.Many2one('stock.location','To location')
	branch_scheduled_date = fields.Datetime('Branch delivery date')
	internal_transfer_type = fields.Selection(selection=[('local','To local stock'),('branch','To Branch')],string='Type of internal transfer',default='local')
	info_company_id = fields.Many2one('res.company','From Branch', store=True, compute='_compute_info_company_id')
	info_location_id = fields.Many2one('stock.location','From Location', store=True, compute='_compute_info_location_id')

	# text_str = fields.Text(default=' You have not recorded done quantities yet, by clicking on apply Odoo will process all the reserved quantities.')



	def _domain_commitee(self):
		return [('state','=','active'),('committee_type.types','=','inventory')]




	@api.onchange('qc_committee_id')
	def onchange_qc_committee_id(self):
		vals = []
		for rec in self.qc_committee_id.committee_member:
			vals.append((0,0,{
				'employee':rec.employee.id,
				'role':rec.role.id,
				}))
		self.qc_committee_member_ids = vals



	# @api.depends('picking_type_id','custome_state')
	# def _compute_committee_members(self):
	# 	if self.picking_type_id and self.picking_type_id.code == 'incoming' and self.custome_state == 'quality':
	# 		committee = self.env['committee.committee'].search([('committee_type.name','ilike','Quality')], limit=1)
	# 		self.qc_committee_id = committee.id

	@api.multi
	def do_receipt(self):
		for record in self:
			precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			no_receipt_quantities = all(float_is_zero(move_line.initial_qty,  precision_digits=precision_digits) for move_line in record.move_ids_without_package)
			if no_receipt_quantities:
				raise UserError( _('You can not confirm request because all initial quantities is 0.0 !!'))
			else:
				self.custome_state = 'quality'




	@api.multi
	def do_quality(self):
		for record in self:
			if not record.qc_committee_id:
				raise ValidationError(_('No Quality check committee is found in the system. This operation can not be done.\n Please contact system administrator.'))

			precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			no_quality_quantities = all(float_is_zero(move_line.qc_qty,  precision_digits=precision_digits) for move_line in record.move_ids_without_package)
			if no_quality_quantities:
				raise UserError( _('You can not confirm request because all quality quantities is 0.0 !!'))
			else:
				self.custome_state = 'final'



	def _prepare_move(self):
		for line in self.move_ids_without_package:
			category_account_id = line.product_id.categ_id.property_account_expense_categ_id.id
			if not category_account_id:
				raise UserError(_("The Product category is not expenses account please insert !! "))

			stock_account_id = self.location_id.account_id.id
			if not stock_account_id:
				raise UserError(_("The location is not account please insert !! "))
			analytic_account_id = line.product_id.categ_id.property_account_expense_categ_id.parent_budget_item_id.id
			if not analytic_account_id:
				raise UserError(_("The Product category is not analytic account please insert !! "))


			date = fields.date.today()
			journal_id = self.env['account.journal'].search([('type','=','general'),('code','=','stock')], limit=1)
			company_currency = self.company_id.currency_id.id
			amount = line.product_id.standard_price * line.quantity_done
			if not journal_id:
				raise UserError(_('You have not stock journal !!!'))

			move_id = self.create_move(
				ref=self.product_id.name,
				journal_id=journal_id.id,
				picking_id=self.id,
				date=date)

			credit_line = self.create_move_line(
				name=self.product_id.name,
				move_id=move_id.id,
				partner_id=self.partner_id.id,
				account_id=stock_account_id,
				credit=amount,
				amount_currency=amount *-1,
				currency_id=company_currency,
				analytic_account_id=analytic_account_id,
				analytic_tag_ids = False)

			debit_line = self.create_move_line(
				name=self.product_id.name,
				move_id=move_id.id,
				partner_id=self.partner_id.id,
				account_id=category_account_id,
				debit=amount,
				amount_currency=amount,
				currency_id=company_currency,
				date=date)
			move_id.post()


	def create_move(self, ref, journal_id, picking_id,date=False):
		move = self.env['account.move']
		vals = {
		'ref': ref,
		'journal_id': journal_id,
		'picking_id':picking_id,
		'date' : date,
		}
		return move.create(vals)

	def create_move_line(self,partner_id=False, name=False, move_id=False, account_id=False, debit=False, credit=False, date=False, amount_currency=False, currency_id=False, analytic_account_id=False, analytic_tag_ids=False):
		move_line = self.env['account.move.line']
		vals = {
			'name': name,
			'partner_id': partner_id,
			'move_id': move_id,
			'account_id': account_id,
			'debit': debit,
			'credit': credit,
			'date_maturity' : date,
			'amount_currency' : amount_currency,
			'currency_id' : currency_id,
			'analytic_account_id' : analytic_account_id,
			'analytic_tag_ids': analytic_tag_ids,
		}
		return move_line.with_context(check_move_validity=False).create(vals)


	@api.multi
	def show_moves(self):
		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'tree,form',
			'res_model' : 'account.move',
			'domain' : [('picking_id','=', self.id )],
		}


	def _prepare_po_lines(self):
		location_id = self.location_id
		po_lines = []
		for rec in self:
			if rec.line_ids:
				for line in rec.line_ids:
					product_quant = self.env['stock.quant'].search([('company_id','=',self.company_id.id),('location_id','=',location_id.id),('product_id','=',line.item_id.id)])
					quant_locs = self.env['stock.quant'].search([('product_id', '=', line.item_id.id),('location_id','=',self.location_id.id)])

					if line.qty > quant_locs.quantity:
						po_lines.append((0,0,{
								'product_id':line.item_id.id,
								'product_qty': abs(line.qty - quant_locs.quantity),
								'planned_date':line.date,
								}))
		return po_lines


	@api.multi
	def button_validate(self):


		res = super(stockPicking, self).button_validate()

		for record in self:
			precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			no_receipt_quantities = all(float_is_zero(move_line.quantity_done,  precision_digits=precision_digits) for move_line in record.move_ids_without_package)
			if no_receipt_quantities:
				raise UserError( _('You can not confirm request because all  reserved quantities is 0.0 !!'))


		if self.picking_type_id.code == 'incoming':
			self.custome_state = 'done'
			self.state = 'done'


		elif self.picking_type_id.code == 'internal' and self.internal_transfer_type == 'branch':
			warehouse_id = self.env['stock.warehouse'].sudo().search([('company_id','=',self.branch_id.id)],limit=1)
			location_id = self.env['stock.location'].sudo().search([('company_id','=',self.branch_id.id),('usage','in',['transit']),('is_for_internal_transfer','=',True)],limit=1)
			if not location_id:
				raise UserError(_("You have not transit location in '%s' branch to transfer please define !!! ") % self.branch_id.name)
			lines = []
			adj_lines = []

			for line in self.move_ids_without_package:
				line_vals = (0,0,{
					'product_id': line.product_id.id,
					'company_id': self.branch_id.id,
					'product_uom_qty': line.quantity_done,
					'date_expected': self.branch_scheduled_date,
					'location_id': location_id.id,
					'location_dest_id': self.branch_location.id,
					'name': line.product_id.name,
					'product_uom': line.product_id.uom_id.id
					})
				adj_line_vals = (0,0,{
					'product_id': line.product_id.id,
					'product_uom_id': line.product_id.uom_id.id,
					'product_qty': line.quantity_done,
					'company_id': self.branch_id.id,
					'location_id': location_id.id
					})
				lines.append(line_vals)
				adj_lines.append(adj_line_vals)
			if warehouse_id:
				branch_receipt = self.sudo().create({
					'company_id': self.branch_id.id,
					'scheduled_date': self.branch_scheduled_date,
					'origin':self.name,
					'location_id': location_id.id,
					'location_dest_id':self.branch_location.id,
					'picking_type_id': self.env['stock.picking.type'].sudo().search([('warehouse_id','=',warehouse_id.id),('code','=','internal')],limit=1).id,
					'info_company_id':self.company_id.id,
					'info_location_id':self.location_id.id,
					'branch_id': self.branch_id.id,
					'branch_location': self.branch_location.id,
					'move_ids_without_package':lines,
					'internal_transfer_type':self.internal_transfer_type,
					'branch_scheduled_date':self.branch_scheduled_date
					})


				branch_receipt.action_assign()

			# branch_inventory_adjustment = self.env['stock.inventory'].sudo().create({
			# 	'name': 'Branch stock moves '+ str(fields.Datetime.now()),
			# 	'location_id': location_id.id,
			# 	'filter':'partial',
			# 	'company_id': self.branch_id.id,
			# 	'line_ids': adj_lines
			# 	})
			# branch_inventory_adjustment.action_validate()

		elif self.picking_type_id.code == 'outgoing' and self.need_request_id and self.need_request_id.state in ['available','purchase','partially_available']:

			self._prepare_move()

			requests = self.env['stock.picking'].search([('need_request_id','=',self.need_request_id.id)])
			if all(pick.state == 'done' for pick in requests):
				self.need_request_id.state = 'done'
		return res


	@api.onchange('internal_transfer_type')
	def _domain_internal_transfer_type(self):
		res = {}
		if self.internal_transfer_type == 'branch':
			res['domain'] = {'location_dest_id':[('company_id','=',self.company_id.id),('usage','in',['transit'])]}
		else:
			res['domain'] = {'location_dest_id':[('company_id','=',self.company_id.id),('usage','in',['internal'])]}

		return res

class stockMove(models.Model):
	_inherit = 'stock.move'

	initial_qty = fields.Float('Inital Reception Qty', copy=False)
	qc_qty = fields.Float('Quality Check Qty', copy=False)



class stockPickingType(models.Model):

	_inherit = 'stock.picking.type'


	for_emloyees_request = fields.Boolean(default=False, string='Is used for Employees Requests?')


class stockLocation(models.Model):

	_inherit = 'stock.location'

	usage = fields.Selection(selection_add=[('employees','Employees')])
	is_for_internal_transfer = fields.Boolean(defalut=False)
	Warehouse_location_type = fields.Selection([('tasks','Tasks Warehouse'),('laboratories','Laboratories Warehouse'),('medical_supplies','Medical Supplies Warehouse'),('medicine','Medicine Warehouse')],default='tasks')




class StockQuant(models.Model):
	_inherit = 'stock.quant'

	product_id = fields.Many2one(
		'product.product', 'Product',
		ondelete='restrict', readonly=True, required=True, index=True)
	categ_id = fields.Many2one('product.category', string="Category")


	def create(self, vals):
		product = self.env['product.product'].search([('id','=',vals['product_id'])],limit=1)
		vals['categ_id'] = product.categ_id.id

		return super(StockQuant, self).create(vals)

	def set_categ(self):
		stock_qty = self.env['stock.quant'].search([])

		for rec in stock_qty:
			rec.update({'categ_id':rec.product_id.categ_id.id})


class AccountMove(models.Model):
	_inherit = 'account.move'

	picking_id = fields.Many2one('stock.picking')
