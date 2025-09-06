# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime

class hrLeaveAllocation(models.Model):
	_inherit = 'hr.leave.allocation'

	degree_ids = fields.Many2many('functional.degree',string="Functional Degree",track_visibility="onchange")
	fun_category_ids = fields.Many2many('functional.category',string="Functional Category",track_visibility="onchange")
	name = fields.Char(string="Allocation Mode",track_visibility="onchange")
	start_date = fields.Date(track_visibility="onchange")
	end_date = fields.Date(track_visibility="onchange")
	holiday_type = fields.Selection([
        ('company', 'By Branch'),
        ('department', 'By Department'),
        ('appoiontment_type', 'By Appointment Type'),
        ('degree','By Degrees'),
        ('functional_cagtegory',('By Functional Category')),
        ('employee', 'By Employeee'),],
        string='Eligible', readonly=True, required=True, default='company',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},track_visibility="onchange")
	appoiontment_type=fields.Many2many('appointment.type',track_visibility="onchange")
	state = fields.Selection([
        ('draft', 'Personnel'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Human Resource Management'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'General Directorate of Human Resources')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        )

	_sql_constraints = [
        ('type_value',
         "CHECK(1=1)",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)", "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]

	def leave_allocations(self):
		print('#########################')
	# 	for leave_type in self.env['hr.leave.type'].search([('annually','=',True)]):
	# 		print('#########################')
	# 		today = date.today()	
	# 		self.env.cr.execute("SELECT * FROM hr_employee  WHERE entry_date = '%s'" %today)
	# 		employees = self.env.cr.fetchall()
	# 		for employee in employees:
	# 			self.env['hr.leave.allocation'].create({})

	# 		print(employees)
	# 		print('#########################')
	# 		print('#########################')



	@api.multi
	def name_get(self):
		res = []
		for allocation in self:
			if allocation.holiday_type == 'company':
				target = allocation.mode_company_id.name
			elif allocation.holiday_type == 'department':
				target = allocation.department_id.name
			elif allocation.holiday_type == 'category':
				target = allocation.category_id.name
			elif allocation.holiday_type == 'appoiontment_type':
				string = 'انواع التعيين ('
				for appoiontment in allocation.appoiontment_type:
					string += appoiontment.name +'    '
				string +=')'
				target = string
			elif allocation.holiday_type == 'degree':
				string = 'الدرجات ('
				for degree in allocation.degree_ids:
					string += degree.name +'    '
				string +=')'
				target = string
			elif allocation.holiday_type == 'functional_cagtegory':
				string = 'الفئات الوظيفية ('
				for category in allocation.fun_category_ids:
					string += category.name +'    '
				string +=')'
				target = string
			elif allocation.holiday_type == 'employee':
				target = allocation.employee_id.name

			res.append(
                (allocation.id,
                 _("Allocation of %s : %.2f %s to %s") %
                 (allocation.holiday_status_id.name,
                  allocation.number_of_hours_display if allocation.type_request_unit == 'hour' else allocation.number_of_days,
                  _('hours') if allocation.type_request_unit == 'hour' else _('days'),
                  target))
            )
		return res



	def _action_validate_create_childs(self):
		childs = self.env['hr.leave.allocation']
		if self.state == 'validate' and self.holiday_type in ['appoiontment_type', 'department', 'company', 'degree', 'functional_cagtegory']:
			domain = []
			if self.holiday_type == 'appoiontment_type':
				appoiontment_list = []
				for appoiontment in self.appoiontment_type:
					appoiontment_list.append(appoiontment.id)
				domain.append(('appoiontment_type','in',appoiontment_list))
			elif self.holiday_type == 'department':
				domain.append(('department_id','=',self.department_id.id))
			elif self.holiday_type == 'degree':
				degrees_list = []
				for deg in self.degree_ids:
					degrees_list.append(deg.id)
				domain.append(('degree_id','in',degrees_list))
			elif self.holiday_type == 'functional_cagtegory':
				fun_category_list = []
				for cat in self.fun_category_ids:
					fun_category_list.append(cat.id)
				domain.append(('category_id','in',fun_category_list))
			else:
				domain.append(('company_id','=',self.mode_company_id.id))
			employees = self.env['hr.employee'].search(domain)
			employees_list = []
			count = 0
			for employee in employees:
				union_flag = 1
				if self.holiday_status_id.union_leave == True:
					if employee.is_union == True:
						union_flag = 1
					else:
						union_flag = 0

				gender_flag = 1
				if self.holiday_status_id.available_gender == 'yes':
					if employee.gender == self.holiday_status_id.gender:
						gender_flag = 1
					else:
						gender_flag = 0

				marital_flag = 1
				if self.holiday_status_id.available_marital == 'yes':
					if employee.marital == self.holiday_status_id.marital:
						marital_flag = 1
					else:
						marital_flag = 0

				religion_flag = 1
				if self.holiday_status_id.religion == 'yes':
					for religion in self.holiday_status_id.religion_id:
						if employee.religion == religion:
							religion_flag = 1
							break
						else:
							religion_flag = 0


				if union_flag == 1 and gender_flag == 1 and marital_flag == 1 and religion_flag == 1:
					employees_list.append(employee)
					count += 1

				

			for employee in employees:
				childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))
            # TODO is it necessary to interleave the calls?
			childs.action_approve()
			if childs and self.holiday_status_id.validation_type == 'both':
				childs.action_validate()
		return childs


	@api.multi
	def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        # if any(holiday.state != 'confirm' for holiday in self):
        #     raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

		self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})
		self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
		self.activity_update()
		return True

	@api.multi
	def action_validate(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		for holiday in self:
			# if holiday.state not in ['confirm', 'validate1']:
			# 	raise UserError(_('Leave request must be confirmed in order to approve it.'))

			holiday.write({'state': 'validate'})
			if holiday.validation_type == 'both':
				holiday.write({'second_approver_id': current_employee.id})
			else:
				holiday.write({'first_approver_id': current_employee.id})

			holiday._action_validate_create_childs()
		self.activity_update()
		return True