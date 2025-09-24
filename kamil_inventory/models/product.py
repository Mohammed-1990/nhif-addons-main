# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class productCategory(models.Model):
    _inherit = 'product.category'

    number = fields.Char('Internal Number')
    warehouse_type = fields.Selection([('tasks', 'Tasks Warehouse'), ('laboratories', 'Laboratories Warehouse'),
                                       ('medical_supplies', 'Medical Supplies Warehouse'),
                                       ('medicine', 'Medicine Warehouse')], default='tasks', )

    @api.onchange('property_account_expense_categ_id')
    def onchange_property_account_expense_categ_id(self):
        self.budget_item_id = self.property_account_expense_categ_id.parent_budget_item_id.id


class productProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think
        # res = super(productProduct, self).name_get()

        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            categ_number = d.get('categ_number', False) or False
            if code and not categ_number:
                name = '[%s] %s' % (code, name)
            if not code and categ_number:
                name = '[%s] %s' % (categ_number, name)
            if code and categ_number:
                name = '[%s/%s] %s' % (code, categ_number, name)

            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id', 'attribute_value_ids', 'attribute_line_ids'],
                         load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped(
                'attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                        'categ_number': product.categ_id.number,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                    'categ_number': product.categ_id.number,
                }
                result.append(_name_get(mydict))
        return result


class ProductTemplate(models.Model):

	_inherit = 'product.template'
	_rec_name = 'long_name'

	short_code = fields.Char(size=5,readonly=True, copy=False ,
        required=False)
	code = fields.Char(compute='set_code_name')
	long_name = fields.Char(string="Display Name", compute='set_code_name')
	new_price = fields.Float(compute='compute_new_price')
	profit_margin = fields.Integer()
	qty_available = fields.Float('Quantity On Hand', compute='_compute_qty_available',)
	min_qty = fields.Float('Minimum Quantity')
	min_qty_test = fields.Boolean(compute='_compute_min_qty_test')

	_sql_constraints = [
		('name_uniq', 'unique(name)', 'The name of the product must be unique per company!'),
		('code_uniq', 'unique(code)', 'The code of the product must be unique per company!'),
	]
	def _compute_min_qty_test(self):
		for rec in self:
			if (rec.qty_available <= rec.min_qty):
				rec.min_qty_test = True
			else:
				rec.min_qty_test = False


	def compute_new_price(self):
		for rec in self:
			x = 0.0
			x = (rec.profit_margin * rec.list_price) / 100
			rec.new_price = rec.list_price + x

	def _compute_qty_available(self):
		for rec in self:
			rec.qty_available = sum(self.env['stock.quant'].search([('product_id','=',rec.id)]).mapped('quantity'))

	# @api.model
	# def create(self, vals):
	# 	if vals.get('short_code', _('New')) == _('New'):
	# 		vals['short_code'] = self.env['ir.sequence'].next_by_code('product.short.code')
	# 	result = super(productTemplate, self).create(vals)
	# 	return result

	@api.onchange('short_code')
	def _onchange_short_code(self):
		try:
			int(self.short_code)
			if self.short_code and len(self.short_code) != 5:
				raise UserError(_('Please make code 5 integers'))
		except:
			raise UserError(_('Please make code 5 integers'))


	@api.onchange('name','short_code','categ_id')
	def set_code_name(self):
		for rec in self:
			if rec.categ_id and rec.short_code:
				rec.code =   str(rec.categ_id.code) + '' + str(rec.short_code)
			else:
				rec.code = 'NEW'
			if rec.code != 'NEW' and rec.name:
				rec.long_name = '[' + rec.code + '] ' + rec.name

	@api.model
	def create(self, values):
		res = super(ProductTemplate, self).create(values)
		res.short_code = self.env['ir.sequence'].get('product.short.code')
		return res
