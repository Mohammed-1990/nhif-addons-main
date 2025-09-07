from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError

class Receipt67(models.Model):
	_name = 'collection.receipt_67'
	_description = '67 Receipt'
	_order = 'ref desc'
	_rec_name = 'ref'
	_inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']

	ref = fields.Char(string='Number')
	collector_id = fields.Many2one('hr.employee',string='Collector',default= lambda self:self.get_collector())
	date = fields.Date(default=lambda self: fields.Date.today())
	journal_id = fields.Many2one('account.journal',string='Bank/Cash')
	name = fields.Text(string='Description',track_visibility='always')
	journal_account_id = fields.Many2one('account.account', string='journal Account')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('permited','Permited'),('returned_to_collector','Returned to Collector'),('audited','Audited'),('returned_to_supervisor','Returned to Supervisor')],default='draft', )
	collection_ids = fields.One2many('collection.collection','receipt_67_id' )
	amount = fields.Float(string='Total Amount', compute='compute_amount', store=True)
	company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
	frist_ref_no = fields.Char(string='F Number')
	last_ref_no = fields.Char(string='L Number')
	collection_type = fields.Selection([('Cheque','Cheque'),('cash','Cash'),('bank_transfer','Bank Transfer'),('counter_cheque','Counter Cheque'),('e_bank','E Bank')], default='cash',track_visibility='always')
	select_all = fields.Boolean(string="Select All E15")
	pid_amount = fields.Float(string="Pid Amount", track_visibility='always')


	@api.onchange('collection_type')
	def onchange_collection_type(self):
		for record in self:
			if record.collector_id and record.collection_type:
				collection_ids_list = []
				for collection in self.env['collection.collection'].search([('collector_id','=',record.collector_id.id),('collection_type','=',record.collection_type),('state','=','confirmed')]):
					collection_ids_list.append( collection.id )
				record.collection_ids = [(6,0, collection_ids_list )]



	@api.onchange('select_all')
	def _onchange_select_all(self):
		for rec in self:
			if rec.collection_ids:
				for line in rec.collection_ids:
					line.is_select_receipt_e15 = rec.select_all

	@api.multi
	def do_confirm(self):
		if any(rec.cancel_e15_state in ['send','accept'] for rec in self.collection_ids):
			raise ValidationError(_(
				"تم طلب الغاء الايصال لايمكن اجراء تاكيد 67 الا بعد موافقة المشرف او رفض الطلب ") )
		if not self.collection_ids.filtered(lambda l: l.is_select_receipt_e15):
			raise ValidationError(_("يجب اختيار بند واحد على الأقل"))
		
		for record in self:
			record.collection_ids = record.collection_ids.filtered(lambda l: l.is_select_receipt_e15)
			for collection in record.collection_ids:
				collection.state = '67_issued'
			record.state = 'confirmed'

	@api.multi
	def do_permit(self):
		for record in self:
			for collection in record.collection_ids:
				collection.state = '67_permited'
			record.state = 'permited'

	@api.multi
	def do_return_to_collector(self):
	
		
		self.ensure_one()
		return {
			'name': _('Return Receipt E15'),
			'res_model': 'returned.collector.e15.wizard',
			'view_mode': 'form',
			'context': {
				'active_model': 'collection.receipt_67',
				'default_receipt_67_id': self.id,
			},
			'target': 'new',
			'type': 'ir.actions.act_window',
		}

		# for record in self:
		# 	for collection in record.collection_ids:
		# 		collection.state = 'returned_to_collector'
		# 	record.state = 'returned_to_collector'
	@api.multi
	def show_collection_collection_details(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'collection.collection.line',
			'view_mode': 'tree',
		}
	

	@api.multi
	def do_return_to_supervisor(self):
		for record in self:
			for collection in record.collection_ids:
				collection.state = 'returned_to_supervisor'
			record.state = 'returned_to_supervisor'


	@api.multi
	def do_audit(self):
		for record in self:
			for collection in record.collection_ids:
				collection.state = 'audited'
			record.state = 'audited'
	



	@api.model
	def create(self, vals):
		create_id = super(Receipt67, self).create(vals)
		list =[]

		if create_id.date:
			seq_code = 'collection.receipt_67.sequence.' + str(create_id.date.year) + '.' + str(create_id.date.month)
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  str(create_id.date.year) + '-' +  str(create_id.date.month) + '-' ,
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
				

			create_id.ref = seq
		if create_id.collection_ids:
			for line in create_id.collection_ids:
				if line:
					list.append(line.ref)
			create_id.frist_ref_no = list[0]
			create_id.last_ref_no = list[-1]
		return create_id


	@api.multi
	def write(self, vals):
		write_id = super(Receipt67, self).write(vals)
		if vals.get('date', False):
			seq_code = 'collection.receipt_67.sequence.' + str(self.date.year) + '.' + str(self.date.month)
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  str(self.date.year) + '-' +  str(self.date.month) + '-' ,
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			self.ref = seq
		return write_id



	# @api.model
	# def create(self, vals):
	# 	vals['ref'] = self.env['ir.sequence'].next_by_code('receipt_67.sequence') or '/'
	# 	collection_ids_list = []
	# 	for collection in self.env['collection.collection'].search([('collector_id','=',vals['collector_id']),('state','=','confirmed')]):
	# 		collection_ids_list.append( collection.id )
	# 	vals['collection_ids'] = [(6,0, collection_ids_list )]
	# 	return super(Receipt67,self).create(vals)


	@api.multi
	def get_collector(self):
		for employee in self.env['hr.employee'].search([('user_id','=',self.env.user.id),('company_id','=',self.env.user.company_id.id),('is_collector','=',True)]):
			return employee.id
		return False


	@api.multi
	@api.depends('collection_ids','collection_ids.is_select_receipt_e15')
	def compute_amount(self):
		for record in self:
			total = 0
			for line in record.collection_ids.filtered(lambda line: line.is_select_receipt_e15 == True):
				total = total + line.amount
			record.amount = total



	@api.multi
	@api.onchange('collector_id')
	def onchange_collector_id(self):
		for record in self:
			if record.collector_id and record.state == 'draft':
				collection_ids_list = []
				for collection in self.env['collection.collection'].search([('collector_id','=',record.collector_id.id),('collection_type','=',record.collection_type),('state','=','confirmed')]):
					collection_ids_list.append( collection.id )
				record.collection_ids = [(6,0, collection_ids_list )]




	@api.multi
	@api.onchange('journal_id')
	def onchange_journal_id(self):
		for record in self:
			if record.journal_id:
				if record.journal_id.default_debit_account_id:
					record.journal_account_id = record.journal_id.default_debit_account_id.id

	@api.multi
	def open_bank_save_supply(self):
		partner_id = False
		account_id = False
		supply_type = False
		amount =  self.amount
		if self.collector_id.user_id:
			if self.collector_id.user_id.commercial_partner_id:
				partner_id = self.collector_id.user_id.commercial_partner_id.id
		if self.collector_id.collector_account_id:
			account_id = self.collector_id.collector_account_id.id
		if self.collection_type :
			if self.collection_type == 'cash':
				supply_type = '39_receipt'
			else:
				supply_type = 'bank_supply'


		return {
			'type' : 'ir.actions.act_window',
			'view_mode' : 'tree,form',
			'res_model' : 'money.supply',
			'domain' : [('receipt_67_id','=', self.id )],
			'context':{
				'default_receipt_67_id':self.id,
				'default_partner_id' : partner_id,
				'default_account_id' : account_id,
				'default_pid_amount' : self.pid_amount,
				'default_total_amount' : amount,
				'default_supply_type' : supply_type,


			}
		}
	

	@api.multi
	def unlink(self):
		for record in self:
			if record.state not in ['draft']:
				raise ValidationError(_('لا يمكن حذف هذا السجل إلا إذا كان في حالة مسودة'))
			
			if any(rec.cancel_e15_state in ['accept'] for rec in record.collection_ids):
				raise ValidationError(_('لا يمكن حذف هذا السجل بعد قبول طلب إلغاء الإيصال'))

		return super(Receipt67, self).unlink()






class Collection(models.Model):
	_inherit = 'collection.collection'

	receipt_67_id = fields.Many2one('collection.receipt_67')



class MoneySupply(models.Model):
	_inherit = 'money.supply'

	receipt_67_id = fields.Many2one('collection.receipt_67', copy=False)

	@api.model
	def create(self, vals):
		if self._context.get('default_receipt_67_id',False):
			vals['receipt_67_id'] = self._context['default_receipt_67_id']

		return super(MoneySupply, self).create(vals)

	@api.multi
	def do_validate(self):
		do_valid = super(MoneySupply, self).do_validate()
		if self.receipt_67_id:
			for receipt in self.env['collection.receipt_67'].search([('id','=',int(self.receipt_67_id))]):
				for collection in receipt.collection_ids:
					collection.state = 'collected'
		return do_valid

