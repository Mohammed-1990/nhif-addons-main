# *.* coding:utf-8 *.*

from odoo import models, fields, api, _


from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from datetime import datetime
from datetime import datetime, date




READONLY_STATES = {
	'done': [('readonly', True)],
	'cancel': [('readonly', True)],
}

PURCHASE_REQUISITION_STATES = [
	('draft','Draft'),
	('finance_admin_purchase_dept)','Administration and Financial Manager /Purchase Department'),
	('gen_man_appr','General Manager Approval'),
	('announcement','Announcement'),
	('comm_decided','Committee Decided'),
	('general_conditions_selection','General Conditions Selection'),
	('technical_selection','Technical Selection'),
	('qualifying_suppliers_valuat','Qualifying Suppliers Valuation'),
	('suppliers_valuation','Suppliers Valuation'),
	('finance_admin_apprv','Administration and Financial Manager Approval'),
	('gm_sign','General Manager Signature'),
	('internal_refrance','Internal Refrance'),
	('in_progress','In Progress'),
	('ongoing', 'Ongoing'),
	('in_progress', 'Confirmed'),
	('open', 'Bid Selection'),
	('done','Done'),
	('cancel','Cancel')
]

class QualifyingSuppliers(models.Model):

	_inherit = 'purchase.requisition'

	sequence = fields.Char('Request ID', readonly=True)
	name = fields.Char(string='Description', default='', required=True, copy=False)
	admin_id = fields.Many2one('hr.department', string="Administration", default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.parent_id, readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id, readonly="1")
	area_rehabilitation_line_ids = fields.One2many('area.rehabilitation.line', 'vendor_rehabilitation_id',track_visibility='always', string="Area Rehabilitation")
	type = fields.Selection([('qualifying_suppliers','Qualifying Suppliers'),
							('public_tender','Public Tender'),
							('limited_tender','Limited Tender')],
							'Type',default='qualifying_suppliers'
							)
	general_conditions_ids =fields.Many2many('pr.general.conditions',string='General Conditions',states=READONLY_STATES, track_visibility='always')
	private_conditions = fields.Text('Private Conditions',track_visibility='always') 
	state = fields.Selection([
							('draft','Draft'),
							('finance_admin_purchase_dept)','Administration and Financial Manager /Purchase Department'),
							('gen_man_appr','General Manager Approval'),
							('announcement','Announcement'),
							('comm_decided','Committee Decided'),
							('general_conditions_selection','General Conditions Selection'),
							('technical_selection','Technical Selection'),
							('qualifying_suppliers_valuat','Suppliers Valuation'),
							('suppliers_valuation','Suppliers Valuation'),
							('finance_admin_apprv','Administration and Financial Manager Approval'),
							('gm_sign','General Manager Signature'),
							('internal_refrance','Internal Refrance'),
							('in_progress','In Progress'),
							('ongoing', 'Ongoing'),
							('in_progress', 'Confirmed'),
							('open', 'Bid Selection'),
							('done','Done'),
							('cancel','Cancel'),
							],default='draft',track_visibility='always')
	state_blanket_order = fields.Selection(PURCHASE_REQUISITION_STATES, compute='_set_state')
	tender_book_ids = fields.One2many('tender.book', 'requisition_id',track_visibility='always')
	book_count = fields.Integer(compute='_compute_book_count')
	announcement = fields.Html(string='Announcement',track_visibility='always')
	announ_number = fields.Integer('Number Of Announcement')
	announ_attach = fields.Binary('Announcement Attach File')
	announcement_ids = fields.One2many('purchase.requisition.announcement','requisition_id', string="NewsPaper", track_visibility='always')
	rep_attendee_ids = fields.One2many('rep.attendee', 'tender_id')
	rep_attendee_count = fields.Integer(compute='_compute_rep_attendee')
	year = fields.Char('Year', default=datetime.now().year)
	ordering_date = fields.Date(string="Ordering Date", track_visibility='onchange')
	finance_admin_signature = fields.Binary('Financial Administration Signature',states=READONLY_STATES)
	gm_signature = fields.Binary('General Manager Signature',states=READONLY_STATES)
	internal_refrance_signature = fields.Binary('Internal Transfer Signature',states=READONLY_STATES)
	state_id = fields.Many2many("res.country.state", string='State')
	country_id = fields.Many2many('res.country', string='Country')
	visit_id = fields.Many2one('visit.template', 'Visit Template')
	email_to = fields.Char(default='/tender/tenderbook/')
	commitee_selection_id = fields.Many2one('committee.committee', 'Committee Selection', domain=lambda self:self._domain_commitee())
	committee_member_ids = fields.One2many('committee.members','requisition_id',string="Committee Members")
	committee_attach = fields.Binary('Required Documents Signature Attachment')
	check_book = fields.Boolean(default=False)
	count_partner = fields.Integer('Qualifiers', compute='_compute_count_partner')
	technical_report = fields.Binary('Technical Report')
	commitee_report = fields.Binary('Committee Report')
	company_id = fields.Many2one('res.company', string='Branch', required=True, default=lambda self: self.env['res.company']._company_default_get('purchase.requisition'))


	def _domain_commitee(self):
		return [('state','=','active'),('committee_type.types','=','purchase')]


	@api.multi
	def _compute_count_partner(self):
		partner = self.env['res.partner'].search_count([('requisition_id','=',self.id)])
		self.count_partner = partner


	@api.multi
	def name_get(self):
		result = []
		for rec in self:
			name = rec.name + ' [' + rec.sequence + ']' 
			result.append((rec.id, name))
		return result


	@api.multi
	@api.constrains('area_rehabilitation_line_ids')
	def _check_area(self):
		for rec in self:
			if rec.type == 'qualifying_suppliers':
				if not rec.area_rehabilitation_line_ids:
					raise UserError(_("The Area Rehabilitation is not exist please entered."))



	@api.onchange('commitee_selection_id')
	def onchange_commitee_selection_id(self):
		vals = []
		for rec in self.commitee_selection_id.committee_member:
			vals.append((0,0,{
				'employee':rec.employee.id,
				'role':rec.role.id,
				}))
		self.committee_member_ids = vals


	@api.multi
	def action_required_documents(self):
		return self.env.ref('kamil_purchase_qualifiying_suppliers.action_required_documents_report').report_action(self)


	@api.model
	def default_get(self, default_fields):
		res = super(QualifyingSuppliers, self).default_get(default_fields)
		vals = []
		general_conditions_obj = self.env['general.conditions'].search([('type','=',self._context.get('default_type'))])
		for line in general_conditions_obj.general_conditions_lines:
			vals.append((0, 0, {
					'name':line.name,             
				}))
		committee = self.env['committee.committee'].search([('committee_type','=','Tender Selection Committee')])

		res['ordering_date'] = datetime.now()
		res['general_conditions_ids'] = vals
		res['state_id'] = [v.id for v in self.env['res.country.state'].search([])]
		res['country_id'] = [v.id for v in self.env['res.country'].search([])]	
		return res 

	@api.model
	def create(self, vals):
		if self._context.get('default_type') == 'qualifying_suppliers':
			seq_code = 'purchase.requisitioin.qualifying.suppliers' + '-' + str(datetime.now().year) + '-' + '.'
			seq = self.env['ir.sequence'].next_by_code( seq_code )
			
			if not seq:
				self.env['ir.sequence'].create({
					'name' : seq_code,
					'code' : seq_code,
					'prefix' :  'QS-' +str(datetime.now().year) + '-',
					'number_next' : 1,
					'number_increment' : 1,
					'use_date_range' : True,
					'padding' : 4,
					})
				seq = self.env['ir.sequence'].next_by_code( seq_code )
			vals['sequence'] = seq
		return super(QualifyingSuppliers, self).create(vals)


	@api.multi
	def announcemnt_confirm(self):
		
		if not self.announ_number: 
			raise UserError(_("The Announcement is not exist please entered."))
		if self.type == 'qualifying_suppliers':
			if not self.visit_id:
				raise UserError(_("The Visit is not exist please entered."))
		self.write({'state':'gen_man_appr'})
			
	@api.multi
	def action_gen_man_appr(self):
		self.write({'state': 'announcement'})		
		


	@api.multi
	def action_comm_decided(self):
		if not self.rep_attendee_ids:
			raise UserError(_("The Representative attendee is not exist please entered."))
		self.write({'state':'general_conditions_selection'})

	@api.multi
	def action_comm_selection(self):
		self.write({'state':'finance_admin_apprv'})

	@api.multi
	def action_finance_admin_apprv(self):
		if not self.finance_admin_signature:
			raise UserError(_("The finance admin signature attachment is not exist please entered."))
		if self.type in ('public_tender','limited_tender'):
			count = self.env['purchase.order'].search_count([('id','in',self.purchase_ids.ids),('state','=','purchase')])
			if not count: 
				raise UserError(_("Select because at least one book to purchase."))
			else:
				for rec in self.purchase_ids:
					if rec.state != 'purchase':
						rec.write({'state':'cancel'})
		if self.type == 'qualifying_suppliers':
			count = self.env['tender.book'].search_count([('id','in',self.tender_book_ids.ids),('state','=','qualifier')])
			if not count: 
				raise UserError(_("Select at least one book qualifier.!!!!!"))
			else:
				for rec in self.tender_book_ids:
					if rec.state != 'qualifier':
						rec.write({'state':'unqualifier'})
		self.write({'state':'gm_sign'})

	@api.multi
	def action_gm_sign(self):
		self.write({'state':'internal_refrance'})

	@api.multi
	def action_internal_refrance(self):
		self.write({'state':'done'})

	@api.multi
	def action_gcs_confirm(self):
		if not self.committee_attach:
			raise UserError(_("The committee attachment is not exist please entered."))
		if not self.committee_member_ids:
			raise UserError(_("The committee member is not exist please entered."))
		
		if self.type == 'qualifying_suppliers':
			self.write({'state':'qualifying_suppliers_valuat'})
			# self.action_suppliers_valuation_confirm()
		else:
			self.write({'state':'technical_selection'})



	@api.multi
	def action_suppliers_valuation_confirm(self):
		self.write({'state':'finance_admin_apprv'})	

	@api.multi
	def action_technical_selection(self):
		self.write({'state':'suppliers_valuation'})	

	# @api.multi
	# def action_valuation_confirm(self):
	# 	self.write({'state':'finance_admin_apprv'})	


	@api.multi
	def _compute_book_count(self):
		for book in self:
			book.book_count = len(book.tender_book_ids)
			confirm_book = self.env['tender.book'].search([('id','in',self.tender_book_ids.ids),('state','=','qualifier')])
			book.qualified_book_count = len(confirm_book.ids)


			
	@api.multi
	def _compute_rep_attendee(self):
		for attendee in self:
			attendee.rep_attendee_count = len(attendee.rep_attendee_ids)


	@api.multi
	def print_qualifying_supplier(self):
		""" Print the Qaulifying supplier report of year 
			easily the next step of the workflow
		"""
		return self.env.ref('kamil_purchase_qualifiying_suppliers.action_report_qualifying_suppliers').report_action(self)
		
		# if self.user_has_groups('account.group_account_invoice'):
		#     return self.env.ref('account.account_invoices').report_action(self)
		# else:
		#     return self.env.ref('account.account_invoices_without_payment').report_action(self)
	

	@api.multi
	def print_area_rehabilitaion(self):
		return self.env.ref('kamil_purchase_qualifiying_suppliers.action_report_area_rehabilitaion').report_action(self)


	@api.multi
	def action_announce_send(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('kamil_purchase_qualifiying_suppliers', 'email_template_announcement')[1]
			
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			
			compose_form_id = False
		ctx = dict(self.env.context or {})
		ctx.update({
			'default_model': 'purchase.requisition',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			# 'custom_layout': "mail.mail_notification_paynow",
			'force_email': True,
			# 'mark_rfq_as_sent': True,
		})

		# In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
		# object. Therefore, we pass the model description in the context, in the language in which
		# the template is rendered.
		lang = self.env.context.get('lang')
		if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
			template = self.env['mail.template'].browse(ctx['default_template_id'])
			if template and template.lang:
				lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

		self = self.with_context(lang=lang)
		if self.state in ['draft', 'sent']:
			ctx['model_description'] = _('Request for Quotation')
		else:
			ctx['model_description'] = _('Purchase Order')

		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	def default_picking_type(self):
		type_obj = self.env['stock.picking.type']
		company_id = self.env.context.get('company_id') or self.env.user.company_id.id
		types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
		if not types:
			types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
		return types[:1].id



	def create_books(self):
		for record in self:
			if record.type in ['qualifying_suppliers','public_tender','limited_tender'] :
				for partner_id in record.recipients_ids:
					record.prepare_book(partner_id=prepare_book,requisition_id=record.id, coll=0 )			
					
	def prepare_book(self, partner_id, requisition_id, coll):

		collection = self.env['collection.collection'].browse(coll).id
		vals = []
		for rec in requisition_id.general_conditions_ids:
			vals.append((0, 0, {
					'name':rec.name
				}))
			
		if requisition_id.type == 'qualifying_suppliers':
			book = self.env['tender.book']
			book = book.with_context({'requisition':requisition_id.sequence}).create({
					'partner_id':partner_id.id,
					'requisition_id':requisition_id.id,
					'type':requisition_id.type,
					'general_conditions_ids':vals,
					'private_conditions':requisition_id.private_conditions,
					'collection_id': collection
						})
			if partner_id.email:
				book.send_book_email()

		else:
			book = self.env['purchase.order']
			book = book.with_context({'requisition':requisition_id.sequence, 'type':requisition_id.type}).create({
					'partner_id':partner_id.id,
					'requisition_id':requisition_id.id,
					'type':requisition_id.type,
					'general_conditions_ids':vals,
					'type': requisition_id.type,
					'private_conditions': requisition_id.private_conditions,
					'collection_id': collection,
					'picking_type_id':self.default_picking_type()
						})
			book._onchange_requisition_id()
			if partner_id.email:
				book.send_book_email()
		requisition_id.check_book = True
		return book

	
	@api.multi
	def action_confirm_announcment(self):

		if self.type in ['qualifying_suppliers','public_tender','limited_tender'] :
			
			for partner_id in self.recipients_ids:
				# collection = self.env['collection.collection'].browse(coll).id
				vals = []
				for rec in self.general_conditions_ids:
					vals.append((0, 0, {
							'name':rec.name
						}))
					
				if self.type == 'qualifying_suppliers':
					book = self.env['tender.book']
					book = book.with_context({'requisition':self.sequence}).create({
							'partner_id':partner_id.id,
							'requisition_id':self.id,
							'type':self.type,
							'general_conditions_ids':vals,
							'private_conditions':self.private_conditions,
							# 'collection_id': collection
								})
					if partner_id.email:
						book.send_book_email()

				else:
					book = self.env['purchase.order']
					book = book.with_context({'requisition':self.sequence, 'type':self.type}).create({
							'partner_id':partner_id.id,
							'requisition_id':self.id,
							'type':self.type,
							'general_conditions_ids':vals,
							'type': self.type,
							'private_conditions': self.private_conditions,
							# 'collection_id': collection,
							'picking_type_id':self.default_picking_type()
								})
					book._onchange_requisition_id()
					if partner_id.email:
						book.send_book_email()
				self.check_book = True

		self.write({'state':'comm_decided'})


class CommitteeMembers(models.Model):
	_name = 'committee.members'
	_description = 'Committee members'

	employee = fields.Many2one('hr.employee',string="Employee", required=True)
	role = fields.Many2one('committee.role',string="Position", required=True)
	requisition_id = fields.Many2one('purchase.requisitioin')
	book_id = fields.Many2one('tender.book')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env['res.company']._company_default_get('committee.members'))

