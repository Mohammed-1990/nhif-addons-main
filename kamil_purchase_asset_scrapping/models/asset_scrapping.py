# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from lxml import etree

class ScrapRequest(models.Model):

	_name = 'scrap.request'
	_description = 'Asset Scrap Request'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_order = 'id desc'


	READONLY_STATES = {
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}


	name = fields.Char('Scrap Name', required=True)
	user_id = fields.Many2one('res.users', string='Organization', index=True, track_visibility='onchange', default=lambda self: self.env.user, readonly=True)
	admin_id = fields.Many2one('hr.department', string="Administration", states=READONLY_STATES, default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.parent_id, readonly="1")
	dept_id = fields.Many2one('hr.department', 'Department', states=READONLY_STATES, default= lambda self: self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id, readonly="1")
	ordering_date = fields.Date('Ordering Date', default=fields.Date.today(), required="1")
	state = fields.Selection([
						('draft','Draft'),
						('manager_director','Manager Director'),
						('gen_man_appr','General Manager'),
						('director_finance_admin','Director and finance and administrative'),
						('comm_decided','Committee Decided'),
						('gen_man_appr2','General Manager'),
						('announcement','Announcement'),
						('auction','Auction'),
						('finance_admin_apprv','Administration and Financial Manager'),
						('finance_manger_apprv','Financial Manager'),
						('done','Done'),
						('cancel','Cancel'),
						],default='draft', track_visibility='onchange')
	type = fields.Selection([
						('scrap','Scrap'),
						('dynamic','Dynamic')],string='Type',default='scrap')
	asset_ids = fields.One2many('asset.request','scrap_id')
	asset_line_ids = fields.One2many('scrap.request.line','scarp_request_id','Assets')
	general_conditions_ids =fields.Many2many('pr.general.conditions',string='General Conditions',states=READONLY_STATES)
	private_conditions = fields.Text('Private Conditions') 
	announcement = fields.Html(string='Announcement')
	announ_number = fields.Integer('Number Of Announcement')
	announ_attach = fields.Binary('Announcement Attach File')
	announcement_ids = fields.One2many('purchase.requisition.announcement','scarp_request_id', string="NewsPaper")
	# book_ids = fields.One2many('tender.book', 'scrap_id')
	# book_count = fields.Integer(compute='_compute_book_count')
	collection_count = fields.Integer(compute='_compute_collection')
	finance_admin_attach = fields.Binary('Finance Administration Attach')
	finance_manager_attach = fields.Binary('Finance Manager Attach')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
	commitee_selection_id = fields.Many2one('committee.committee', 'Committee Selection')
	committee_member_ids = fields.One2many('committee.members','scrap_id',string="Committee Members")
	finance_attach = fields.Binary('Finance Attachment')
	control_attach = fields.Binary('Control Attachment')
	auction_date = fields.Date('Auction Date')
	tech_report_attach = fields.Binary('Technical Report Attachment', required=True) 



	@api.onchange('commitee_selection_id')
	def onchange_commitee_selection_id(self):
		vals = []
		for rec in self.commitee_selection_id.committee_member:
			vals.append((0,0,{
				'employee':rec.employee.id,
				'role':rec.role,
				}))
		self.committee_member_ids = vals


	@api.constrains('ordering_date')
	def _constrains_ordering_date(self):
		ordering_date = fields.Date.from_string(self.ordering_date)
		now = fields.Date.from_string(datetime.now())
		if self.ordering_date:
			if ordering_date < now:
				raise UserError(_("You cannot confirm Request '%s' because there is no valid date.") % self.ordering_date)
	

	@api.model
	def default_get(self, default_fields):
		res = super(ScrapRequest, self).default_get(default_fields)
		vals = []
		general_conditions_obj = self.env['general.conditions'].search([('type','=','scrap_request')])
		for line in general_conditions_obj.general_conditions_lines:
			vals.append((0, 0, {
					'name':line.name,             
				}))
		res['general_conditions_ids'] = vals
		return res


	@api.multi
	def action_cancel(self):
		self.write({'state':'cancel'})
	
	@api.multi
	def action_reset_draft(self):
		self.write({'state':'draft'})

	@api.multi
	def action_confirm(self):
		self.ensure_one()
		if not all(obj.asset_ids for obj in self):
			raise UserError(_("You cannot confirm Request '%s' because there is no Asset line.") % self.name)

		# self.name = self.env['ir.sequence'].next_by_code('scrap.requests') + ' / ' + self.name
		self.write({'state':'manager_director'})


	@api.model
	def create(self, vals):
		create_id = super(ScrapRequest, self).create(vals)

		context = self._context
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		employee = self.env['hr.employee'].search([('user_id.id','=',user.id)],limit=1)
		department = employee.department_id
		seq_code = 'scrap.requests.' + str(create_id.admin_id.name or False) + ' / '+ '.' +  str(create_id.dept_id.name or False) + ' / '+ '.'


		seq = self.env['ir.sequence'].next_by_code( seq_code )
		if not seq:
			self.env['ir.sequence'].create({
				'name' : seq_code,
				'code' : seq_code,
				'prefix' : 'PR / ' + str(create_id.admin_id.name or False) + ' / ' +  str(create_id.dept_id.name or False) + ' / ' ,
				'number_next' : 1,
				'number_increment' : 1,
				'use_date_range' : True,
				'padding' : 4,
				})
			seq = self.env['ir.sequence'].next_by_code( seq_code )
		create_id.name = seq 

		return create_id



	@api.multi
	def action_manager_dicrector(self):
		self.write({'state':'gen_man_appr'})


	@api.multi
	def action_gen_man_appr(self):
		self.write({'state':'director_finance_admin'})

	@api.multi
	def action_gen_man_appr2(self):
		self.write({'state':'announcement'})

	@api.multi
	def action_director_finance_admin(self):
		if not all(obj.committee_member_ids for obj in self):
			raise UserError(_("The committee members not exist!!"))
		self.write({'state':'comm_decided'})

	@api.multi
	def action_confirm_announcment(self):
		self.write({'state':'auction'})

	@api.multi
	def action_confirm_comm_decided(self):
		if not self.announ_number: 
			raise UserError(_("The Announcement is not exist please entered."))
		vals = []
		for rec in self:
			if rec.asset_line_ids:
				asset = self.env['scrap.request.line'].search('id','in',rec.asset_line_ids.ids)
				asset.unlink()
			for asset in rec.asset_ids:
				vals.append((0,0,
						{'asset_ids':[(6, 0, asset.asset_ids.ids)]}
						)) 
			rec.asset_line_ids = vals
		self.write({'state':'gen_man_appr2'})

	@api.multi
	def action_confirm_auction(self):
		self.write({'state':'auction'})
	
	@api.multi
	def action_auction(self):
		flag = False
		for line in self.asset_line_ids:
			coll = self.env['collection.collection'].search([('scrap_id','=',self.id)])
			if not line.partner_id and not line.estimated_value and not line.sales_value and not coll:
				flag = True
		if flag:
			raise UserError(_("Please sale at least one asset !!!"))

		self.write({'state':'finance_admin_apprv'})

	@api.multi
	def action_set_scrap(self):
		self.write({'state':'finance_manger_apprv'})


	@api.multi
	def get_collection(self):
		for rec in self:
			coll = self.env['collection.collection'].search([('scrap_id','=',self.id)])
			vals = []

			return{
				'name':'collection',
				'type':'ir.actions.act_window',
				'res_model':'collection.collection',
				'view_mode':'tree,form',
				'target':'current',
				'domain':[('id','in',coll.ids)],
				'context':{'create':False,}
				}


	@api.multi
	def _compute_collection(self):
		for line in self:
			line.collection_count = self.env['collection.collection'].search_count([('scrap_id','=',self.id)])
			



	@api.multi
	def action_finance_manger_apprv(self):
		self.write({'state':'done'})

