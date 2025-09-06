# -*- coding:utf-8 -*-
from odoo import models, fields, api


class RatificationReport(models.AbstractModel):
	_name = 'report.kamil_accounting_reports.ratification_list_template'


	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['from']['date_from']
		date_to = data['from']['date_to']
		partner_ids = data['from']['partner_ids']
		group_id = data['from']['group_id']
		company_id_logo = self.env.user.company_id.logo

		vals = []
		docs = []
			
		for the_partner_id in partner_ids:
			vals = []
			partner_name = ''
			partner_ids = []
			partner_ids.append( the_partner_id )
			for partner in self.env['res.partner'].search([('id','=',the_partner_id)]):
				partner_name = partner.name
				if partner.parent_id:
					partner_ids.append( partner.parent_id.id )
					partner_name = partner_name + ', ' +  partner.parent_id.name
				for child in partner.child_ids:
					partner_ids.append( child.id )
					partner_name = partner_name + child.name


			total_amount = 0
			total_deduction = 0
			list_name = ''
		
			for ratification in self.env['ratification.ratification'].search([('state','in',['payment_created','payment_confirmed','paid']),('date','>=', date_from),('date','<=',date_to),('ratification_list_id','!=',False)],order='date asc'):

				total_amount = 0
				total_deduction = 0
				list_name = ''

				list_name = ratification.ratification_list_id.name

				found = False
				for line in ratification.line_ids:
					

					if line.partner_id.id in partner_ids and line.account_id:

						found = True
						total_amount = total_amount + line.amount
						for deduction_line in line.deduction_ids:
							total_deduction = total_deduction + deduction_line.amount

				for other_deduction_line in ratification.ratification_list_id.other_deduction_ids:
					if other_deduction_line.partner_id.id in partner_ids and other_deduction_line.tax_id:
						found = True
						total_deduction = total_deduction + other_deduction_line.amount

				if found:
					payment_number = ''
					payment_date = ''
					payment_type = ''
					for payment in self.env['ratification.payment'].search([('ratification_id','=',ratification.id)]):
						payment_number = payment.code
						payment_date = payment.date
						payment_type = payment.payment_type

					vals.append({
						'payment_number' : payment_number,
						'payment_date' : payment_date,
						'amount': total_amount,
						'deduction_amount': total_deduction,
						'net_amount': total_amount - total_deduction,
						'payment_type' : payment_type,
						'name': list_name,
					})
			docs.append({
				'partner':partner_name,
				'data':vals,
			})






			# if len(partner_ids) == 1:
			# 	self._cr.execute("select  payment.code payment_number, payment.date payment_date, sum(rat_line.amount) line_amount, (sum(deduction.amount)  + sum(other_deduction.amount)) deduction, (sum(rat_line.amount)  - ( sum(deduction.amount)  + sum(other_deduction.amount) )  ) net_amount, payment.payment_type payment_type, rat_list.name description from ratification_list rat_list inner join ratification_line rat_line on rat_line.ratification_list_id = rat_list.id inner join ratification_ratification rat on rat.ratification_list_id =  rat_list.id inner join ratification_payment payment on payment.ratification_id = rat.id full outer join ratification_line_tax_line deduction on deduction.ratification_line_id = rat_line.id full outer join list_other_deduction other_deduction on other_deduction.ratification_list_id = rat_list.id inner join res_partner on res_partner.id = rat_line.partner_id where rat.state in ('payment_created','payment_confirmed','paid') and res_partner.id = " +str(the_partner_id)+ " and other_deduction.partner_id = " + str(the_partner_id) + " and payment.date >= '"+str(date_from)+"' and payment.date <= '"+str(date_to)+"' ")

			# else:
			# 	self._cr.execute("select  payment.code payment_number, payment.date payment_date, sum(rat_line.amount) line_amount, (sum(deduction.amount)  + sum(other_deduction.amount)) deduction, (sum(rat_line.amount)  - ( sum(deduction.amount)  + sum(other_deduction.amount) )  ) net_amount, payment.payment_type payment_type, rat_list.name description from ratification_list rat_list inner join ratification_line rat_line on rat_line.ratification_list_id = rat_list.id inner join ratification_ratification rat on rat.ratification_list_id =  rat_list.id inner join ratification_payment payment on payment.ratification_id = rat.id full outer join ratification_line_tax_line deduction on deduction.ratification_line_id = rat_line.id full outer join list_other_deduction other_deduction on other_deduction.ratification_list_id = rat_list.id inner join res_partner on res_partner.id = rat_line.partner_id where rat.state in ('payment_created','payment_confirmed','paid') and res_partner.id in " + str(tuple(partner_ids) ) + " and other_deduction.partner_id in " + str(tuple(partner_ids) ) + " and payment.date >= '"+str(date_from)+"' and payment.date <= '"+str(date_to)+"'  ")

			# list_records = self.env.cr.fetchall()

			# for list_record in list_records:
			# 	vals.append({
			# 		'payment_number' : list_record[0],
			# 		'payment_date' : list_record[1],
			# 		'amount': list_record[2] or 0,
			# 		'deduction_amount': list_record[3] or 0,
			# 		'net_amount': list_record[4] or 0,
			# 		'payment_type' :  list_record[5],
			# 		'name': list_record[6],
			# 	})

			# docs.append({
			# 	'partner':partner_name,
			# 	'data':vals,
			# })

		return {
			'doc_ids': data['ids'],
			'doc_model': data['model'],
			'docs': docs,
			'date_from': date_from,
			'company_id_logo': company_id_logo,
			'date_to' : date_to, 
		}


		