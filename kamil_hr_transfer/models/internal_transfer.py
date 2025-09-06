
from odoo import models, fields, api, _
from datetime import date

class internalTransfer(models.Model):
	_name = 'internal.transfer'
	_inherit = ['mail.thread','mail.activity.mixin',]
	_rec_name = "employee_id"

	
	employee_no = fields.Integer(string="Employee Number")

	employee_id = fields.Many2one('hr.employee' , required=True,)
	unit_id = fields.Many2one('hr.department')
	department_id = fields.Many2one('hr.department')
	degree_id = fields.Many2one('functional.degree' )
	date = fields.Date(default=lambda self: fields.Date.today())

	current_unit_id = fields.Many2one('hr.department')
	new_unit_id = fields.Many2one('hr.department',domain=[('type','=','general_administration'), ],track_visibility="onchange")
	current_branch_id = fields.Many2one("res.company")
	new_branch_id = fields.Many2one("res.company",track_visibility="onchange")
	current_location = fields.Many2one('hr.department' )
	new_location = fields.Many2one('hr.department',domain=[('type','=','department'), ],track_visibility="onchange")
	current_job = fields.Many2one('hr.function' )
	new_job = fields.Many2one('hr.function',track_visibility="onchange")

	transfer_reason = fields.Text( string="Transfer Reason",track_visibility="onchange")
	note = fields.Html()
	state = fields.Selection([('draft','Draft'),('current_dept_managar','Current Managar'),('new_dept_managar','New Managar'),('hr_managar','HR managar'),('reject','Rejected')],default='draft',track_visibility="onchange")


	def do_current_managar(self):
		self.write({'state':'current_dept_managar'})
	def do_managar_reject(self):
		self.state = 'reject'
	def do_managar_reject1(self):
		self.state = 'reject'
	def do_managar_reject2(self):
		self.state = 'reject'
	

	def current_managar_return(self):
		self.state = 'draft'
	def do_new_managar(self):
		# change state to current new managar
		self.state = 'new_dept_managar'

	def do_hr_managar(self):
		# change state to hr managar
		self.employee_id.unit_id = self.new_unit_id
		self.employee_id.department_id = self.new_location
		self.employee_id.functional_id = self.new_job
		self.employee_id.company_id = self.new_branch_id
		self.employee_id.user_id.company_ids = [(6, 0, [self.new_branch_id.id])]
		self.employee_id.user_id.company_id = self.new_branch_id
		self.state = 'hr_managar'

	def do_managar_return(self):
		if self.state == 'current_dept_managar':
			self.state = 'draft'
		if self.state == 'new_dept_managar':
			self.state = 'current_dept_managar'
		if self.state == 'hr_managar':
			self.state = 'new_dept_managar'

	def do_managar_return1(self):
		if self.state == 'current_dept_managar':
			self.state = 'draft'
		if self.state == 'new_dept_managar':
			self.state = 'current_dept_managar'
		if self.state == 'hr_managar':
			self.state = 'new_dept_managar'

	def do_managar_return2(self):
		if self.state == 'current_dept_managar':
			self.state = 'draft'
		if self.state == 'new_dept_managar':
			self.state = 'current_dept_managar'
		if self.state == 'hr_managar':
			self.state = 'new_dept_managar'

	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id
			self._onchange_employee_id()

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = False
			self.employee_no = self.employee_id.number
			self.unit_id = self.employee_id.unit_id
			self.department_id = self.employee_id.department_id
			self.current_unit_id = self.employee_id.unit_id
			self.current_location = self.employee_id.department_id
			self.current_branch_id = self.employee_id.company_id
			self.current_job = self.employee_id.functional_id
			self.degree_id = self.employee_id.degree_id


	@api.onchange('new_branch_id')
	def get_branch_units(self):
		self.new_unit_id = False
		if self.new_branch_id:
			return{
				'domain':{
					'new_unit_id':[('company_id','=',self.new_branch_id.id)]
				}
			}

	@api.onchange('new_unit_id')
	def get_unit_departments(self):
		self.new_location = False
		if self.new_unit_id:
			return{
			       'domain':{
			       		'new_location':[('parent_id','=',self.new_unit_id.id)]
			       }
			}
				
