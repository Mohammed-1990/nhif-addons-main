

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo.tools.safe_eval import safe_eval


class Project(models.Model):

    _inherit = 'project.project'

    planned_amount = fields.Integer('Planned Budget Amount')
    remaining_amount = fields.Integer('Remaining Budget Amount')




class Task(models.Model):

    _inherit = 'project.task'

    planned_amount = fields.Integer('Planned Budget Amount')
    remaining_amount = fields.Integer('Remaining Budget Amount')


    @api.onchange('planned_amount')
    def _onchange_planned_amount(self):
        if self.planned_amount:
            print(self.planned_amount)
            
    