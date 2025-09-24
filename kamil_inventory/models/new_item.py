# -*- coding: utf-8 -*-
# TODO this model need revision

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class KamilNewProductLines(models.Model):
    _name = 'new.product.line'

    product_name = fields.Char(string='Product Name')
    product_id = fields.Many2one('product.product', string='Product')
    product_type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'), ('product', 'Storable')],
                                    compute="_compute_product_info", store=True, inverse="_set_product_info")
    category_id = fields.Many2one('product.category', 'Product Category', compute="_compute_product_info", store=True,
                                  inverse="_set_product_info")
    cost = fields.Float(string='Cost Price')
    sale = fields.Float(string='Sale Price')
    uom = fields.Many2one('uom.uom', string='UOM', compute="_compute_product_info", store=True,
                          inverse="_set_product_info")
    note = fields.Char()
    new_product = fields.Many2one('new.product')
    created_prod = fields.Many2one('product.template')
    state = fields.Selection(
        [('no_process', 'Not Processed'), ('created', 'Created'), ('exist', 'Exist'), ('update', 'Updated'),
         ('reject', 'Rejected')], default='no_process', string='State', tracking=True)
    is_manager = fields.Boolean(string='Manager', default=False, compute="_check_user_group")
    short_code = fields.Integer('Product Code')

    @api.depends('product_id')
    def _compute_product_info(self):
        for rec in self:
            if rec.product_id and rec.new_product.type == 'update':
                rec.product_type = rec.product_id.type
                rec.category_id = rec.product_id.categ_id.id
                rec.uom = rec.product_id.uom_id.id
            elif not rec.product_id:
                rec.product_type = False
                rec.category_id = False
                rec.uom = False

    def _set_product_info(self):
        pass

    @api.multi
    def _check_user_group(self):
        for rec in self:
            if rec.new_product.state != "no_process":
                if rec.new_product.is_manager:
                    rec.is_manager = True
                else:
                    rec.is_manager = False

    @api.multi
    def create_product(self):
        vals = {
            'name': self.product_name,
            'type': self.product_type,
            'categ_id': self.category_id.id,
            'list_price': self.sale,
            'standard_price': self.cost,
            'uom_id': self.uom.id,
            'uom_po_id': self.uom.id,
        }
        self.created_prod = self.env['product.template'].with_context({'need_request': True}).create(vals)
        self.write({'state': 'created'})
        self.product_id = self.created_prod.id

    @api.multi
    def open_product(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'res_id': self.product_id.id,
            'view_type': 'form',
            'view_mode': 'form'
        }

    def action_exist(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'exist.add.update.wizard',
            'context': {'default_request_line_id': self.id},
            'view_mode': 'form',
            'target': 'new'
        }

    def action_update(self):
        if self.product_id:
            self.product_id.add_update_line_id = self.id
            self.write({'state': 'update'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'view_mode': 'form',
                'target': 'new'
            }
            self.write({'state': 'update'})
        else:
            raise UserError(_('There\'s no product selected in this line.'))

    def action_reject(self):
        self.write({'state': 'reject'})


class KamilNewProduct(models.Model):
    _name = 'new.product'
    _rec_name = 'new_request'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.onchange('type')
    def _onchange_type(self):
        if self.item_lines:
            self.item_lines = False

    def get_company_id(self):
        return self.env.user.company_id.id

    responsible = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    date = fields.Datetime(string='Request Date', default=datetime.now())
    new_request = fields.Char(string='Request ID', default="New")
    type = fields.Selection([('add', 'Addition'), ('update', 'Modification')], default="add", string="Type")
    item_lines = fields.One2many('new.product.line', 'new_product', string='New Items')
    is_manager = fields.Boolean(string='Manager', default=False, compute="_check_user_group")
    state = fields.Selection([('draft', 'Draft'), ('inventory_resp_approval', 'Inventory Responsible Approval'),
                              ('warehouse_manager', 'warehouse Manager HQ'),
                              ('erp_system_administrator', 'ERP System Administrator'), ('done', 'Done'),
                              ('cancel', 'Cancel')], default='draft', string='State', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Branch', default=get_company_id)

    @api.multi
    def _check_user_group(self):
        user_id = self._context.get('uid')
        user = self.env['res.users'].browse(user_id)
        if user.has_group('stock.group_stock_manager'):
            self.is_manager = True
        else:
            self.is_manager = False

    @api.model
    def create(self, vals):
        seq_code = False
        if vals['type'] == 'add':
            seq_code = 'add.new.product'
            seq = self.env['ir.sequence'].next_by_code(seq_code)
            if not seq:
                self.env['ir.sequence'].create({
                    'name': 'Add Product Request Sequence',
                    'code': seq_code,
                    'prefix': 'NI/',
                    'number_next': 1,
                    'number_increment': 1,
                    'use_date_range': True,
                    'padding': 4,
                })
                seq = self.env['ir.sequence'].next_by_code(seq_code)
            vals['new_request'] = seq
        elif vals['type'] == 'update':
            seq_code = 'update.product.request'
            seq = self.env['ir.sequence'].next_by_code(seq_code)
            if not seq:
                self.env['ir.sequence'].create({
                    'name': "Update Product Request Sequence",
                    'code': seq_code,
                    'prefix': 'UP/',
                    'number_next': 1,
                    'number_increment': 1,
                    'use_date_range': True,
                    'padding': 4,
                })
                seq = self.env['ir.sequence'].next_by_code(seq_code)
            vals['new_request'] = seq
        return super(KamilNewProduct, self).create(vals)

    @api.multi
    def submit_to_approval(self):
        if not any(line.item_lines for line in self):
            raise UserError(_('You have to set at least one product from request !'))
        self.write({'state': 'inventory_resp_approval'})

    @api.multi
    def action_confirm(self):
        self.write({'state': 'warehouse_manager'})

    @api.multi
    def warehouse_manager_confirm(self):
        self.write({'state': 'erp_system_administrator'})

    @api.multi
    def erp_system_administrator_confirm(self):
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    def unlink(self):
        if any(item.state in ('done') for item in self):
            raise UserError(_('You cannot delete done itme.'))
        return super(KamilNewProduct, self).unlink()