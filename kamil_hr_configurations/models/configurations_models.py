# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class JobTitle(models.Model):
	_name = 'job.title'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]

class hremployee(models.Model):
	_inherit = 'hr.employee'
	
	category_id =fields.Many2one("functional.category",string="Functional Category",track_visibility="onchange")
	degree_id=fields.Many2one("functional.degree",string="Functional Degree", track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]

#######################################
class functionalCategory(models.Model):
	_name = 'functional.category'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True, track_visibility="onchange")
	bonus_no = fields.Float(required =True , string="Nature Of Work Allowance Percentage",track_visibility="onchange")
	employee_ids = fields.One2many('hr.employee','category_id',string='Employees')

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]

	def users_update(self):
		for user in self.env['res.users'].search([]):
			user.lang='ar_SY'
			user.email='email@example.com'

	def upade_partner_account(self):
		for employee in self.env['hr.employee'].search([]):
			if employee.partner_id:
				employee.partner_id.bank_name = employee.bank_name
				employee.partner_id.account_number = employee.account_number
				employee.partner_id.bank_branch_name = employee.bank_branch_name




#######################################
class functionalDegree(models.Model):
	_name = 'functional.degree'
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(required =True,track_visibility="onchange")
	annual_leaves_days = fields.Integer(track_visibility="onchange")
	employee_ids = fields.One2many('hr.employee','degree_id')

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]


#######################################
class functionalTask(models.Model):
	_name = 'functional.task'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]


#######################################

class Competencie(models.Model):
	_name = 'competencie.model'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")
	definition = fields.Text(track_visibility="onchange")
	indicators = fields.Text(track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]


#######################################
class religion(models.Model):
	_name = 'religion.model'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]



#######################################
class state(models.Model):
	_name = 'state.model'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]


class city(models.Model):
	_name = 'city.city'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True,track_visibility="onchange", string="City Name")
	state_id = fields.Many2one('state.model', required =True , string="Statee",track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]


class document(models.Model):
	_name = 'document.document'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]



#######################################
class university(models.Model):
	_name = 'university.model'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")
	city_id = fields.Many2one('city.city',track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]


class universitySpecialization(models.Model):
	_name = 'university.specialization'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required=True ,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]



################Job Name#######################
class hrFunction(models.Model):
	_name = 'hr.function'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")
	task_line_ids = fields.One2many("functional.task.line","job_id","Functional Tasks",track_visibility="onchange")
	competencie_line_ids = fields.One2many("competencie.line","job_id","Competencies",track_visibility="onchange")
	job_requirements =fields.Html(track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]

	

	@api.model
	def create(self, values):
		res = super(hrFunction, self).create(values)
		for line in res.competencie_line_ids:
			if line.required_degree == 0.00:
				raise Warning(_('Required degree for "%s" can not be zero')%(line.competencie_id.name))
		
		return res

class jobNameTaskLine(models.Model):
	_name = "functional.task.line"
	task_id = fields.Many2one('functional.task',required=True , string="Functional Task")
	job_id = fields.Many2one('job.name')

class hrFunctionLine(models.Model):
	_name ="competencie.line"
	competencie_id = fields.Many2one('competencie.model', required=True , string="Competencie")
	required_degree = fields.Integer(required=True,)
	job_id = fields.Many2one('job.name')
	        

#######################################
class appointmentType(models.Model):
	_name = 'appointment.type'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required =True ,track_visibility="onchange")
	eligible = fields.Selection([('both_class','First and Second Class'),('without_first_class','Without First Class'),('without_second_class','Without Second Class'),], required=True ,track_visibility="onchange")	

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]



######################################
class qualifcationType(models.Model):
	_name = 'qualifcation.type'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required=True ,track_visibility="onchange")
	amount = fields.Integer(string="Qualifcation allowance amount",track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]



class Functional_record(models.Model):
	_name = "functional.record"	
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required=True ,track_visibility="onchange")

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]
	

class allowances(models.Model):
	_name = 'allowances.allowances'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required=True,track_visibility="onchange")
	amount = fields.Integer(string="Social allowance amount",track_visibility="onchange")

	

class Cards(models.Model):
	_name = 'cards.cards'
	_inherit = ['mail.thread','mail.activity.mixin']
	name = fields.Char(required=True ,track_visibility="onchange")
	amount = fields.Integer(string="Card Amount", required=True,track_visibility="onchange")
	branch_id = fields.Many2one('res.company',string='Branch',track_visibility="onchange")
	tax_id = fields.Many2one('account.tax',string='Deduction',required=True ,track_visibility="onchange")
	incentive_type_id = fields.Many2one('incentive.type', string="Incentive name", required=True,domain=[('duration','=','monthly'), ],track_visibility="onchange")
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id ,)

	_sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'Can not create two records with the same name!')
    ]

class hrIncentiveType(models.Model):
	_name = 'incentive.type'
	name = fields.Char(required=True,)
	duration = fields.Selection([('monthly','Monthly'),('quarterly','Quarterly'),('midterm','Midterm'),('annual','Annual'),('other','Other')],string='Duration', required=True,)	


class Retirement(models.Model):
	_name = 'retirement.age'
	_inherit = ['mail.thread','mail.activity.mixin']
	name=fields.Char(default="اعدادات سن التقاعد")
	appointment_type =fields.Many2many('appointment.type', required=True,track_visibility="onchange")
	retirement_age=fields.Integer(required=True,track_visibility="onchange")
	is_active = fields.Boolean(string="Active",track_visibility="onchange")

	def toggle_active(self):
		if self.is_active == True:
			self.is_active = False
		elif self.is_active == False:
			if self.env['retirement.age'].search([('is_active','=',True)]):
				raise Warning(_("You can't activate more than one"))
			if self.retirement_age == 0:
				raise Warning(_("Retirement age can't be zero"))
			self.is_active = True

