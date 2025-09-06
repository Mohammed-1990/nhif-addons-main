from openerp import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import Warning

class hrLoanPayslip(models.Model):
	_name = 'hr.payslip'
	_inherit = ['hr.payslip','mail.thread','mail.activity.mixin']

	contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True,
        states={'draft': [('readonly', True)]})
	struct_id = fields.Many2one('hr.payroll.structure', string='Structure',
        readonly=True, states={'draft': [('readonly', True)]},)
	number = fields.Char(string='Signal serial number', readonly=True, copy=False,
        states={'draft': [('readonly', False)]})
	branch_id = fields.Many2one("res.company",string="Branch")
	is_temporary = fields.Boolean()
	years_experience = fields.Integer()
	old_salary_id = fields.Many2one("salary.structure")
	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('done','Accounting')], string="Status" ,default='draft', track_visibility="onchange")

 
	@api.model
	def create(self, values):
		values['company_id'] = self.env['hr.employee'].search([('id','=',values['employee_id'])]).company_id.id
		values['branch_id'] = self.env['hr.employee'].search([('id','=',values['employee_id'])]).company_id.id
		res = super(hrLoanPayslip, self).create(values)
		if not res.employee_id.contract_id:
			raise Warning(('يرجي التأكد من ان الموظف "%s" لديه عقد')%(res.employee_id.name))
		if not res.employee_id.contract_id.struct_id:
			raise Warning(('يرجي إعداد هيكل راتبي لعقد الموظف "%s"')%(res.employee_id.name))
		res.contract_id = res.employee_id.contract_id.id
		res.struct_id = res.employee_id.contract_id.struct_id.id
		res.company_id = res.employee_id.company_id.id
		res.branch_id = res.employee_id.company_id.id
		return res

	@api.multi
	def action_payslip_confirm(self):
		for rec in self:
			rec.write({'state': 'verify'})
	
	@api.multi
	def compute_total_loan_amount(self):
		for rec in self:
			total = 0.00
			for line in rec.loan_ids:
				total += line.amount
			rec.total_loan_amount = total
	
	loan_ids = fields.One2many('hr.payslip.loan.line', 'payroll_id', string="Loans")
	total_loan_amount = fields.Float(string="Total Loans", compute= 'compute_total_loan_amount')
	
	def do_submit(self):
		# self.state = 'benefits_wages'
		self.write({'state':'benefits_wages'})

	def do_confirm(self):
		# self.state = 'personnel'
		self.write({'state':'personnel'})

	def do_personnel_confirm(self):
		# self.state = 'general_directorate'
		self.write({'state':'general_directorate'})

	def do_gd_confirm(self):
		# general directorate confirm
		# self.state = 'internal_auditor'
		self.write({'state':'internal_auditor'})

	
	def do_return(self):
		if self.state == 'benefits_wages':
			# self.state = 'draft'
			self.write({'state':'draft'})
		if self.state == 'personnel':
			# self.state = 'benefits_wages'
			self.write({'state':'benefits_wages'})
		if self.state == 'general_directorate':
			# self.state = 'personnel'
			self.write({'state':'personnel'})
		if self.state == 'internal_auditor':
			# self.state = 'general_directorate'
			self.write({'state':'general_directorate'})
	
	@api.multi
	def compute_sheet(self):
		for rec in self:
			#Old Salary
			rec.old_salary_id = rec.env['salary.structure'].search([('is_old_structure','=',True)],limit=1).id
			super(hrLoanPayslip, rec).compute_sheet()
			#======================
			if rec.employee_id.entry_date:
				entry_date = datetime.strptime(str(rec.employee_id.entry_date), '%Y-%m-%d')
				today = datetime.strptime(str(date.today()), '%Y-%m-%d')
				rec.years_experience = (today - entry_date).days / 364
			#============loans
			loan_lines = []
			hr_loan = rec.env['hr.loan'].sudo().search([('employee_id','=',rec.employee_id.id), ('state','=','start_payments'),('deduction','=','salary'),])

			for loan in hr_loan:
				if not rec.is_temporary and loan.company_id.is_main_company == True:
					for line in loan.line_ids:
						if line.paid == False and line.paid_date and line.paid_date >= rec.date_from and line.paid_date <= rec.date_to:
								loan_lines.append({'loan_id':loan.id,
		                            'date':line.paid_date,
		                            'amount':line.paid_amount,
		                            'line_id':line,
		                            })
				if rec.is_temporary:
					for line in loan.line_ids:
						if line.paid == False and line.paid_date and line.paid_date >= rec.date_from and line.paid_date <= rec.date_to:
								loan_lines.append({'loan_id':loan.id,
		                            'date':line.paid_date,
		                            'amount':line.paid_amount,
		                            'line_id':line,
		                            })
			rec.loan_ids = False
			rec.loan_ids = loan_lines
			rec.compute_total_loan_amount()

			leaves = rec.env['hr.leave'].search(['&',('employee_id','=',rec.employee_id.id),'|','|','&',('request_date_from','<',rec.date_from),('request_date_to','>',rec.date_to),'&',('request_date_from','>=',rec.date_from),('request_date_from','<=',rec.date_to),'&',('request_date_to','>=',rec.date_from),('request_date_to','<=',rec.date_to)])
				
			days_leave = 0
			in_unpaid_leave = False
			for leave in leaves:
				if leave.state == 'validate':
					if leave.request_date_from >= rec.date_from and leave.request_date_to <= rec.date_to:
						days_leave += leave.number_of_days_display
					elif leave.request_date_from < rec.date_from:
						different_days = (fields.Date.from_string(rec.date_from)-fields.Date.from_string(leave.request_date_from)).days
						days_leave += leave.number_of_days_display - different_days
					elif leave.request_date_to > rec.date_to:
						different_days = (fields.Date.from_string(leave.request_date_to)-fields.Date.from_string(rec.date_to)).days
						days_leave += leave.number_of_days_display - different_days
					worked_days = self.env['hr.payslip.worked_days'].search([('payslip_id','=',rec.id),('code','=',leave.holiday_status_id.name)])
					if days_leave >= 28:
						days_leave = 30
					if worked_days:
						worked_days.unlink()

					worked_days.create({
						'name':leave.holiday_status_id.name,
						'code':leave.holiday_status_id.name,
						'number_of_days':days_leave,
						'contract_id':rec.employee_id.contract_id.id,
						'payslip_id':rec.id
						})
					if leave.state == 'validate' and leave.holiday_status_id.unpaid == True:
						in_unpaid_leave = True
						super(hrLoanPayslip, rec).compute_sheet()
						if days_leave == 30:
							for line in rec.line_ids:
								line.write({'amount':0.00})
								line.write({'total':0.00})
						else:
							for line in rec.line_ids:
								amount = line.amount
								total = line.total
								line.write({'amount':amount - ((amount/30)*days_leave)})
								line.write({'total':total - ((total/30)*days_leave)})
			if not in_unpaid_leave:
				super(hrLoanPayslip, rec).compute_sheet()	
				


