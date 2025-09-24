# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class IndirectReceive(models.Model):
    _name = 'indirect.receive'
    _rec_name = 'request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def get_company_id(self):
        return self.env.user.company_id.id


    def _get_warehouse(self):
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.company_id.id)],
            limit=1
        )
        return warehouse.id if warehouse else False

    def _default_currency_id(self):
        company_id = self.env.context.get('force_company') or self.env.context.get('company_id') or self.env.user.company_id.id
        return self.env['res.company'].browse(company_id).currency_id
    request = fields.Char(string="Request ID", default='New')
    date = fields.Datetime(string="Date", default=datetime.now())
    responsible_id = fields.Many2one('res.users', string='Responsible',
                                     default=lambda self: self.env.user)
    receive_for = fields.Many2one('res.partner',required=True)
    warehouse_type = fields.Selection(
        [('tasks', 'Tasks Warehouse'), ('laboratories', 'Laboratories Warehouse'),
         ('medicine', 'Medicine Warehouse'), ('medical_supplies', 'Medical Supplies Warehouse')],
        default='tasks',required=True )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Warehouse",
        default=lambda self: self._get_warehouse()
    )
    category_id = fields.Many2one('product.category', )
    location_id = fields.Many2one('stock.location', 'Location',
                                  domain="[('usage','=','internal'),('warehouse_id','=',"
                                         "warehouse_id)]",required=True)
    warehouse_root_location_id = fields.Many2one(
        'stock.location',
        compute='_compute_warehouse_root_location',
        store=True
    )
    state = fields.Selection([('draft', 'Requestor'),
                              ('finance_admin_manager', 'Finance and Administration Management'),
                              ('support_services', 'Support services'),
                              ('medical_services', 'Medical services'),
                              ('director_of_health_services_department', 'Director of Health Services Department'),
                              ('inventory_manager', 'Inventory Department'),
                              ('inventory_employee', 'Inventory Keeper'), ('in_progress',
                                                                           'In Progress'),
                              ('done', 'Done'), ('cancel', 'Cancel')],
                             string="State", default="draft", track_visibility='onchange')
    line_ids = fields.One2many('indirect.receive.line', 'requests', string="Request Lines")
    show_issuing_order = fields.Boolean(default=False)
    company_id = fields.Many2one('res.company', 'Branch', default=get_company_id)
    document = fields.Binary(string='Receive Indirect Document')
    forty_six_seen = fields.Binary()
    serial_number = fields.Char()
    operation_type = fields.Selection(
        [('direct', 'Direct exchange'),
         ('indirect', 'Indirect exchange')], track_visibility='onchange')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=_default_currency_id)
    amount_total = fields.Monetary(
        string="Total",
        compute="_amount_all",
        store=True,
        currency_field="currency_id"
    )

    @api.depends('warehouse_id')
    def _compute_warehouse_root_location(self):
        for rec in self:
            rec.warehouse_root_location_id = rec.warehouse_id.view_location_id.id if rec.warehouse_id else False

    def action_return(self):
        if self.state == 'finance_admin_manager':
            self.state = 'draft'
        if self.state == 'inventory_manager':
            self.state = 'finance_admin_manager'
        if self.state == 'inventory_employee':
            self.state = 'inventory_manager'
    def action_return_2(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        seq_code = 'indirect.receive.sequence'
        seq = self.env['ir.sequence'].next_by_code(seq_code)
        vals['request'] = seq
        return super(IndirectReceive, self).create(vals)


    # @api.onchange('state')
    # def _onchange_state(self):
    #     for rec in self:
    #         if rec.state in 'done':
    #             rec.line_ids.item_id.list_price = rec.line_ids.new_unit_price






    @api.depends('line_ids.total_price')
    def _amount_all(self):
        for order in self:
            order.amount_total = sum(line.total_price for line in order.line_ids)


    def action_draft(self):
        self.ensure_one()  # يضمن وجود سجل واحد فقط
        if not any(line.line_ids for line in self):
            raise UserError(_('You have to set at least one product from request !'))

        if self.operation_type not in ['direct','indirect']:
            raise UserError(_('Please select operation type!!'))
        if  self.warehouse_type =='tasks':
            self.write({'state': 'finance_admin_manager'})
        if  self.warehouse_type in ['laboratories','medicine']:
            self.write({'state': 'support_services'})
        if self.warehouse_type in ['medical_supplies']:
            self.write({'state': 'medical_services'})



    def action_finance_admin_manager(self):
        self.write({'state': 'inventory_manager'})

    def action_support_services(self):
        self.write({'state': 'director_of_health_services_department'})

    def action_medical_services(self):
        self.write({'state': 'director_of_health_services_department'})

    def action_director_of_health_services_department(self):
        self.write({'state': 'inventory_manager'})

    def action_inventory_manager(self):
        self.write({'state': 'inventory_employee'})

    def action_inventory_employee(self):
        self.write({'state': 'in_progress'})

    def action_inventory_done(self):
        picking_obj = self.env['stock.picking']

        # البحث عن picking type outgoing للـ warehouse
        picking_type_id = self.env['stock.picking.type'].search([
            ('code', 'ilike', 'outgoing'),
            ('warehouse_id', '=', self.warehouse_id.id)
        ], limit=1)
        if not picking_type_id:
            raise ValidationError(_('No picking type found for this warehouse.'))

        # تحديد المواقع
        location_id = self.location_id
        location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
        if not location_dest_id:
            raise ValidationError(_('Destination location with usage "customer" not found.'))

        for record in self:
            picking_id = picking_obj.create({
                'partner_id': record.responsible_id.partner_id.id,
                'origin': str(record.request),
                'scheduled_date': fields.Datetime.now(),
                'picking_type_id': picking_type_id.id,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'move_ids_without_package': record._prepare_picking_lines(),
                'indirect_receive_id': record.id
            })
            picking_id.action_assign()
            if picking_id:
                self.show_issuing_order = True

    def _prepare_picking_lines(self):

        picking_lines = []
        for rec in self:
            warehouse = rec.env['stock.warehouse'].search([('company_id', '=', rec.company_id.id)], limit=1)
            picking_type_id = rec.env['stock.picking.type'].search(
                [('code', 'ilike', 'outgoing'), ('warehouse_id', '=', warehouse.id),
                 ('default_location_src_id', '=', rec.location_id.id)], limit=1)

            if rec.line_ids:
                for line in rec.line_ids:
                    picking_lines.append((0, 0, {
                        'name': _('Product ') + line.item_id.name,
                        'product_uom': line.item_id.uom_id.id,
                        'product_id': line.item_id.id,
                        'product_uom_qty': line.qty,
                        'reserved_availability': line.qty,
                        'date_expected': self.date,
                        'picking_type_id': picking_type_id.id,
                        'location_id': rec.location_id.id,
                        'location_dest_id': 1,
                        'state': 'draft'
                    }))
        return picking_lines

    def action_view_picking(self):
        sp = self.env['stock.picking'].search([('indirect_receive_id', '=', self.id)])
        if sp:
            return {
                'name': _('Issuing Order'),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'view_id':self.env.ref('stock.view_picking_form').id,
                'domain': [('indirect_receive_id', '=', self.id)]
            }
        else:
            raise UserError(
                _('There\'s no associated issuing order to this need request, please check with Inventory Keeper!!'))


    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        self.category_id = False
        self.location_id = False
        self.line_ids = [(5, 0, 0)]  # يمسح كل السطور المرتبطة
        return {'domain': {'category_id': [('warehouse_id', '=', self.warehouse_id.id)]}}

    @api.onchange('warehouse_type')
    def _onchange_warehouse_type(self):
        self.line_ids = [(5, 0, 0)]


    # يمسح كل السطور المرتبطة



class IndirectReceiveLine(models.Model):
    _name = 'indirect.receive.line'
    item_id = fields.Many2one('product.product', string="Item", required=True,)
    item_code = fields.Char(related="item_id.code")
    category_id = fields.Many2one('product.category', related="item_id.categ_id")
    currency_id = fields.Many2one(related='requests.currency_id', store=True, string='Currency', readonly=True)
    uom = fields.Many2one('uom.uom', related="item_id.uom_id",string="UOM", readonly=True)
    qty = fields.Float(string="Quantity", required=True)
    qty_available = fields.Float()
    requests = fields.Many2one('indirect.receive')
    unit_price = fields.Float(related='item_id.new_price',readonly=False)
    total_price = fields.Monetary(compute='compute_total_price',store=True)


    @api.onchange('item_id')
    def compute_new_price(self):
        for record in self:
            if record.requests and record.requests.warehouse_type:
                warehouse_type = record.requests.warehouse_type

                # الحصول على الأصناف المرتبطة بنوع المخزن
                categories = self.env['product.category'].search([('warehouse_type', '=', warehouse_type)])
                products = self.env['product.product'].search([('categ_id', 'in', categories.ids)]) if categories else self.env['product.product'].browse([])

                # تعيين الـ domain للـ item_id
                record.item_id = record.item_id if record.item_id in products else False
                domain = {'item_id': [('id', 'in', products.ids)]}

                # تحديث السعر تلقائيًا إذا تم اختيار منتج
                if record.item_id:
                    if record.requests.operation_type == 'direct':
                        record.unit_price = record.item_id.lst_price  # أو أي حقل سعر آخر حسب الحاجة
                    elif record.requests.operation_type == 'indirect':
                        record.unit_price = record.item_id.new_price

                return {'domain': domain}


    @api.depends('qty', 'unit_price')
    def compute_total_price(self):
        for rec in self:
            rec.total_price = rec.unit_price * rec.qty

    # @api.onchange('requests')
    # def _onchange_requests(self):
    # 	domain = [('type', '=', 'product')]
    # 	if self.requests.warehouse_id and not self.requests.category_id:
    # 		categories = self.env['product.category'].search(
    # 			[('warehouse_id', '=', self.requests.warehouse_id.id)]).ids
    # 		domain.append(('categ_id', 'in', categories))
    # 	elif self.requests.category_id:
    # 		domain.append(('categ_id', '=', self.requests.category_id.id))
    #
    # 	return {'domain': {'item_id': domain}}

    @api.onchange('item_id')
    def _onchange_item_id(self):
        if self.item_id:
            qty_available = 0.00
            location_id = self.requests.warehouse_id.lot_stock_id
            for quant in self.env['stock.quant'].search(
                    [('product_id', '=', self.item_id.id), ('location_id', '=', location_id.id)]):
                if quant.quantity > 0:
                    qty_available += quant.quantity
            self.qty_available = qty_available

    @api.onchange('qty')
    def _onchange_qty(self):
        for rec in self:
            if rec.qty > rec.qty_available:
                raise UserError(_('You can not insert qty greatest than onhand qty !!'))


# في stock.picking model أو عبر الوراثة
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    indirect_receive_id = fields.Many2one('indirect.receive', string='Indirect Receive',copy=False)





