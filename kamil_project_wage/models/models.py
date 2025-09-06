# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError


class project_task(models.Model):
  _inherit = 'project.task'
  # planned_amount = fields.Integer('Planned Budget Amount')
  remaining_amount = fields.Integer('Remaining Budget Amount')
  wage = fields.Integer(string='Wage', default="100")

  @api.onchange('wage')
  def _onchange_wage(self):
      if self.wage and self.wage <= self.project_id.wage:
        self.project_id.write({'wage':abs(self.project_id.wage - self.wage)})
      elif self.wage and self.wage > self.project_id.wage:
        raise ValidationError(_("You can not assign amount for this sub project which is more than the remaining amount of its parent project !"))
      
  @api.onchange('wage')
  def _onchange_wage(self):
    for line in self.timesheet_ids:
      line.wage_no = self.wage            
      


  # @api.onchange('wage')
  # def onchange_wage(self):
  #   if self.task_id and self.task_id.wage and self.wage and self.wage <= self.task_id.wage:
  #     self.task_id.wage - = self.wage
  #   else:
  #     raise ValidationError(_("You can not assign amount for this sub project which is more than the remaining amount of its parent project !"))

  # @api.onchange('wage')
  # def _onchange_wage(self):
  #   if self.wage and self.wage <= self.project_id.wage:
  #     self.project_id.write({'wage':abs(self.project_id.wage - self.wage)})
  #   elif self.wage and self.wage > self.project_id.wage:
  #     raise ValidationError(_("You can not assign amount for this sub project which is more than the remaining amount of its parent project !"))
                


  # wage_id = fields.Integer(related='wage_id.partner_id.wage_no', string="Wage", readonly=True)


  @api.depends('planned_amount')
  def remaing_cost(self):
    remaing = 0

    for x in self.timesheet_ids:
      cost = x.cost

      remaing = planned_amount-cost

      remaing = self.remaining_amount 






class AccountAnalyticLine(models.Model):


  _inherit = 'account.analytic.line'

  wage_no = fields.Integer(string="Wage")
  cost_id = fields.Integer(string="Cost")


  # @api.onchange('wage')
  # def onchange_wage(self):
  #   if self.task_id and self.task_id.wage and self.wage and self.wage <= self.task_id.wage:
  #     self.task_id.wage -= self.wage
  #   else:
  #     raise ValidationError(_("You can not assign amount for this sub project which is more than the remaining amount of its parent project !"))




  @api.model
  def create(self, values):
    if values.get('cost_id'):
      task_id = self.env['project.task'].browse(values.get('task_id'))
      print(task_id)
      print(task_id.remaining_amount)
      lat_remain_amt = task_id.planned_amount - values.get('cost_id')
      # lat_remain_amt = task_id.remaining_amount - values.get('cost')
      task_vals = {
      'remaining_amount' : lat_remain_amt,
      }
      print(task_vals)
      task_id.write(task_vals)
    result = super(AccountAnalyticLine, self).create(values)
    return result



  @api.multi
  def write(self, values):
    if values.get('cost'):
      print(values.get('cost_id'))
      print(values.get('task_id'))
      print(self.task_id)
      task_id = self.env['project.task'].browse(self.task_id.id)
      task_ids = self.env['account.analytic.line'].search([('task_id', '=',task_id.id)])
      total_cost = 0
      for line in task_ids:
        total_cost = total_cost + line.cost
        print(line.cost_id)
        print(total_cost)
        lat_remain_amt = task_id.planned_amount - values.get('cost_id')
      # lat_remain_amt = task_id.planned_amount - total_cost
      task_vals = {
      'id' : task_id.id,
      'remaining_amount' : lat_remain_amt,
      }
      print(task_vals)
      task_id.write(task_vals)



    result = super(AccountAnalyticLine, self).write(values)
    return result