class NewsPaper(models.Model):

	_name = 'announcement.newspaper'
	_description = 'NewsPaper'

	name = fields.Char('Name', required=True)
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env['res.company']._company_default_get('announcement.newspaper'))	


class PurchaseRequisitionGeneralConditions(models.Model):

	_name = 'pr.general.conditions'
	_description = 'Purchase Requisition General Conditions'

	name = fields.Char('Conditions',translate=True)
	attachments = fields.Binary('Attachment')
	requisition_id = fields.Many2one('purchase.requisition')
	exist = fields.Boolean('Exist' , default=False )
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env['res.company']._company_default_get('pr.general.conditions'))	
		
class AreaRehabilitation(models.Model):

	_name = 'area.rehabilitation'
	_description = 'Area Rehabilitation'

	name = fields.Char('Area Of Rehabilitation', required=True)
	partner_ids = fields.Many2many('res.partner','partner_id_rel')
	count_partner = fields.Integer(compute='_compute_count_partner')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

	@api.depends('partner_ids')
	@api.multi
	def _compute_count_partner(self):
		for partner in self:
			self.count_partner = len(partner.partner_ids)

	@api.multi
	def action_partner_open(self):
		return{
			'name':'Suppliers',
			'type':'ir.actions.act_window',
			'res_model':'res.partner',
			'view_mode':'tree,form',
			'target':'current',
			'domain':[('id','in',self.partner_ids.ids)]
		}

