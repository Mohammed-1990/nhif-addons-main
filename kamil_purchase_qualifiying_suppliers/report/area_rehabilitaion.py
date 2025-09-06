# *.* codig:utf-8 *.*

from odoo import models, fields, api

class AreaRehabiliation(models.AbstractModel):
	_name = 'report.kamil_purchase_qualifiying_suppliers.area_template'

	@api.model
	def _get_report_values(self, docids, data=None):
		area_id = self.env['area.rehabilitation'].search([('id','=',data['form']['area_id'])])
		domain = []
		docs=[]
		