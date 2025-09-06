# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Announcement(models.TransientModel):
	_inherit = 'tender.announcement'

		
	@api.multi
	def create_annoncement(self):
		res = super(Announcement, self).create_annoncement()

		context = dict(self._context or {})
		active_id = context.get('active_id', False)
		if active_id:
			inv = self.env['scrap.request'].browse(active_id)
			if self.env.context.get('active_model') == 'scrap.request':
				inv.write({'announcement':self.announcement,
							'announ_number':self.count,
							'announ_attach':self.announ_attach
							})
		return res

	@api.multi
	def action_newspaper(self):
		res = super(Announcement, self).action_newspaper()
		vals= []
		context = dict(self._context or {})
		active_id = context.get('active_id', False)
		if self.env.context.get('active_model') == 'scrap.request':
			inv = self.env['scrap.request'].browse(active_id)
			for res in self.newspaper_ids:
				vals.append((0, 0, {
					'newsPaper_id':res.newsPaper_id.id,
					'release_date':res.release_date,
					'release_number':res.release_number,
					'attach': res.attach
					}))
			inv.write({'announcement_ids':vals,
							})
			inv.action_confirm_announcment()
		return res


