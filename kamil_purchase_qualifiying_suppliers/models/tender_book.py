# *.* encoding:utf-8 *.*

from odoo import models, fields, api, _
from datetime import datetime


class TenderBook(models.Model):

	_name = 'tender.book'
	_description = 'Tender Book'
	_rec_name = 'sequence'
	_order = 'id desc'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']


	READONLY_STATES = {
		'qualifier': [('readonly', True)],
		'unqualifier': [('readonly', True)],
	}


	sequence = fields.Char('Number',default='New', readonly=True)
	qualifier = fields.Boolean(default=False, help="Set qualifier to false to hide the Tender Book Tag without removing it.")
	issuing_date = fields.Date('Issuing Date', default=fields.Date.today(), states=READONLY_STATES,)
	deadline_date = fields.Date('Deadline Date', states=READONLY_STATES)
	received_date = fields.Date('Received Date', states=READONLY_STATES)
	vendor_name = fields.Char()
	vendor_email = fields.Char('Vendor Email')
	vendor_phone = fields.Char('Vendor Phone')
	terms = fields.Text(states=READONLY_STATES)
	general_conditions_ids =fields.Many2many('pr.general.conditions', string='General Conditions',states=READONLY_STATES)
	private_conditions = fields.Text('Private Conditions',states=READONLY_STATES) 
	other_features = fields.Text('Other Features',states=READONLY_STATES)
	requisition_id = fields.Many2one('purchase.requisition','Tender',states=READONLY_STATES)
	phone = fields.Char('Phone', track_visibility='onchange', track_sequence=5, states=READONLY_STATES, related='partner_id.phone')
	email = fields.Char('Email', help="Email address of the contact", track_visibility='onchange', track_sequence=4, index=True, states=READONLY_STATES,related='partner_id.email')
	area_rehabilitation_ids = fields.Many2many('area.rehabilitation','area_rehab_rel', string='Area of rehabilitation', states=READONLY_STATES)
	area_rehab_ids = fields.Many2many('area.rehabilitation','area_rel', states=READONLY_STATES, domain=lambda self:self._domain_area())
	state = fields.Selection([
					('draft','Draft'),
					('general_conditions_selection','General Conditions Selection'),
					('technical_selection','Technical Selection'),
					('to approve', 'To Approve'),
					('confirm','Confirm'),
					('qualifier','Qualifier'),
					('unqualifier','Unqualifier'),
					('done','Done'),
					('cancel','Cancel')
					],default='draft', string='States',track_visibility='onchange')

	company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id, states=READONLY_STATES)
	rep_attendee_ids = fields.One2many('rep.attendee', 'book_id', states=READONLY_STATES)
	partner_id = fields.Many2one('res.partner', 'Supplier',states=READONLY_STATES,track_visibility='onchange')
	visit_id = fields.Many2one('tender.book.visit', states=READONLY_STATES, track_visibility='onchange')
	committee_ids = fields.One2many('committee.members','book_id',string="Committee Members")
	visit_attach = fields.Binary('Visit Attachment')
	state_ids = fields.Many2many("res.country.state", string='State')
	country_ids = fields.Many2many('res.country', string='Country')
	active = fields.Boolean('Active', default=True)
	collection_id = fields.Many2one('collection.collection', string='Book Fees',track_visibility='onchange')
	visit_result = fields.Float('Result',track_visibility='onchange')


	@api.model
	def default_get(self, default_fields):
		res = super(TenderBook, self).default_get(default_fields)
		res['state_ids'] = [v.id for v in self.env['res.country.state'].search([])]
		res['country_ids'] = [v.id for v in self.env['res.country'].search([])]	
		return res 


	def _domain_area(self):
		request = self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
		return [('id','in',[v.area_rehabilitation_id.id for v in request.area_rehabilitation_line_ids])]
	
	@api.model
	def create(self, vals):
		seq_code = 'qualifying.suppliers.tender.book' + ' / ' + str(self._context.get('requisition')) + '.'
		seq = self.env['ir.sequence'].next_by_code( seq_code )

		if not seq :
			self.env['ir.sequence'].create({
				'name' : seq_code,
				'code' : seq_code,
				'prefix' : str(self._context.get('requisition')) + ' / TB',
				'number_next' : 1,
				'number_increment' : 1,
				'use_date_range' : True,
				'padding' : 4,
				})
			seq = self.env['ir.sequence'].next_by_code( seq_code )
		vals['sequence'] = seq
		return super(TenderBook, self).create(vals)

	@api.multi
	def action_check_general_conditions(self):
		self.write({'state':'general_conditions_selection'})

	@api.multi
	def action_confirm_book(self):
		self.write({'state':'confirm'})

	@api.multi
	def action_qualifier(self):
		self.partner_id.write({
			'qualified':True,
			'requisition_id':self.requisition_id.id,
			'book_id':self.id,
			'area_rehabilitation_ids': [(6, 0, [v.id for v in self.area_rehab_ids] )]
			})

		area_of_rehabilitaion = self.env['area.rehabilitation'].search([('id','in',self.area_rehab_ids.ids)])
		for rec in area_of_rehabilitaion:
			rec.write({'partner_ids':(0,0, self.partner_id.id)})
		vals_list = []
		for rec in self.requisition_id.area_rehabilitation_line_ids:
			vals_list = rec.partner_ids.ids
			if rec.area_rehabilitation_id.id in [v.id for v in self.area_rehab_ids] :
				vals_list.append(self.partner_id.id)
			rec.write({'partner_ids':[(6,0,vals_list)]})

		self.write({'state': 'qualifier','qualifier':True})

	@api.multi
	def action_unqualifier(self):
		self.write({'state': 'unqualifier'})

	@api.multi
	def print_visit_template(self):
		return self.env.ref('kamil_purchase_qualifiying_suppliers.action_visit_report').report_action(self)

	@api.multi
	def action_technical_selection(self):
		if self.requisition_id:
			self.write({'state':'technical_selection'})
		else:
			self.write({'state':'confirm'})


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
			 'url':"/tenderbook/" + str(id),
			  'target': 'new', # open in a new tab
		}

	@api.multi
	def send_book_email(self):
		template_id = self.env.ref('kamil_purchase_qualifiying_suppliers.email_template_qs_tender_book', False)
		mail_template = self.env['mail.template'].browse(template_id.id)
		mail_template.send_mail(self.id, force_send=True, raise_exception=True)


	@api.multi
	def send_email_done(self):
		template_id = self.env.ref('kamil_purchase_qualifiying_suppliers.email_template_done_tender_book', False)
		mail_template = self.env['mail.template'].browse(template_id.id)
		mail_template.send_mail(self.id, force_send=True, raise_exception=True)

		
