from odoo import models, fields, api
from datetime import date,datetime
from dateutil.relativedelta import relativedelta	
from odoo.exceptions import Warning

class hrEmployee(models.Model):
	_inherit = "hr.employee"

	name_eng=fields.Char(string="Name in English",track_visibility="onchange" )
	number=fields.Integer(string="Employee Number", readonly=True, track_visibility="onchange")
	unit_id= fields.Many2one('hr.department',track_visibility="onchange")
	department_id= fields.Many2one('hr.department',track_visibility="onchange")
	appoiontment_type=fields.Many2one('appointment.type',track_visibility="onchange")
	appoiontment_degree=fields.Many2one('functional.degree',string="Degree upon appoiontment",track_visibility="onchange")
	appointment_qualification=fields.Many2one('qualifcation.type',string="Qualification",track_visibility="onchange")
	university=fields.Many2one("university.model",track_visibility="onchange")
	specialization=fields.Many2one("university.specialization",track_visibility="onchange")
	retirement_date=fields.Date(compute='_get_retirement_date' ,track_visibility="onchange")
	graduation_date=fields.Date(track_visibility="onchange")
	appoiontment_date=fields.Date(track_visibility="onchange")
	entry_date = fields.Date(track_visibility="onchange")
	last_promotion_date = fields.Date(track_visibility="onchange")
	termination_date=fields.Date(track_visibility="onchange")
	index_number=fields.Char(track_visibility="onchange")
	training_number = fields.Char(track_visibility="onchange")
	state=fields.Many2one("state.model", string="Statee",track_visibility="onchange")
	partner_id=fields.Many2one("res.partner",readonly=True,track_visibility="onchange")
	city=fields.Many2one('city.city',string="City",track_visibility="onchange")
	area=fields.Char(string="Area",track_visibility="onchange")
	nearest_landmark=fields.Char(string="Nearest landmark",track_visibility="onchange")
	is_union=fields.Boolean("union" ,track_visibility="onchange")
	fellowship=fields.Boolean(track_visibility="onchange")
	birth_certifiiate = fields.Selection([('birth_certifiiate','Birth Certifiiate'),('teething','Teething')],string="Type of birth certifiiate",default='birth_certifiiate' ,track_visibility="onchange")
	birth_certifiiate_date = fields.Date(string="Birth Certifiiate Date" ,track_visibility="onchange")
	gender = fields.Selection([('male', 'Male'),('female', 'Female')],required="True" , track_visibility="onchange")
	religion =fields.Many2one('religion.model',string="Religion",track_visibility="onchange")
	mother_name =fields.Char(string="Mother Name",track_visibility="onchange")
	bank_name=fields.Char('Bank Name',track_visibility="onchange")
	bank_branch_name = fields.Char(track_visibility="onchange")
	driving_license = fields.Char(track_visibility="onchange")
	license_type = fields.Selection([('speciall_license','Specliall'),('general_license','General')],track_visibility="onchange")
	home_address = fields.Char(track_visibility="onchange")
	marital=fields.Selection([('single','SINHLE'),('married','Married'),('have_kids','Married  and have kids'),('widowre','Widowre'),('divorced','Divorced')],track_visibility="onchange")
	job_title_id=fields.Many2one("job.title",track_visibility="onchange")
	functional_id=fields.Many2one("hr.function",required=True,track_visibility="onchange")
	bonus = fields.Selection([
		('first_bonus','First Bonus'),
		('second_bonus','Second Bonus'),
		('third_bonus','Third Bonus'),
		('fourth_bonus','Fourth Bonus'),
		('fifth_bonus','Fifth Bonus'),
		('sixth_bonus','Sixth Bonus'),
		('seventh_bonus','Seventh Bonus'),
		('eighth_bonus','Eighth Bonus'),
		('ninth_bonus','Ninth Bonus')
		], track_visibility="onchange")
	last_bonus_date=fields.Date(track_visibility="onchange")
	education_lines=fields.One2many("employee.education","employee_id",track_visibility="onchange")
	allowances_lines=fields.One2many("social.allowances","employee_id",track_visibility="onchange")
	fingerprint_number=fields.Char(string="Fingerprint number",track_visibility="onchange")
	user_id = fields.Many2one(string='user',readonly=True,track_visibility="onchange")

	nclination_deserved=fields.Boolean(track_visibility="onchange")
	driving_attch=fields.Binary(string="Driving License",track_visibility="onchange")
	search_certificate=fields.Binary(string="Search certificate",track_visibility="onchange")
	date_from=fields.Date(string="Due Date from",track_visibility="onchange")
	date_to=fields.Date(string="Date to",track_visibility="onchange")
	tax_exempt = fields.Boolean(track_visibility="onchange")
	reason = fields.Text(track_visibility="onchange")
	document = fields.Binary(track_visibility="onchange")
	medical_state=fields.Selection([('intact','Intace'),('speccial_needs','Speccial Needs')], default='intact',track_visibility="onchange")
	speccial_needs_type=fields.Char(track_visibility="onchange")
	blood_type=fields.Selection([('a+','A+'),('a','A-'),('b','B+'),('b','B-'),('ab+','AB+'),('ab-','AB-'),('o+','O+'),('o-','O-'),],track_visibility="onchange")
	medical_line_ids = fields.One2many('medical.state.line', 'employee_id',track_visibility="onchange")
	cards_line_ids = fields.One2many("employee.card","employee_id",track_visibility="onchange")
	total_cards_amount = fields.Float(compute='_compute_total_cards_amount',track_visibility="onchange")
	phone_numbre= fields.Char(track_visibility="onchange")
	relative_name =fields.Char(string="name",track_visibility="onchange")
	relative_relation =fields.Char(track_visibility="onchange")
	line_ids = fields.One2many("initiatives.tributes","initiatives_line_id",track_visibility="onchange")

	###########################
	work_phone = fields.Char('Work Phone',track_visibility="onchange")
	mobile_phone = fields.Char('Work Mobile',track_visibility="onchange")
	work_email = fields.Char('Work Email',track_visibility="onchange")
	work_location = fields.Char('Work Locationt',track_visibility="onchange")
	country_id = fields.Many2one('res.country', 'Nationality (Country)', groups="hr.group_hr_user",track_visibility="onchange")
	identification_id = fields.Char(string='Identification No', groups="hr.group_hr_user",track_visibility="onchange")
	passport_id = fields.Char('Passport No', groups="hr.group_hr_user",track_visibility="onchange")
	account_number= fields.Char('Bank Account Number',help='Employee bank salary account',track_visibility="onchange")
	current_leave_state = fields.Selection(string="Current Leave Status",
        selection=[
            ('draft', 'Draft'),
	        ('acting','The approval of a designee'),
	        ('dep_manger','Department Manger Confirm'),
	        ('confirm', 'Unit Manger Confirm'),
	        ('hr_manger','HR Manger'),
	        ('refuse', 'Refused'),
	        ('validate1', 'Second Approval'),
	        ('validate', 'Approved'),
	        ('end','End'),
	        ('cancel', 'Cancelled'),
        ])
	childs_number = fields.Integer(track_visibility="onchange")

	def unlink(self):
		for rec in self:
			rec.contract_id.unlink()
		return models.Model.unlink(self)


	@api.model
	def create(self,vals):
		vals['number'] = self.env['ir.sequence'].next_by_code('sequence.employee.number')
		res = super(hrEmployee,self).create(vals)
		if res.mobile_phone:
			login = res.mobile_phone
		else:
			login = res.number
		lang = self.env.user.lang
		if self.env['res.lang'].search([('code','=','ar_SY')]):
			lang = 'ar_SY'
		user = self.env['res.users'].create({'name':res.name,'login':login,'password':123,'company_id':res.company_id.id,'company_ids':[(6, 0, [res.company_id.id])],'lang':lang,'sel_groups_14_15':14,'email':'email@example.com'})
		res.user_id = user.id
		partner = self.env['res.partner'].search([('name','=',res.name)],limit=1)
		res.partner_id = partner.id
		res.partner_id.is_employee = True
		res.partner_id.bank_name = res.bank_name
		res.partner_id.account_number = res.account_number
		res.partner_id.bank_branch_name = res.bank_branch_name
		return res

	@api.onchange('birthday')
	def _date(self):
		if self.birthday:
			if self.birthday > date.today():
				raise Warning(_("Sorry! The birthday cannot be greater than Today"))

	@api.onchange('name')
	def _onchange_name(self):
		if self.name:
			self.user_id.write({'name': self.name})
			self.user_id.write({'login': self.name})
	    

	@api.onchange('bank_name','account_number','bank_branch_name')
	def _onchange_account(self):
		for rec in self:
			if rec.partner_id:
				rec.partner_id.write({'bank_name':rec.bank_name})
				rec.partner_id.write({'account_number':rec.account_number})
				rec.partner_id.write({'bank_branch_name':rec.bank_branch_name})

	        

	@api.onchange('company_id')
	def get_unit_company(self):
		branchs = self.env['hr.department'].search([])
		if self.company_id:
			for branch in branchs:
				return{
					'domain':{
						'unit_id':[('company_id','child_of',self.company_id.id)]
					}
				}
    
	@api.onchange('unit_id')
	def get_unit_department(self):
		branchs = self.env['hr.department'].search([])
		if self.unit_id:
			for branch in branchs:
				return{
				       'domain':{
				       		'department_id':[('id','child_of',self.unit_id.id)]
				       }
				}
	

	
	@api.onchange('state')
	def _onchange_state(self):
		if self.state:
			return {'domain':{'city':[('state_id','=',self.state.id)]}}
	        

	def check_next_promotions(self):
		for employee in self.env['hr.employee'].search([]):
			if employee.last_promotion_date and employee.category_id and employee.degree_id and employee.category_id:
				timeline = self.env['promotions.timeline'].search([('state','=','validated')], limit=1)
				for line in timeline.line_ids:
					for category in line.category_id:
						if category == employee.category_id and line.from_degree_id == employee.degree_id:
							if str((datetime.strptime(str(employee.last_promotion_date), "%Y-%m-%d") + relativedelta(months=(line.years * 12 ))).date()) == str((datetime.strptime(str(date.today()), "%Y-%m-%d") + relativedelta(months=1)).date()):
								for user in self.env['res.users'].search([]):
									if user.has_group('hr.group_hr_user'):
										self.env['mail.activity'].create({
											'res_name': 'Employee promotion',
								            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
								            'date_deadline':date.today(),
								            'summary': 'Employee "' + employee.name + '" promotion will be after one month',
								            'user_id': user.id,
								            'res_id': employee.id,
								            'res_model_id': self.env.ref('hr.model_hr_employee').id,
								        })

	@api.onchange('appoiontment_type','birthday')
	def _get_retirement_date(self):
		for rec in self:
			if rec.appoiontment_type and rec.birthday:
				retirement = self.env['retirement.age'].search([('is_active','=',True)])
				for appointment in retirement.appointment_type:				
					if appointment == rec.appoiontment_type:
						rec.retirement_date = (datetime.strptime(str(rec.birthday), "%Y-%m-%d") + relativedelta(years=(retirement.retirement_age ))).date()
						


	@api.onchange('cards_line_ids')
	def _compute_total_cards_amount(self):
		for rec in self:
			total = 0.00
			for line in rec.cards_line_ids:
				total += line.total
			rec.total_cards_amount = total
	        

	def check_termination_date(self):
		for employee in self.env['hr.employee'].search([]):
			if employee.termination_date:
				day_after = (datetime.strptime(str(date.today()), "%Y-%m-%d") + relativedelta(days=40)).date()
				if employee.termination_date == day_after:
					for user in self.env['res.users'].search([]):
						if user.has_group('hr.group_hr_user'):
							self.env['mail.activity'].create({
								'res_name': 'Employee termination date',
					            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
					            'date_deadline':date.today(),
					            'summary': 'Employee "' + employee.name + '" termination date will be after 40 days',
					            'user_id': user.id,
					            'res_id': employee.id,
					            'res_model_id': self.env.ref('hr.model_hr_employee').id,
					        })
				if employee.termination_date <= date.today():
					employee.toggle_active()

	def check_next_bonus_date(self):
		for employee in self.env['hr.employee'].search([]):
			if employee.termination_date:
				day_after = (datetime.strptime(str(date.today()), "%Y-%m-%d") + relativedelta(days=10)).date()
				if employee.last_bonus_date == day_after:
					for user in self.env['res.users'].search([]):
						if user.has_group('hr.group_hr_user'):
							self.env['mail.activity'].create({
								'res_name': 'Employee next bonus date',
					            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
					            'date_deadline':date.today(),
					            'summary': 'Employee "' + employee.name + '" next bonus date will be after 10 days',
					            'user_id': user.id,
					            'res_id': employee.id,
					            'res_model_id': self.env.ref('hr.model_hr_employee').id,
					        })
	



