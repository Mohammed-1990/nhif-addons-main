from odoo import models,fields,api
from datetime import datetime
from datetime import date
from dateutil import relativedelta


class record_job_wizard(models.TransientModel):
	_name="record.job.wizard"

	date_from = fields.Date(string='Date From', required=True,
	    default=datetime.now().strftime('%Y-%m-01'))
	date_to = fields.Date(string='Date To', required=True,
	    default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

	@api.multi
	def print_report(self):
	    active_ids = self.env.context.get('active_ids', [])
	    datas = {
	         'ids': active_ids,
	         'model': 'record.job.wizard',
	         'form': self.read()[0]
	    }
	    return self.env.ref('kamil_hr.record_job_report').report_action([], data=datas)

	# date_from =fields.Date("Date From")
	# date_to =fields.Date("Date To")

	# @api.multi
	# def print_report(self):
	# 	datas={}
	# 	data=self.read()[0]
	# 	datas={
	# 	         'ids':[],
	# 	         'model':'record.job.wizard',
	# 	         'form':data
	# 	}

	# 	return self.env['report'].get_action(self,'kamil_hr.record_job_report').report_action([], data=datas)

