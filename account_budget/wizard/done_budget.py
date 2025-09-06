from odoo import fields, models, api


class Done_budget(models.TransientModel):
    _name = 'done.budget'

    budget = fields.Many2one(
        comodel_name='crossovered.budget',
        string='Budget',
        required=False, readonly=True)

    def close_budget(self):
        teams = self.env['crossovered.budget'].search([('id', '=', self.budget.id)])
        teams.update({'state': 'done'})

    @api.model
    def default_get(self, fields):
        rec = super(Done_budget, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        if active_model == 'crossovered.budget':
            lead = self.env[active_model].browse(self.env.context.get('active_id')).exists()
            if lead:
                rec.update(
                    budget=lead.id,
                )
        return rec