class employee_education(models.Model):
	_name="employee.education"	
	_inherit = ['mail.thread','mail.activity.mixin',]

	qualifcat_type=fields.Many2one('qualifcation.type',track_visibility="onchange")
	date=fields.Date("Date",track_visibility="onchange")
	university=fields.Many2one("university.model",track_visibility="onchange")
	specialization=fields.Many2one("university.specialization", track_visibility="onchange")
	document=fields.Binary(track_visibility="onchange")
	qualifying_allowance=fields.Boolean(track_visibility="onchange")
	amount=fields.Integer(readonly=True,track_visibility="onchange")
	employee_id=fields.Many2one("hr.employee",track_visibility="onchange")

	@api.onchange('qualifying_allowance')
	def _get_allowance_amount(self):
		if self.qualifying_allowance == True:
			self.amount = self.qualifcat_type.amount




class social_allowances(models.Model):
	_name="social.allowances"
	_inherit = ['mail.thread','mail.activity.mixin',]
	allowance_type=fields.Many2one('allowances.allowances',track_visibility="onchange")
	date=fields.Date(required=True,track_visibility="onchange")
	relatives=fields.Char(string="Name of wife/child", required=True,track_visibility="onchange")
	document=fields.Binary(required=True,track_visibility="onchange")
	amount=fields.Integer(readonly=True,track_visibility="onchange")
	employee_id=fields.Many2one("hr.employee",track_visibility="onchange")
	social_allowance =fields.Boolean(track_visibility="onchange")

	@api.onchange('social_allowance')
	def _get_allowance_amount(self):
		if self.social_allowance == True:
			self.amount = self.allowance_type.amount


