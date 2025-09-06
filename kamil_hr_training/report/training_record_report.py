from odoo import models,fields,api
from datetime import date, datetime
import math

class ReporttrainingRecord(models.AbstractModel):
	"""Abstract Model for report template.

	for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
	"""
	_name = 'report.kamil_hr_training.training_record_report_view'

	@api.model
	def _get_report_values(self, docids, data=None):
		domain = []
		program_execution_id = data['form']['program_execution_id']
		if program_execution_id:
			domain.append(('id','=',program_execution_id))

		TheProgram = self.env['program.execution'].search(domain)

		docs = []
		for record in self.env['program.execution'].search(domain):
			employee_data = [] 
			employees_count = 0
			employee = ''
			branch = ''
			department = ''
			job_title = ''
			for line in record.line_ids:
				employees_count += 1
				if employees_count == 1:
					employee = line.employee_id.name
					branch = line.employee_id.company_id.name
					department = line.employee_id.department_id.name
					job_title = line.employee_id.job_title_id.name
				else:
					employee_data.append({'employee':line.employee_id.name,
						'branch':line.employee_id.company_id.name,
						'department':line.employee_id.department_id.name,
						'job_title':line.employee_id.job_title_id.name,
					})
			no_days = 0
			if record.date_to and record.date_from:
				no_days = (record.date_to - record.date_from).days + 1
			
			docs.append({'name':record.name,
					'country':record.country.name,
					'date_from':record.date_from,
					'date_to':record.date_to,
					'city_id':record.city_id.name,
					'training_center':record.training_center.name,
					'financier_name':record.financier_name,
					'total_cost':record.total_cost,
					'no_days':no_days,
					'no_hours':record.training_programs.no_hours,
					'type':record.training_type.name,
					'employees_count':employees_count,
					'employee_data':employee_data,					
					'employee':employee,
					'branch':branch,
					'department':department,
					'job_title':job_title,
					})

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
		}