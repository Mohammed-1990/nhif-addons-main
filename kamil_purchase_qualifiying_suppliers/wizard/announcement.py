# *.* coding:utf-8 *.*

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Announcement(models.TransientModel):
	_name = 'tender.announcement'
	_description = 'Tender Announcement'

	announcement = fields.Html('Announcement')
	count = fields.Integer('Number Of Announcement')
	announ_attach = fields.Binary('Attachment')
	requisition_id = fields.Many2one('purchase.requisition' , 'Requisition')
	newspaper_ids = fields.One2many('announcement.newspaper.line', 'announcement_id',string="NewsPaper")

	@api.multi
	def create_annoncement(self):
		self.ensure_one()
		if not self.count:
			raise UserError(_("The announcement number is not exist please entered."))
		if self.env.context.get('active_model') == 'purchase.requisition':
			if not self.announ_attach and self.announcement == '<p><br></p>':
				raise UserError(_("You cannot confirm Announcement because there is no Announcement or Attachment."))

			requisition = self.env['purchase.requisition'].browse(self.env.context.get('active_ids'))
			requisition.write({'announcement':self.announcement,
								'announ_number':self.count,
								'announ_attach':self.announ_attach
							})
			# return requisition.action_set_announcment()


	@api.multi
	def action_newspaper(self):
		if not self.newspaper_ids:
			raise UserError(_("The newspaper is not exist please entered."))

		vals= []
		if self.env.context.get('active_model') == 'purchase.requisition':
			for res in self.newspaper_ids:
				vals.append((0, 0, {
					'newsPaper_id':res.newsPaper_id.id,
					'release_date':res.release_date,
					'release_number':res.release_number,
					'attach': res.attach
					}))

			requisition = self.env['purchase.requisition'].browse(self.env.context.get('active_ids'))
			requisition.write({'announcement_ids':vals,
							})
			return requisition.action_confirm_announcment()


class AnnouncementNewspaper(models.TransientModel):

	_name = 'announcement.newspaper.line'
	_description = 'Announcement NewsPaper Line'

	newsPaper_id = fields.Many2one('announcement.newspaper','NewsPaper')
	release_date = fields.Datetime('Release Date')
	release_number = fields.Char('Release Number')
	attach = fields.Binary('Attachment')
	announcement_id = fields.Many2one('tender.announcement')

	@api.constrains('release_date')
	def _check_date(self):
		if self.env.context.get('active_model') == 'purchase.requisition':
			if self.announcement_id.requisition_id.date_end and self.announcement_id.requisition_id.ordering_date :
				if self.announcement_id.requisition_id.date_end <= self.release_date :
					raise UserError(_("The Relase date is not valid '%s' because is larg than aggrement end date.") % self.release_date)
				if self.announcement_id.requisition_id.ordering_date >= self.release_date :
					raise UserError(_("The Relase date is not valid '%s' because is less than aggrement ordering date.") % self.release_date)
		