class RepAttendee(models.Model):

	_name = 'rep.attendee'
	_description = 'Representative attendee'

	name = fields.Char('Name', required=True)
	phone = fields.Char('Phone')
	email = fields.Char('Email')
	book_id = fields.Many2one('tender.book', 'Book Number')
	tender_id = fields.Many2one('purchase.requisition')
	vendor_name = fields.Char(related='book_id.vendor_name')
	order_id = fields.Many2one('purchase.order', 'Book Order')
	type = fields.Selection(related='tender_id.type')
	partner_id = fields.Many2one('res.partner')

	# Fields for address, due to separation from Suppliers and res.partner

	street = fields.Char('Street')
	street2 = fields.Char('Street2')
	zip = fields.Char('Zip', change_default=True)
	city = fields.Char('City')
	state_id = fields.Many2one("res.country.state", string='State')
	country_id = fields.Many2one('res.country', string='Country')
	phone = fields.Char('Phone', track_visibility='onchange', track_sequence=5)
	mobile = fields.Char('Mobile')
	title = fields.Many2one('res.partner.title')
	company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)

	@api.onchange('book_id')
	def onchange_book_id(self):
		self.partner_id = self.book_id.partner_id

	@api.onchange('order_id')
	def onchange_order_id(self):
		self.partner_id = self.order_id.partner_id

	@api.model
	def create(self, vals):
		res = super(RepAttendee, self).create(vals)
		val = []
		val.append((0,0 ,{
				'name': res['name'],
				'phone': res['phone'],
				'email': res['email'],
				'street': res['street'],
				'street2': res['street2'],
				'zip': res['zip'],
				'city': res['city'],
				'state_id': res['state_id'].id,
				'country_id': res['country_id'].id,
				'type':'contact'
				}))
		pr = self.env['res.partner'].search([('id','=',res['partner_id'].id)])
		pr.write({'child_ids':val})
		return res

class Visit(models.Model):
	
	_name = 'tender.book.visit'
	_description = 'Tender Book Visit'
	_rec_name = 'sequence'

	sequence = fields.Char(readonly="1")
	year = fields.Char('Year', default=datetime.now().year)
	book_id = fields.Many2one('tender.book')
	visit_line_ids = fields.One2many('tender.book.visit.line','visit_id', readonly='1')
	requisition_id = fields.Many2one('purchase.requisition')
	partner_id = fields.Many2one('res.partner', related='book_id.partner_id')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)

class VisitLine(models.Model):

	_name = 'tender.book.visit.line'
	_description = 'Tender Book Visit Line'

	visit_id = fields.Many2one('tender.book.visit')

	criteria_id = fields.Many2one('tender.book.visit.criteria')
	required_score = fields.Float('Required Score')
	obtained_score = fields.Float('Obtained Score')
	note = fields.Text('Notes') 
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)				
	

class Criteria(models.Model):

	_name = 'tender.book.visit.criteria'
	_description = 'tender book visit criteria'
	
	name = fields.Char('Name')		
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)