class AreaRehabilitationLine(models.Model):

	_name = 'area.rehabilitation.line'
	_description = 'Area Rehabilitation Line'
	_rec_name = 'area_rehabilitation_id'

	area_rehabilitation_id = fields.Many2one('area.rehabilitation', required=True)
	vendor_rehabilitation_id = fields.Many2one('purchase.requisition')
	tendor_book_id = fields.Many2one('tender.book')
	partner_ids = fields.Many2many('res.partner', string='Suppliers', readonly=True)
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

class GeneralConditions(models.Model):

	_name = 'general.conditions'
	_description = 'General Conditions'
	_rec_name = 'type'

	type = fields.Selection([
					('qualifying_suppliers','Qualifying Suppliers'),
					('public_tender','Public Tender'),
					('limited_tender','Limited Tender'),
					('scrap_request','Scrap Request')],
					'Type',Index=True ,default='qualifying_suppliers', required=True)

	general_conditions_lines = fields.One2many('general.conditions.line','general_conditions_id')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

	_sql_constraints = [('type_unique','UNIQUE(type)','General Conditions type is already exist!!!!'),('name','UNIQUE(name)','General Conditions type is Name exist!!!!')]



class GeneralConditionsLine(models.Model):

	_name = 'general.conditions.line'
	_description = 'General Conditions Line'

	name = fields.Char('Conditions', required=True)
	general_conditions_id = fields.Many2one('general.conditions')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
		
class Announcement(models.Model):

	_name = 'purchase.requisition.announcement'
	_description = 'Purchase Requisition Announcement'

	newsPaper_id = fields.Many2one('announcement.newspaper','NewsPaper')
	release_date = fields.Date('Release Date')
	release_number = fields.Char('Release Number')
	attach = fields.Binary('Attachment')
	requisition_id = fields.Many2one('purchase.requisition')
	color = fields.Integer('Color Index')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

class VisitTempalate(models.Model):
	_name = 'visit.template'
	_description = 'Visit Template'

	name = fields.Char('Name')
	visit_ids = fields.One2many('visit.line','visit_template_id')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

class VisitLine(models.Model):
	_name = 'visit.line'
	_description = 'visit Line'

	visit_template_id = fields.Many2one('visit.template')

	criteria_id = fields.Many2one('tender.book.visit.criteria')
	required_score = fields.Float('Required Score')
	obtained_score = fields.Float('Obtained Score')
	note = fields.Text('Notes') 
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)