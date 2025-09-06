# -*- coding: utf-8 -*-

from odoo import models, fields, api
###################Employee Data####################
class emp(models.Model):
	_inherit = ['mail.thread','mail.activity.mixin']

	_name ="archive.archive"
	_rec_name = "employee_id"
	employee_id = fields.Many2one('hr.employee',required=True, track_visibility="onchange")
	employee_no = fields.Integer(track_visibility="onchange")
	branch_id = fields.Many2one('res.company',string="Branch", related='employee_id.company_id',readonly=True, track_visibility="onchange")
	file_no = fields.Char(required=True, track_visibility="onchange")
	closet_no = fields.Char(track_visibility="onchange")
	box_no = fields.Char(track_visibility="onchange")

	certificates_id = fields.One2many("certi.certi","certi_id")
	appdocuments_id = fields.One2many("appdoc.appdoc","appdoc_id")
	promotions_id = fields.One2many("promo.promo","promo_id")
	vacations_id = fields.One2many("vaca.vaca","vaca_id")
	bonuses_id = fields.One2many("bonu.bonu","bonu_id")
	movements_id = fields.One2many("move.move","move_id")
	endservice_id = fields.One2many("eos.eos","eos_id")
	servicerecord_id = fields.One2many("servrec.servrec","servrecord_id")
	medical_id = fields.One2many("medical.medical","med_id")
	training_misssions_id = fields.One2many("training.missions","training_id")
	secret_report_id = fields.One2many("secret.report","secret_id")
	accounting_procedures_id =fields.One2many("accounting.procedures","procedures_id")
	@api.onchange('employee_no')
	def _onchange_employee_no(self):
		if self.employee_no:
			self.employee_id = False
			self.employee_id = self.env['hr.employee'].search([('number','=',self.employee_no)],limit=1).id
			
	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		if self.employee_id:
			self.employee_no = False
			self.employee_no = self.employee_id.number
			
########### Certificates ######################
class Certificates(models.Model):
	_name = "certi.certi"
	doc = fields.Binary("Document" , required=True)
	doc_name = fields.Char("Document Name" , required=True)
	certi_id = fields.Many2one("archive.archive")

########### Appointment Documents ##############
class AppointmentDocuments(models.Model):
	_name ="appdoc.appdoc"
	doc = fields.Binary("Document" , required=True)
	doc_name = fields.Char("Document Name", required=True)
	appdoc_id = fields.Many2one("archive.archive")

########### Promotions ######################
class Promotions(models.Model):
	_name = "promo.promo"
	doc = fields.Binary("Document" , required=True)
	doc_name = fields.Char("Document Name", required=True)
	promo_id = fields.Many2one("archive.archive")

########### Vacations ######################
class Vacations(models.Model):
	_name = "vaca.vaca"
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	vaca_id = fields.Many2one("archive.archive")

########### Bonuses ######################
class Bonuses(models.Model):
	_name = "bonu.bonu"
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	bonu_id = fields.Many2one("archive.archive")

########### Movements ######################
class Movements(models.Model):
	_name = "move.move"
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	move_id = fields.Many2one("archive.archive")


########### End Of Service ######################
class EndOfService(models.Model):
	_name = "eos.eos"
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	eos_id = fields.Many2one("archive.archive")
	
########### Service Record ######################
class ServiceRecord(models.Model):
	_name = "servrec.servrec"
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	servrecord_id = fields.Many2one("archive.archive")

class Medical(models.Model):
	_name = 'medical.medical'
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	med_id = fields.Many2one("archive.archive")

class TrainingAndMissions(models.Model):
	_name = 'training.missions'
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	training_id = fields.Many2one("archive.archive")

class accountingProcedures(models.Model):
	_name = 'accounting.procedures'
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	procedures_id = fields.Many2one("archive.archive")

class ReportSecret(models.Model):
	_name = "secret.report"
	doc = fields.Binary("Document", required=True)
	doc_name = fields.Char("Document Name", required=True)
	secret_id = fields.Many2one("archive.archive")