class medicalStateLine(models.Model):
	_name = 'medical.state.line'
	_inherit = ['mail.thread','mail.activity.mixin',]
	disease_name = fields.Many2one("disease.disease",required=True,track_visibility="onchange")
	medical_report = fields.Binary(required=True,track_visibility="onchange")
	employee_id=fields.Many2one("hr.employee",track_visibility="onchange")

class employeeCard(models.Model):
	_name = 'employee.card'
	_inherit = ['mail.thread','mail.activity.mixin',]
	card_id = fields.Many2one('cards.cards', required=True, string="Sponsorship",track_visibility="onchange")
	amount = fields.Integer('cards.cards',readonly=True,related='card_id.amount',track_visibility="onchange")
	branch_id = fields.Many2one('res.company',string='Branch',readonly=True,related='card_id.branch_id',track_visibility="onchange")
	count = fields.Integer(required=True,default=1,track_visibility="onchange")
	total = fields.Integer(compute='_onchange_count',track_visibility="onchange")
	employee_id = fields.Many2one('hr.employee',track_visibility="onchange")



	@api.onchange('count','card_id')
	def _onchange_count(self):
		for rec in self:
			rec.total = rec.amount * rec.count



class InitiativesTributes(models.Model):
	_name='initiatives.tributes'
	_inherit = ['mail.thread','mail.activity.mixin',]
	description=fields.Char(track_visibility="onchange")
	beneficiary=fields.Char(track_visibility="onchange")
	document=fields.Binary(track_visibility="onchange")
	notes=fields.Char(track_visibility="onchange")
	initiatives_line_id = fields.Many2one("hr.hr.employee",track_visibility="onchange")

class Disease_Disease(models.Model):
	_name='disease.disease'
	name=fields.Char()




