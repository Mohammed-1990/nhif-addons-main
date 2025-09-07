from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from . import amount_to_text as amount_to_text_ar
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT   # 👈 أضف ده
import qrcode
import base64
from io import BytesIO
import binascii
import pytz


class Collection(models.Model):
    _name = 'collection.collection'
    _description = 'Revenues Collection'
    _order = 'id desc'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']


    ref = fields.Char(string="Recipt Number",track_visibility='always', copy=False, default='/')
    partner_id = fields.Many2one('res.partner', string='Receipt From',track_visibility='always')
    state_id = fields.Many2one('res.company', string='Branch',default= lambda self:self.env.user.company_id.id,track_visibility='always')
    date = fields.Date(string='Collection Date',track_visibility='always',default=lambda self: fields.Date.today(), copy=False)
    operation_type = fields.Selection([('subscription','Subscription'),('other_revenues','Other Revenues'),('customization','Customization')], default='subscription',track_visibility='always')
    collection_type = fields.Selection([('Cheque','Cheque'),('cash','Cash'),('bank_transfer','Bank Transfer'),('counter_cheque','Counter Cheque'),('e_bank','E Bank')], default='cash',track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency',default= lambda self:self.env.user.company_id.currency_id.id,track_visibility='always')
    cheque_number = fields.Char('Cheque Number',track_visibility='always')
    cheque_bank = fields.Many2one('cheque.bank',string='Cheque Bank',track_visibility='always')
    subscription_date_from = fields.Date(string='Date From',track_visibility='always')
    subscription_date_to = fields.Date(string='Date To',track_visibility='always')
    name = fields.Text(string='Description',track_visibility='always',size=100)
    collector_id = fields.Many2one('hr.employee', string='Collector', default= lambda self:self.get_collector() ,track_visibility='always')
    collector_account_id = fields.Many2one('account.account',string='Collector Account', related='collector_id.collector_account_id', track_visibility='always')
    # collector_account_id = fields.Many2one('account.account',string='Collector Account', default= lambda self:self.get_collector_account() ,track_visibility='always')
    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
    e_15_no = fields.Char(string='E15 Number',default=0, required=True,track_visibility='always')

    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
    line_ids = fields.One2many('collection.collection.line','line_id',track_visibility='always', copy=True)

    journal_id = fields.Many2one('account.journal',string='Bank/Cash',track_visibility='always')

    amount = fields.Float(compute='compute_amount', store=True,track_visibility='always')
    amount_in_words = fields.Char(compute='get_amount_in_words',track_visibility='always')
    collection_move_id = fields.Many2one('account.move', copy=False)
    # qr_code = fields.Binary("QR Code", compute="_generate_qr_code", store=False)
    qr_code_str = fields.Char("QR Text")
    qr_code = fields.Binary(string="QR Code", attachment=True, store=True)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('internal_auditor_audit','Internal Auditor Audit')
                              ,('collected','Collected'),('returned_to_collector','Returned To Collector'),('67_issued','67 Issued'),
                              ('67_permited','67 Permited'),('returned_to_supervisor','Returned To Supervisor'),('audited','Audited'),('canceled','Canceled')], default='draft',track_visibility='always')
    budget_item_ids = fields.Many2many('account.analytic.account', compute='get_budget_items',track_visibility='always')
    is_cancel_receipt_e15 = fields.Boolean()
    cancel_e15_state = fields.Selection([('draft','Draft'),
        ('send', 'Send Request'), ('reject', 'Reject Request'),('accept', 'Accepted Request'),('cancel', 'Cancel Request')
    ],default='draft', track_visibility='always')
    cancel_reason = fields.Text(string='Cancel Reason',track_visibility='always')
    returned_reason = fields.Text(string='Cancel Reason',track_visibility='always')
    bank_application_id = fields.Many2one('banking.application',string='Application Name',track_visibility='always')
    transaction_number = fields.Char(string='Transaction Number',track_visibility='always')
    account_number  = fields.Char(string='Acount Number',track_visibility='always')
    is_select_receipt_e15 = fields.Boolean(string="Select Recipt E15")
    is_cancel_accept_e15 = fields.Boolean()
    is_reject_cancle_e15 = fields.Boolean()
    is_unlink_cancel_accept_e15 = fields.Boolean()



    @api.onchange('collection_type')
    def _onchange_collection_type(self):
        if self.collection_type == 'e_bank':
            applications = self.env['banking.application'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ])
            return {
                'domain': {
                    'bank_application_id': [('id', 'in', applications.ids or [0])]
                }
            }
        return {}





    @api.multi
    @api.onchange('bank_application_id')
    def onchange_bank_application_id(self):
        self.account_number = False
        for record in self:
            if record.bank_application_id.account_number:
                record.account_number = record.bank_application_id.account_number

        

    @api.multi
    @api.onchange('collection_type')
    def onchange_collector_id(self):
        for record in self:
            if record.collector_id and record.collection_type:
                collection_ids_list = []
                for collection in self.env['collection.collection'].search([('collector_id','=',record.collector_id.id),('collection_type','=',record.collection_type),('state','=','confirmed')]):
                    collection_ids_list.append( collection.id )
                record.collection_ids = [(6,0, collection_ids_list )]

    @api.multi
    def request_to_cancel_receipt_e_15(self):
        if self.receipt_67_id.state not in ['draft']:
            raise ValidationError(_('لا يمكن ارسالطلب الغاء ايصال  بعد تاكيد 67 الا بعد ارجاعة من المشرف '))
    
    
        if any(rec.cancel_e15_state in ['send','accept'] for rec in self):
            raise ValidationError(_('تم ارسال طلب الغاء الايصال للمشرف مسبقا لايمكن اتمام العملية الا بعدموافقة او رفص المشراف علي الطلب ') )
        self.ensure_one()
        return {
            'name': _('Cancel Receipt E15'),
            'res_model': 'cancel.receipt.e15.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'collection.collection',
                'default_collection_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



    
    @api.multi
    def request_cancel_e15(self):
        for  record in self:
            record.write({'cancel_e15_state': False})
            record.write({'is_cancel_receipt_e15': False})

    
    @api.multi
    def accept_cancel_e15(self):
        for record in self:
            record.write({'cancel_e15_state': 'accept'})
            record.write({'is_cancel_accept_e15': True})

            

    @api.multi
    def cancel_e15(self):
        list_cancel = []
        list = []
        receipt_67_opj = self.env['collection.receipt_67'].search([('collection_ids', '=', self.id)])
        
        for line in receipt_67_opj.collection_ids.filtered(lambda l: l.cancel_e15_state == 'accept'):
            list_cancel.append(line.id)
            receipt_67_opj.write({'collection_ids': [(3, line.id, 0)]})
            self.write({'is_unlink_cancel_accept_e15':True})
            self.write({'state':'canceled'})

        if list_cancel:
            for account_move in self.env['account.move'].search([('collection_id','in',list_cancel)]):
                account_move.button_cancel()
                account_move.unlink()
            
            for line in receipt_67_opj.collection_ids:
                if line:
                    list.append(line.ref)
            if list:
                if len(list) > 1:
                    receipt_67_opj.write({'frist_ref_no' :list[0]})
                    receipt_67_opj.write({'last_ref_no':list[-1]})
                if len(list) == 1:
                    receipt_67_opj.write({'frist_ref_no' :list[0]})
                    receipt_67_opj.write({'last_ref_no':list[0]})
                else:
                    receipt_67_opj.write({'frist_ref_no' : 0.0})
                    receipt_67_opj.write({'last_ref_no': 0.0})

                    


            
            




    @api.multi
    def reject_cancel_e15(self):
        for  record in self:
            record.write({'cancel_e15_state': False})
            record.write({'is_reject_cancle_e15': False})
            record.collection_ids =  False





    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ['draft','canceled']:
                raise ValidationError(_('You Can not delete a Record, witch is not Draft or Canceled'))
            return super(Collection, self).unlink()


    @api.multi
    def do_cancel(self):
        for record in self:
            for account_move in self.env['account.move'].search([('collection_id','=',record.id)]):
                account_move.button_cancel()
                account_move.unlink()
            record.state = 'canceled'

    @api.multi
    @api.onchange('collection_type')
    def onchange_payment_type(self):
        # if self.
        for record in self:

            if record.collection_type == 'bank_transfer':
                # record.check_number = self.env['ir.sequence'].next_by_code( 'bank.transfer.sequence' )
                if record.date:
                    seq_code = 'payment.bank.transfer.sequence.' + str(record.date.year) + '.' + str(record.date.month)
                    seq = self.env['ir.sequence'].next_by_code(seq_code)
                    if not seq:
                        self.env['ir.sequence'].create({
                            'name': seq_code,
                            'code': seq_code,
                            'prefix': str(record.date.year) + '-' + str(record.date.month) + '-',
                            'number_next': 1,
                            'number_increment': 1,
                            'use_date_range': True,
                            'padding': 4,
                        })
                        seq = self.env['ir.sequence'].next_by_code(seq_code)
                    record.check_number = seq

            if record.collection_type == 'cash':
                record.journal_id = False
                return {
                    'domain': {
                        'journal_id': [
                        ('type', 'in', ['cash','bank']) ,('bank_type','=','deposit_bank')]
                    }
                }

            if record.collection_type in ['Cheque', 'bank_transfer', 'counter_cheque','e_bank']:
                record.journal_id = False
                return {
                    'domain': {
                        'journal_id': [('type', '=', 'bank'),('bank_type','=','deposit_bank')]
                        
                    }
                }
        





    @api.multi
    def do_reset_to_draft(self):
        # receipt_67_opj = self.env['collection.receipt_67'].search([('collection_ids', '=', self.id)])
        # if receipt_67_opj.state !=  "draft":
            raise ValidationError(_('لا يمكن إعادة الإيصال إلى حالة المسودة بعد  الموافقة علي طلب الغاء من قبل المشرف'))

        # for record in self:
        #     record.state = 'draft'


    @api.multi
    @api.depends('amount')
    def get_amount_in_words(self):
        for record in self:
            if record.amount:
                record.amount_in_words  = amount_to_text_ar.amount_to_text(record.amount, 'ar')


    @api.multi
    @api.depends('line_ids')
    def compute_amount(self):
        for record in self:
            total = 0
            for line in record.line_ids:
                total = total + line.amount
            record.amount = total




    @api.multi
    @api.depends('line_ids')
    def get_budget_items(self):
        for record in self:
            item_ids = []
            for item in record.line_ids:
                if item.analytic_account_id:
                    item_ids.append(item.analytic_account_id.id)
            record.budget_item_ids = [(6,0, item_ids )]

    @api.model
    def create(self, vals):
     

        create_id =  super(Collection, self).create(vals)

        # duplicate = self.env['collection.collection'].search([
        #         ('collector_id', '=', create_id.collector_id.id)
        #     ], limit=1)
        
        # if duplicate:
        #      self.env.user.notify_warning(
        #             message="تنبيه: يوجد عملية بيع بنفس العميل والمبلغ والتاريخ.",
        #             title="تكرار محتمل",
        #             sticky=True,
        #         )

        


        if len(create_id.line_ids) < 1:
            raise ValidationError(_("يجب اختيار بند واحد على الأقل"))

        
        if create_id and len(create_id.name) > 50:
            raise ValidationError("الرجاء إدخال وصف لا يزيد عن 100 خانة.")
        if create_id.date:
            seq_code = 'revenues.collection.sequence.' + str(create_id.date.year) + '.' + str(create_id.date.month)
            seq = self.env['ir.sequence'].next_by_code( seq_code )
            if not seq:
                self.env['ir.sequence'].create({
                    'name' : seq_code,
                    'code' : seq_code,
                    'prefix' :  str(create_id.date.year) + '-' +  str(create_id.date.month) + '-' ,
                    'number_next' : 1,
                    'number_increment' : 1,
                    'use_date_range' : True,
                    'padding' : 4,
                    })
                seq = self.env['ir.sequence'].next_by_code( seq_code )
            create_id.ref = seq
        return create_id


    @api.multi
    def copy(self):
        raise ValidationError(_('Can not Duplicate This Record, Please create a new Record'))


    @api.multi
    def write(self, vals):
        # if vals.get('name', False):
            # vals['name'] = self.env["ir.fields.converter"].text_from_html(vals['name'], 40, 1000, "...")
        write_id = super(Collection, self).write(vals)
        if vals.get('date', False):
            seq_code = 'revenues.collection.sequence.' + str(self.date.year) + '.' + str(self.date.month)
            seq = self.env['ir.sequence'].next_by_code( seq_code )
            if not seq:
                self.env['ir.sequence'].create({
                    'name' : seq_code,
                    'code' : seq_code,
                    'prefix' :  str(self.date.year) + '-' +  str(self.date.month) + '-' ,
                    'number_next' : 1,
                    'number_increment' : 1,
                    'use_date_range' : True,
                    'padding' : 4,
                    })
                seq = self.env['ir.sequence'].next_by_code( seq_code )
            self.ref = seq
        return write_id

        # q
    def convert_withtimezone(self, userdate):
        """
        Convert to Time-Zone with compare to UTC
        """
        tz_name = self.env.context.get('tz') or self.env.user.tz
        contex_tz = pytz.timezone(tz_name)
        date_time_local = pytz.utc.localize(userdate).astimezone(contex_tz)
        return date_time_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _string_to_hex(self, value):
        if value:
            string = str(value)
            string_bytes = string.encode("UTF-8")
            encoded_hex_value = binascii.hexlify(string_bytes)
            hex_value = encoded_hex_value.decode("UTF-8")
            # print("This : "+value +"is Hex: "+ hex_value)
            return hex_value

    def _get_hex(self, tag, length, value):
        if tag and length and value:
            # str(hex(length))
            hex_string = self._string_to_hex(value)
            length = int(len(hex_string)/2)
            # print("LEN", length, " ", "LEN Hex", hex(length))
            conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
            hexadecimal = ''
            while (length > 0):
                remainder = length % 16
                hexadecimal = conversion_table[remainder] + hexadecimal
                length = length // 16
            # print(hexadecimal)
            if len(hexadecimal) == 1:
                hexadecimal = "0" + hexadecimal
            return tag + hexadecimal + hex_string

        # 



    def get_qr_code_data(self):
        partner = self.partner_id.name
        state = self.state_id.name 
        partner_hex = self._get_hex("02", "0f", partner) or ""
        state_hex = self._get_hex("02", "0f", state) or ""
        time_stamp = str(self.create_date)
        usertime = self.convert_withtimezone(self.create_date)
        date_hex = self._get_hex("03", "14", usertime)
        amount_hex = self._get_hex("04", "0a", str(round(self.amount, 2)))
        qr_hex = partner_hex + state_hex + date_hex + amount_hex
        encoded_base64_bytes = base64.b64encode(bytes.fromhex(qr_hex)).decode()
        return encoded_base64_bytes
    
    @api.onchange('partner_id.name', 'state_id.name', 'amount')

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        str_to_encode = (
                "وصل من: " + (self.partner_id.name or "") + " | "
                "الفرع: " + (self.state_id.name or "") + " | "
                "إجمالي المبلغ: " + "{:,.2f}".format(self.amount) + " SDG | "
                "البيان: " + (self.name or "") + " | "
                "التاريخ: " + (self.date and str(self.date) or ""))
           
        qr.add_data(str_to_encode)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
        







        


    @api.multi
    def get_collector(self):
        for employee in self.env['hr.employee'].search([('user_id','=',self.env.user.id),('company_id','=',self.env.user.company_id.id),('is_collector','=',True)]):
            return employee.id
        return False

    @api.multi
    def get_collector_account(self):
        for employee in self.env['hr.employee'].search([('user_id','=',self.env.user.id),('company_id','=',self.env.user.company_id.id),('is_collector','=',True)]):
            return employee.collector_account_id.id
        return False


    @api.multi
    @api.onchange('collector_id')
    def onchange_collector(self):
        for record in self:
            if record.collector_id:
                record.collector_account_id = record.collector_id.collector_account_id.id








    # @api.multi
    # @api.onchange('collection_type')
    # def onchange_collection_type(self):
    # 	if self.collection_type == 'cash':
    # 		self.journal_id = False
    # 		return {
    # 			'domain' : {
    # 				'journal_id':[('type','=','cash')]
    # 			}
    # 		}
    # 	if self.collection_type in ['Cheque','bank_transfer','counter_cheque']:
    # 		self.journal_id = False
    # 		return {
    # 			'domain' : {
    # 				'journal_id':[('type','=','bank')]
    # 			}
    # 		}



    @api.multi
    def do_confirm(self):

        if self.collection_move_id:
            for account_move in self.env['account.move'].search([('collection_id','=',self.id)]):
                if account_move:
                    account_move.button_cancel()
                    account_move.unlink()
        if self.operation_type in ['subscription','customization']:
            if self.subscription_date_to < self.subscription_date_from:
                raise ValidationError(_('the period dates are not correct!'))

        if not self.line_ids:
            raise ValidationError(_('Please Add Lines!'))
        for line in self.line_ids:
            if line.amount <= 0:
                raise ValidationError(_('Add Amount More than Zero!'))

        if self.e_15_no:
            collector_partner_id = False
            if self.collector_id.user_id:
                if self.collector_id.user_id.commercial_partner_id:
                    collector_partner_id = self.collector_id.user_id.commercial_partner_id.id

            self.create_accounting_enteries(partner_id=collector_partner_id, account_id=self.collector_account_id.id)

            self.state = 'confirmed'

        elif not self.e_15_no:
            for record in self:
                if not record.journal_id.default_debit_account_id.id:
                    raise ValidationError(_('Please Provide Debit Account for the Journal'))
                record.create_accounting_enteries(partner_id=record.partner_id.id, account_id=record.journal_id.default_debit_account_id.id)
                record.state = 'internal_auditor_audit'


    @api.multi
    def do_return_to_collector(self):
        self.state = 'returned_to_collector'


    @api.multi
    def do_audit(self):
        for record in self:
            found = False
            for move in self.env['account.move'].search([('collection_id','=',record.id)]):
                found = True
            if not found:
                if not record.journal_id.default_debit_account_id.id:
                    raise ValidationError(_('Please Provide Debit Account for the Journal'))
                record.create_accounting_enteries(partner_id=record.partner_id.id, account_id=record.journal_id.default_debit_account_id.id)
            record.state = 'collected'


    @api.multi
    def create_accounting_enteries(self, partner_id=False, account_id=False):
        for record in self:

            company_currency = self.company_id.currency_id

            amount = record.amount
            amount_currency = 0
            currency = False
            if record.currency_id != company_currency:
                amount = record.currency_id._convert( record.amount , company_currency, self.company_id, record.date  )
                amount_currency = record.amount
                currency = record.currency_id.id

            total_amount = amount

            move_id = self.create_move(
                ref=record.name,
                journal_id=record.journal_id.id,
                collection_id=self.id,
                employee_id = self.collector_id.id,
                date=record.date)

            for line in record.line_ids:
                tags_list = []
                for tag in line.analytic_tag_ids:
                    tags_list.append( (4, tag.id) )

                amount = line.amount
                amount_currency = 0
                currency = False
                if record.currency_id != company_currency:
                    amount = record.currency_id._convert( line.amount , company_currency, self.company_id, record.date  )
                    amount_currency = line.amount
                    currency = record.currency_id.id

                credit_line = self.create_move_line(
                    name=record.name,
                    partner_id=self.partner_id.id,
                    move_id=move_id.id,
                    account_id=line.account_id.id,
                    credit=line.amount,
                    amount_currency=amount_currency *-1,
                    currency_id=currency,
                    analytic_account_id=line.analytic_account_id.id,
                    analytic_tag_ids = tags_list,
                    cost_center_id=line.cost_center_id.id)

            debit_line = self.create_move_line(
                name=record.name,
                partner_id = self.collector_id.address_id.id,
                move_id=move_id.id,
                account_id=account_id,
                debit=total_amount,
                amount_currency=amount_currency,
                currency_id=currency,
                date=record.date)
            record.collection_move_id = move_id.id
            move_id.post()



    def create_move(self, ref, journal_id,collection_id,employee_id, date=False):
        move = self.env['account.move']
        vals = {
        'ref': ref,
        'journal_id': journal_id,
        'collection_id' : collection_id,
         'employee_id' : employee_id,
        'date' : date,
        'document_number' : self.cheque_number or self.ref,
        }
        return move.create(vals)

    def create_move_line(self, partner_id=False, name=False, move_id=False, account_id=False, debit=False, credit=False, date=False, amount_currency=False, currency_id=False, analytic_account_id=False, analytic_tag_ids=False,cost_center_id=False):
        move_line = self.env['account.move.line']
        vals = {
            'partner_id': partner_id,
            'name': name,
            'move_id': move_id,
            'account_id': account_id,
            'debit': debit,
            'credit': credit,
            'date_maturity' : date,
            'amount_currency' : amount_currency,
            'currency_id' : currency_id,
            'analytic_account_id' : analytic_account_id,
            'analytic_tag_ids': analytic_tag_ids,
            'cost_center_id': cost_center_id,
        }
        return move_line.with_context(check_move_validity=False).create(vals)


    @api.multi
    def show_collection_moves(self):
        return {
            'type' : 'ir.actions.act_window',
            'view_mode' : 'tree,form',
            'res_model' : 'account.move',
            'domain' : [('collection_id','=', self.id )],
        }
    


    @api.constrains('line_ids')
    def _check_lines_amount(self):
        for record in self:
            for line in record.line_ids:
                if line.amount <= 0:
                    raise ValidationError("لا يمكن حفظ السجل إذا كان أحد البنود يحتوي على قيمة صفرية أو سالبة.")


class CollectionLine(models.Model):
    _name = 'collection.collection.line'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']

    branch_id = fields.Many2one('res.company',string='Branch',track_visibility='always',default= lambda self:self.env.user.company_id.id)
    cost_center_id = fields.Many2one('kamil.account.cost.center',string='Cost Center')
    analytic_account_id = fields.Many2one('account.analytic.account',string='Budget Item')
    analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags')
    account_id = fields.Many2one('account.account', string='Account', domain=['|',('code','=ilike','1%'),('code','=ilike','3%'),('is_group','=','sub_account')])
    amount = fields.Float()

    line_id = fields.Many2one('collection.collection',ondelete='cascade')

    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)



    @api.multi
    @api.onchange('account_id')
    def onchnage_account(self):
        for record in self:
            if record.account_id:
                if record.account_id.budget_item_id:
                    record.analytic_account_id = record.account_id.parent_budget_item_id

class Cheque_Bank(models.Model):
    _name = 'cheque.bank'

    name = fields.Char()


class AccountMove(models.Model):
    _inherit = 'account.move'

    collection_id = fields.Many2one('collection.collection')
    employee_id = fields.Many2one('hr.employee',string="Collector ")

    document_number = fields.Char(default='-')