class ScrapRequestLine(models.Model):
	_name = 'scrap.request.line'
	_description = 'Scrap Request Line'
	
	asset_ids = fields.Many2many('account.asset.asset','scrap_asset_ref', string='Assets')
	estimated_value = fields.Float('Estimated Value')
	sales_value = fields.Float('Selling Value')
	partner_id = fields.Many2one('res.partner','Purchaser')
	move_check = fields.Boolean()
	move_posted_check = fields.Boolean()
	scarp_request_id = fields.Many2one('scrap.request')

		


	@api.multi
	def create_move(self):
		for rec in self:
			rec.move_posted_check = True

			scrap_inventory = self.env['stock.scrap']
			scrap_account = self.env['account.asset.asset']

			for line in rec.asset_ids:
				# scrap_inventory.create({
				# 		'product_id':line.product_id.id,
				# 		'product_uom_id':line.product_id.uom_po_id.id
				# 		})
				scrap_account = scrap_account.search([('product_id','=',line.product_id.id)])
				scrap_account.write({'state':'sold'})
			vals = []
			company_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).company_id
			# asset = self.env['account.asset.asset'].search([('id','=')])
			vals.append((0,0,{
					'account_id':self.asset_ids[0].category_id.account_asset_id.id,
					'amount':self.sales_value,
					'branch_id':company_id.id
					}))
			return{
				'name':'collection',
				'type':'ir.actions.act_window',
				'res_model':'collection.collection',
				'view_mode':'form',
				'target':'current',
				'context':{
					'default_scrap_id':rec.scarp_request_id.id,
					'default_scrap_line_id':rec.id, 
					'default_partner_id':self.partner_id.id,
					'default_operation_type':'other_revenues',
					'default_branch_id':company_id.id,
					'default_line_ids':vals
					}
				}


class ProductProduct(models.Model):

	_inherit = 'product.template'

	is_car = fields.Boolean('Is Car')
	car_name = fields.Char('Car Name')
	car_number = fields.Char('Car Number')
	shasea_number = fields.Char('Shasea Number')
	palte_number = fields.Char('Plate Number')
	car_model = fields.Char('Car Model')
	machine = fields.Char('Machine')
	car_color = fields.Char('Color')
	fuel= fields.Selection([('jazz','jazz'),('boys','Boys')],'Fuel')
	origin = fields.Many2one('res.country','Origin')
	branch_id = fields.Many2one('res.company', 'Branch')


class Announcement(models.Model):

	_inherit = 'purchase.requisition.announcement'

	scarp_request_id = fields.Many2one('scrap.request')

class AssetRequest(models.Model):
	_name = 'asset.request'

	asset_ids = fields.Many2many('account.asset.asset',string='Asset')
	scrap_id = fields.Many2one('scrap.request')
	company_id = fields.Many2one('res.company', 'Branch')
	categ_id = fields.Many2one('account.asset.category', 'Category')

		
class CommitteeMembers(models.Model):
	_inherit = 'committee.members'

	scrap_id = fields.Many2one('scrap.request')
		