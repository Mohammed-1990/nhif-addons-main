# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)
class KamilContractClaims(models.Model):
    _name = 'contract.claims'
    _description = 'Contract claim'
    _order = 'id desc'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']



    name = fields.Char(string='Name', readonly=True, track_visibility="always", default='New') #lambda self: self._get_next_claimname(), store=True, readonly=True)
    reference = fields.Many2one('kamil.contracts.contract', string='Contract', required="1", track_visibility="always", domain="[('state', '=', 'open')]")
    # contractor = fields.Char(string='Contractor', default=lambda self: self._ge_contractor(), track_visibility="always", domain="[('state', '=', 'open')]")
    date = fields.Date(string='Claim Date', default=datetime.today().date(), track_visibility="always")
    # claim_ids = fields.Many2one('kamil.contracts_waypay',ondelete='cascade', string='Payment')
    # claim_ids = fields.Many2many('kamil.contracts_waypay', related='reference.payment_mode_ids', track_visibility="always")
    penalty_ids = fields.One2many('kamil.contracts.panalty_lines','contract_id', related='reference.panalty_ids', track_visibility="always")
    subject = fields.Char(string='Subject', track_visibility="always")
    body = fields.Html(track_visibility="always")
    attachment = fields.Binary(string='Attachment', track_visibility="always")
    file_name = fields.Char(string='File', track_visibility="always")
    penalties = fields.Many2many('kamil.contracts.panalty_lines',string='Penalties', track_visibility="always")
    total_penalties=fields.Float(string='Total of Panalties', track_visibility="always",default=0)
    
    claims = fields.Many2many('kamil.contracts_waypay',string='Claims',domain="[('status_sel','=','n')]", track_visibility="always")
    state = fields.Selection([
        ('draft', 'Draft')
        , ('submit', 'Submit')
        ,('approved','Approved')
        ,('invoice','Invoice Created')
        ,('cancel', 'Canceld'),],string="State",default='draft', track_visibility="always")
    total_claim = fields.Float(string='Total of Claim', track_visibility="always")
    invoice = fields.Many2one('ratification.ratification', track_visibility="always")
    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)


    _rec_name = 'name'

    # @api.model
    # def _get_next_purchasename(self):
    #     sequence = self.env['ir.sequence'].search([('code','=','claim.req')])

    #     next= sequence.get_next_char(sequence.number_next_actual)

    #     return next

    @api.model
    def create(self, values):                
        # values['name'] = self.env['ir.sequence'].get('kamil.contracts.claim.req') 
        if self.name == 'New':
                seq_code = 'claim.req' 
                seq = self.env['ir.sequence'].next_by_code( seq_code )
                if not seq:
                    self.env['ir.sequence'].create({
                        'name' : seq_code,
                        'code' : seq_code,
                        'prefix' : 'Claim-',
                        'number_next' : 1,
                        'number_increment' : 1,
                        'use_date_range' : True,
                        'padding' : 4,
                        })
                seq = self.env['ir.sequence'].next_by_code( seq_code )
                self.name = seq

        # if values.get('name', 'New') == 'New':
        #     sequence = self.env['ir.sequence'].search([('code','=','kamil_contracts.claim.req')])
        #     next= sequence.get_next_char(sequence.number_next_actual)
        #     # values['name'] = self.env['ir.sequence'].sudo().next_by_code('claim.req') or 'New'
            

        total_penalti = 0
        total_claims = 0
        for penalti in self.penalties:
            total_penalti += penalti.total_penalty
            # penalti.write({'status_sel':'i'})
        for claim in self.claims:
            total_claims += claim.claim_amount
            # claim.write({'status_sel':'i'})
        # raise ValidationError(self.claims)
        grand_total = total_claims - total_penalti

        values['total_claim'] = grand_total
        values['total_penalties']=total_penalti
      

        return super(KamilContractClaims, self).create(values)

    # @api.one
    # def _ge_contractor(self):
    #     if self.reference:
    #         self.contractor = self.reference.second_party_name
    #     raise ValidationError(_(self.reference))
    @api.multi
    @api.onchange('claims')
    def onchange_claim_amount(self):
        
        total_penalti = 0
        total_claims = 0
        for penalti in self.penalties:
            total_penalti += penalti.total_penalty
            # penalti.write({'status_sel':'i'})
        for claim in self.claims:
            total_claims += claim.claim_amount
            # claim.write({'status_sel':'i'})
        # raise ValidationError(total_claims)
        grand_total = total_claims - total_penalti
        self.total_claim=grand_total
        self.write({'total_claim': grand_total})  

    @api.multi
    @api.onchange('reference')
    def onchange_contract_id(self):
        if self.reference:
            # self.contractor = self.reference.second_party_name.name
            # for line in self.reference.payment_mode_ids:
                # print("line::",line,"\n\n\n")
                # _logger.debug('Create a %s :::', line)
                # self.claims = line
            self.claims = self.reference.payment_mode_ids.search([('status_sel','in',['n','p','i']),('contract_id','=',self.reference.id)])

            for line in self.reference.payment_mode_ids:
                line.claim_amount = line.pay_balance
        # Get Panaalties #
        penalty_list = []
        amount=0
        # print ("self.claims::",self.claims,"\n\n")
        
        for penalty in self.penalty_ids:
            if penalty.is_active:
                if penalty.panalty_basis =='cont_per':
                    # print ("penalty.panalty_basis ::",penalty.panalty_basis ,"\n\n")

                    if penalty.affect_date < self.date:
                        delta = self.date - penalty.affect_date
                        days = delta.days                             
                        
                        if penalty.frequency =='onetime':
                            print ("penalty.frequency ::",penalty.frequency ,"\n\n")
                            amount = self.reference.contract_amount * (penalty.percentage ) /100
                            # raise ValidationError(_(amount))
                        else:                            
                            
                                # raise ValidationError(days)
                                amount = days * (self.reference.contract_amount *penalty.percentage /100)
                    else:
                        days=0
                else:
                     if penalty.affect_date < self.date:
                        delta = self.date - penalty.affect_date
                        days = delta.days                             
                        
                        if penalty.frequency =='onetime':
                            amount = (penalty.panalty_amount )
                            # raise ValidationError(_(amount))
                        else:                            
                            
                                # raise ValidationError(days)
                                amount = days * (penalty.panalty_amount)

                penalty.write({'difference': days, 'total_penalty': amount})
                penalty_list.append(penalty.id)
        self.update({'penalties':[(6,0,penalty_list)]})
        # print ("End of change of claims::\n\n")
        # total_penalti = 0
        # total_claims = 0
        # for penalti in self.penalties:
        #     total_penalti += penalti.total_penalty
        #     # penalti.write({'status_sel':'i'})
        # for claim in self.claims:
        #     total_claims += claim.claim_amount
        #     # claim.write({'status_sel':'i'})
        # grand_total = total_claims - total_penalti
        # self.total_claim=grand_total

        if self.reference and not len(self.claims):
            raise ValidationError('عفوا لاتوجد مطالبة لهذا العقد: الرجاء التاكد من صفحة المطالبات  اسفل العقد')
        

    @api.multi
    def action_submit(self):
        

        for record in self:
            for rec in record.claims:
                rec.pay_applied_amount+=rec.claim_amount
                rec.pay_balance = rec.phase_amount - rec.pay_applied_amount    
                if rec.pay_applied_amount:
                    rec.execu_percentage = rec.pay_applied_amount / rec.phase_amount * 100
        
        # raise ValidationError(self.claims)
        total_penalti = 0
        total_claims = 0
        for penalti in self.penalties:
            total_penalti += penalti.total_penalty
        # raise ValidationError(total_penalti)
            # penalti.write({'status_sel':'i'})
        for claim in self.claims:
            total_claims += claim.claim_amount
            # claim.write({'status_sel':'i'})
        # raise ValidationError(total_claims)
        # raise ValidationError(total_claims)
        grand_total = total_claims - total_penalti
        self.total_claim=grand_total     
        # raise ValidationError(self.total_claim)
        self.write({'total_claim': grand_total})   
        self.write({'penalties': self.penalties})   
        self.write({'total_penalties': total_penalti})  
        print ("\n\n total_penalties::",total_penalti,"\n\n")
        
        if not len(self.claims):
            raise ValidationError('عفوا لاتوجد مطالبة لهذا العقد: الرجاء التاكد من صفحة المطالبات  اسفل العقد')
        elif(self.total_claim <=0):
            raise ValidationError('Claim cannot be less than or equal Zero')
        self.write({'state':'submit'})


    @api.multi
    def action_approve(self):
        self.write({'state':'approved'})

    @api.multi
    def cancel(self):
        self.write({'state':'cancel'})
        for record in self:
            for rec in record.claims:
                rec.pay_applied_amount-=rec.claim_amount
                rec.pay_balance -= rec.claim_amount
                if rec.pay_applied_amount:
                    rec.execu_percentage = rec.pay_applied_amount / rec.phase_amount * 100
    
    @api.multi
    def senttodraft(self):
        self.write({'state':'draft'})
        for record in self:
            for rec in record.claims:
                rec.pay_applied_amount-=rec.claim_amount
                rec.pay_balance -= rec.claim_amount
                if rec.pay_applied_amount:
                    rec.execu_percentage = rec.pay_applied_amount / rec.phase_amount * 100
    
                

    @api.multi
    def button_invoice(self):
        return {
        'name': ('Vendor Bills - Contract Claims'),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'ratification.ratification',
        'res_id': self.invoice.id,
        'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_create_invoice(self):
        journal = self.env['account.journal'].search([('name','ilike','BILL')])
        product = self.env['product.product'].search([('name','ilike','CONTRACT CLAIM')])
        # if not product:
        #     raise ValidationError('Please create a product named "CONTRACT CLAIM" and then continue to create Invoice')
        # if not product.product_tmpl_id.property_account_income_id:
        #     raise ValidationError('Please assign an account to Income Account of the product "CONTRACT CLAIM" and then continue to create Invoice')

        

        user = self.env.user.id
        user_id = self.env['res.users'].browse(user)
        
        total_claims=0
        for claim in self.claims:
            total_claims += claim.claim_amount
        
        # ratification_line_id = {
        # 'partner_id': self.reference.second_party_ch.id,
        # 'state_id': user_id.company_id.id,
        # 'date': datetime.now().date(),
        # 'payment_type': 'Cheque',
        # 'name':self.reference.name+ '-' + 'Contract Claim',
        # 'amount':total_claims
        # # ,'net_amount':self.total_claim,

        # }

        # ratification = self.env['ratification.ratification'].create(ratification_line_id)


        acc=0
        an_id=0
        acc_code=0
        tax=0
        for acc_id in self.env['kamil.contracts.account_setting'].search([('company_id','=',self.env.user.company_id.id)],limit=1):
            acc=acc_id.account_id
            stamp=acc_id.stamp

        
        ratification = self.env['ratification.ratification'].create({
            'partner_id':self.reference.second_party_ch.id,
            'state_id':user_id.company_id.id,
            'ratification_type':'salaries_and_benefits',
            'name':self.reference.name+ '-' + 'Contract Claim',
            'amount':total_claims,
            'date': datetime.now().date(),
            'payment_type': 'Cheque',
            'deduction_ids':[{'tax_id':stamp.id,'name':stamp.name,'amount':self.total_penalties}]
            })

        

        ratification.line_ids = [{'name':self.reference.name,
        'amount':total_claims,
        'account_id':acc,
        'ratification_id':ratification.id,
        'deduction_ids':[{'tax_id':stamp.id,'name':stamp.name,'amount':self.total_penalties}]}]

        print("\n\n\n self.total_penalties::",self.total_penalties,"\n\n\n")

        ratification.tax_ids = [{
        'name':stamp.name,
        'tax_id':stamp.id,
        'amount':self.total_penalties,
        'ratification_id':ratification.id,}]



        for ids in self.claims:
            if ids.pay_balance==0:
              ids.write({'status_sel': 'f'}) # Fully paid
            else:
              ids.write({'status_sel': 'p'}) # Partially paid
        
        self.write({'invoice':ratification.id, 'state':'invoice'})

        


class KamilProductTemplate(models.Model):
    _inherit = 'product.template'

    budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item', track_visibility="always")


class KamilStockLocation(models.Model):
    _inherit = 'stock.location'


    account_id = fields.Many2one('account.account', string='Stock Account', track_visibility="always")


class KamilProductCategory(models.Model):
    _inherit = 'product.category'

    budget_item_id = fields.Many2one('account.analytic.account', string='Budget Item', track_visibility="always")

class KamilResCompany(models.Model):
    _inherit = 'res.company'

    social_facebook = fields.Char()
    social_twitter = fields.Char()
    social_linkedin = fields.Char()
    social_instagram = fields.Char()
    social_github = fields.Char()
    social_youtube = fields.Char()
    social_googleplus = fields.Char()