class hrLoanLinePayslip(models.Model):
	_name = 'hr.payslip.loan.line'

	payroll_id = fields.Many2one('hr.payslip')

	loan_id = fields.Many2one('hr.loan','Loan')
	date = fields.Date()
	amount = fields.Float()
	line_id = fields.Many2one('hr.loan.line')


	
class hrPayslipRun(models.Model):
	_name = 'hr.payslip.run'
	_inherit = ['hr.payslip.run','mail.thread','mail.activity.mixin']
	_order = "id desc"

	def appoiontment_type_domain(self):
		appoiontment_type_ids = []
		if self._context.get('default_is_temporary') == True:
			for appo_type in self.env['appointment.type'].search([('eligible','!=','both_class')]):
				appoiontment_type_ids.append(appo_type.id)
		else:
			for appo_type in self.env['appointment.type'].search([('eligible','=','both_class')]):
				appoiontment_type_ids.append(appo_type.id)
		return [('id','in',appoiontment_type_ids)]


	state = fields.Selection([
		('draft','Draft'),
		('benefits_wages','Benefits and wages'),
		('personnel','Personnel'),
		('general_directorate','General Directorate of Human Resources'),
		('internal_auditor','Internal Auditor'),
		('done','Accounting')], string="Status" ,default='draft', track_visibility="onchange")
	slip_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips',
		states={'draft': [('readonly', True)]}, copy=True)
	notes = fields.Html()
	branch_id = fields.Many2one("res.company",string="Branch", required=True,)
	appoiontment_type=fields.Many2many('appointment.type',track_visibility="onchange", required=True, domain=appoiontment_type_domain)
	is_temporary = fields.Boolean()

	def unlink(self):
		for rec in self:
			for line in rec.slip_ids:
				line.unlink()
		return models.Model.unlink(self)
	
	def do_compute_sheet(self):
		for rec in self:
			for slip in rec.slip_ids:
				slip.compute_sheet()


	def do_details(self):
		for rec in self:
			for line in rec.slip_ids:
				line.unlink()
			if rec.branch_id:
				line_list = []
				appoiontment_type_list = []
				for appointment in rec.appoiontment_type:
					appoiontment_type_list.append(appointment.id)
				payslips = rec.env['hr.payslip']
				for employee in rec.env['hr.employee'].search([('company_id','=',rec.branch_id.id),('appoiontment_type','in',appoiontment_type_list)]):
					slip_data = rec.env['hr.payslip'].onchange_employee_id(rec.date_start, rec.date_end, employee.id, contract_id=False)
					res = {
		                'employee_id': employee.id,
		                'name': slip_data['value'].get('name'),
		                'struct_id': slip_data['value'].get('struct_id'),
		                'contract_id': slip_data['value'].get('contract_id'),
		                'payslip_run_id': rec.id,
		                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
		                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
		                'date_from': rec.date_start,
		                'date_to': rec.date_end,
		                'company_id': employee.company_id.id,
		            }
					if res != {}:
						payslips += self.env['hr.payslip'].create(res)
				payslips.compute_sheet()

	def do_compute_details(self):
		for rec in self:
			if not rec.slip_ids:
				raise Warning(_('Please Enter payslips details'))
			for line in rec.slip_ids:
				line.compute_sheet()
				line.write({'state': 'benefits_wages'})
		self.write({'state':'benefits_wages'})

	def do_submit(self):
		for rec in self:
			for line in rec.slip_ids:
				line.write({'state': 'benefits_wages'})
		self.write({'state':'benefits_wages'})

	def do_confirm(self):
		for rec in self:
			for line in rec.slip_ids:
				line.write({'state': 'personnel'})
		self.write({'state':'personnel'})

	def do_personnel_confirm(self):
		for rec in self:
			for line in rec.slip_ids:
				line.write({'state': 'general_directorate'})
		self.write({'state':'general_directorate'})

	def do_gd_confirm(self):
		for rec in self:
			for line in rec.slip_ids:
				line.write({'state': 'internal_auditor'})
		self.write({'state':'internal_auditor'})

	
	def do_return(self):
		state = 'draft'
		if self.state == 'benefits_wages':
			self.write({'state':'draft'})
			state = 'draft'
		if self.state == 'personnel':
			self.write({'state':'benefits_wages'})
			state = 'benefits_wages'
		if self.state == 'general_directorate':
			self.write({'state':'personnel'})
			state = 'personnel'
		if self.state == 'internal_auditor':
			self.write({'state':'general_directorate'})
			state = 'general_directorate'
		for rec in self:
			for line in rec.slip_ids:
				line.write({'state': state})


	@api.multi
	def action_accounting(self):
		for rec in self:
			#Delete the old rati list
			for rati in self.env['ratification.list'].search([('payslip_id','=',self.id)]):
				rati.write({'state':'canceled'})
				rati.sudo().unlink()
			ratification_line = []
			other_deduction_line = []
			company_id = self.env.user.company_id.id
			if self.env['res.company'].search([('is_main_company','=',True)]):
				company_id = self.env['res.company'].search([('is_main_company','=',True)])[0].id
			if not rec.is_temporary:
				ratification = self.env['ratification.list'].create({'name':'مُسير ('+rec.name+')',
				'date':date.today(),
				'from_hr':True,
				'payslip_id':self.id,
				'company_id' : company_id 
				})

				for slip in rec.slip_ids:
					for line in slip.line_ids:					
						if line.total > 0 and line.salary_rule_id.account_id:
							ratification_line.append({
								'name':line.name,
								'partner_id':slip.employee_id.partner_id.id,
								'branch_id':slip.employee_id.company_id.id,
								'amount':line.total,
								'account_id':line.salary_rule_id.account_id.id,
								'analytic_account_id':line.salary_rule_id.account_id.parent_budget_item_id.id,
								'ratification_list_id':ratification.id,
								'company_id' : company_id,
								})
						elif line.total < 0 and line.salary_rule_id.tax_id:
							other_deduction_line.append({'name':line.name,
								'partner_id':slip.employee_id.partner_id.id,
								'tax_id':line.salary_rule_id.tax_id.id,
								'amount':abs(line.total),
								})
					slip.write({'state': 'done'})
				ratification.ratification_line_ids = ratification_line 
				ratification.other_deduction_ids = other_deduction_line
			elif rec.is_temporary:
				ratification = self.env['ratification.list'].create({'name':'مُسير ('+rec.name+')',
				'date':date.today(),
				'from_hr':True,
				'payslip_id':self.id,
				'company_id' : self.branch_id.id
				})

				for slip in rec.slip_ids:
					for line in slip.line_ids:					
						if line.total > 0 and line.salary_rule_id.account_id:
							ratification_line.append({
								'name':line.name,
								'partner_id':slip.employee_id.partner_id.id,
								'branch_id':slip.employee_id.company_id.id,
								'amount':line.total,
								'account_id':line.salary_rule_id.account_id.id,
								'analytic_account_id':line.salary_rule_id.account_id.parent_budget_item_id.id,
								'ratification_list_id':ratification.id,
								'company_id' : slip.employee_id.company_id.id,
								})
						elif line.total < 0 and line.salary_rule_id.tax_id:
							other_deduction_line.append({'name':line.name,
								'partner_id':slip.employee_id.partner_id.id,
								'tax_id':line.salary_rule_id.tax_id.id,
								'amount':abs(line.total),
								})
					
					slip.write({'state': 'done'})
				ratification.ratification_line_ids = ratification_line 
				ratification.other_deduction_ids = other_deduction_line
			rec.write({'state': 'done'})

	def register_payment(self,branch):
		for slip in branch.slip_ids:
			for line in slip.loan_ids:
				line.line_id.write({'paid':True})
				line.loan_id._compute_amount()

	def canceled_register_payment(self,branch):
		for slip in branch.slip_ids:
			for line in slip.loan_ids:
				line.line_id.write({'paid':False})
				line.loan_id._compute_amount()
		

class hrPayrollStructure(models.Model):
	_inherit = 'hr.payroll.structure'
	
	appoiontment_type_ids = fields.Many2many('appointment.type', required=True,)
	category_ids = fields.Many2many('functional.category',string="Functional Category")


	def set_contracts_structure(self):

		domain = []
		appoiontment_list = []
		category_list = []
		if self.appoiontment_type_ids:
			for appoiontment in self.appoiontment_type_ids:
				if appoiontment.id not in appoiontment_list:
					appoiontment_list.append(appoiontment.id)

			domain.append(('appoiontment_type','in',appoiontment_list))

		if self.category_ids:
			for category in self.category_ids:
				if category.id not in category_list:
					category_list.append(category.id)

			domain.append(('category_id','in',category_list))
		
		for contract in self.env['hr.contract'].search(domain):
			contract.struct_id = self.id

class HrSalaryRule(models.Model):
	_name = 'hr.salary.rule'
	_inherit = ['hr.salary.rule','mail.thread','mail.activity.mixin']

	account_id = fields.Many2one("account.account",track_visibility="onchange", domain=[('is_group','=','sub_account')])
	tax_id = fields.Many2one("account.tax", string="Deduction Account",track_visibility="onchange")

		
	
			
