
# -*- coding:utf-8 -*-
from odoo import models, fields, api


class MontlyAllocationReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.monthly_allocation_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		month = data['from']['month']
		year = data['from']['year']
		company_id_logo = self.env.user.company_id.logo
		

		docs = []	
		allocation = self.env['kamil.customization'].search([('year','=',year),('month','=',month)], limit=1)

		companies = self.env['res.company'].search([])
		com_list = []
		for company in companies:
			com_list.append({'id':company.id, 'name':company.name})

		
		for company in companies:
			amount = 0.0
			medicine = labs = other = transformed = 0.0
			total = 0.0
			branch_total = 0.0
			for allocat in allocation.line_ids:
				if company['id'] == allocat.branch_id.id:
					amount = allocat.customized_amount

				for line in allocat.loans_from_branches_ids:
					if allocat.branch_id.id == line.parent_branch_id.id == company['id']:
						if line.item_type == 'medicine':
							medicine += line.amount
						if line.item_type == 'labs':
							labs += line.amount
						if line.item_type == 'transformed':
							transformed += line.amount
						if line.item_type == 'other':
							other += line.amount


				for line in allocat.deduction_ids:
					if allocat.branch_id.id == line.parent_branch_id.id == company['id']:
						if line.item_type == 'medicine':
							medicine += line.amount
						if line.item_type == 'labs':
							labs += line.amount
						if line.item_type == 'transformed':
							transformed += line.amount
						if line.item_type == 'other':
							other += line.amount
				total += medicine + labs + transformed + other


			com_data = []
			for comp in companies:
				amount_1 = 0.0
				for allocat in allocation.line_ids :
					if company['id'] == allocat.branch_id.id:
						for line in allocat.loans_from_branches_ids:
							if comp['id'] == line.parent_branch_id.id:
								amount_1 = line.amount

				com_data.append(amount_1)
			total += sum([v for v in com_data])


			branch_total = amount - total
			docs.append({
				'company':company['name'],
				'amount':amount,
				'medicine':medicine,
				'labs':labs,
				'transformed':transformed,
				'com_data':com_data,
				'other':other,
				'total':total,
				'branch_total':branch_total

				})
		
		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'month': month,
			'year' : year,
			'company_id_logo': company_id_logo,
			'com_list':com_list
		}


		