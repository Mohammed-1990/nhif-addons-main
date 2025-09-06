# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta , datetime 
from dateutil.relativedelta import relativedelta

class KamilContractsProjectExtensionRequest(models.Model):
    _name = 'kamil.contracts.extensions'
    _description = 'Contract Extension'
    _order = 'id desc'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
    # _inherit = ['mail.thread','mail.activity.mixin']    
    

    training_state = fields.Selection([
        ('training_none', 'None'),
        ('training_draft', 'Draft'),
        ('training_submit', 'Submit'),
        ('training_executive_director', 'Executive Director'), 
        ('training_gm', 'GM'), 
        ('training_department', 'Training Department'),         
        ('training_legal_affairs', 'Legal Affairs'), 
        ('training_done', 'Extended'), 
        ('training_reject', 'Reject'), 
        ], 'Status', readonly=True, copy=False, required=True, default='training_none', track_visibility="always", inverse='update_status')        

    service_state = fields.Selection([
        ('service_none', 'None'),
        ('service_draft', 'Draft'),
        ('service_submit', 'Submit'),
        ('service_executive_director', 'Executive Director'), 
        ('service_gm', 'GM'),         
        ('service_department', 'Purchase Department'),         
        ('service_legal_affairs', 'Legal Affairs'), 
        ('service_done', 'Extended'), 
        ('service_reject', 'Reject'), 
        ], 'Status', readonly=True, copy=False, required=True, default='service_none', track_visibility="always", inverse='update_status')        

    purchase_state = fields.Selection([
        ('purchase_none', 'None'),
        ('purchase_draft', 'Draft'),
        ('purchase_submit', 'Submit'),
        ('purchase_executive_director', 'Executive Director'), 
        ('purchase_gm', 'GM'),         
        ('purchase_department', 'Purchase Department'),         
        ('purchase_legal_affairs', 'Legal Affairs'), 
        ('purchase_done', 'Extended'), 
        ('purchase_reject', 'Reject'), 
        ], 'Status', readonly=True, copy=False, required=True, default='purchase_none', track_visibility="always", inverse='update_status')        

    research_state = fields.Selection([
        ('research_none', 'None'),
        ('research_draft', 'Draft'),
        ('research_submit', 'Submit'),
        ('research_department', 'Research department'),        
        ('head_of_commitee', 'Head of commitee'), 
        ('research_done', 'Extended'), 
        ('research_reject', 'Reject'), 

        ], 'Status', readonly=1, copy=False, required=True, default='research_none', track_visibility="always", inverse='update_status')
    
    name = fields.Char('Name', track_visibility="always", readonly=True, required=True, copy=False, default='New')
    status=fields.Char('Status', track_visibility="always")
    application_date= fields.Date('Application Date', default=lambda self: fields.Date.today(), track_visibility="always")
    contract_id = fields.Many2one('kamil.contracts.contract','Reffrence', required=True, inverse='track_change_state')
    # administration_concerned = fields.Selection([('purchase_management','Purchase Management'),('administrative_affairs','Administrative Affairs'),('planning_department','Planning Department')])
    subject = fields.Char('Subject', track_visibility="always")
    the_body_of_the_message = fields.Html(track_visibility="always")    
    applicant = fields.Many2one('res.users',string='Applicant Name', required=True, default= lambda self: self.env.user, track_visibility="always")
    # adjective = fields.Many2one('hr.function',related='applicant.functional_id', readonly=True)
    # check_contract_typefields.Boolean(string="Journal Type",  default=False)

    contract_type=fields.Char(related='contract_id.contract_type')
    

    period_name = fields.Selection([('w', 'Weeks/s'),('m', 'Month/s'), ('y', 'Year/s')], default="m", required=True, track_visibility="always")
    period = fields.Selection([('1', '1'), ('2', '2'),('3','3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')],string="Period ", required=True, track_visibility="always")
  

    # attachment_ids= fields.many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Attachments')

    # attachment_ids = fields.Many2one('kamil.contracts.attachments', track_visibility="always")
    # attachment_ids = fields.Many2one('kamil.contracts.attachments','rel_kamil_contracts_contract_kamil_contracts_attachments','attachment_id',string='Attachment', track_visibility="always")
    # attachment_ids = fields.Many2many('kamil.contracts.attachments','attachment_id',string='Attachment', track_visibility="always")
    attachment_ids = fields.One2many('kamil.contracts.extension.attachments','attachment_id',string='Attachment', track_visibility="always")
    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id)
    # state = fields.Selection([('draft', 'Draft'),('submit', 'Submit'),('done', 'Done'),('cancel', 'Canceld'), ], 'Status', readonly=True, copy=False, required=True, default='draft', track_visibility="always")

    # @api.multi
    # @api.onchange('applicant')
    # def onchnage_applicant(self):
    #     if self.applicant:
    #         self.adjective = self.applicant.job_id.id

    def track_change_state(self):
        
        if self.contract_type=='Goods' and self.purchase_state=='purchase_none':
            self.training_state='training_none'
            self.research_state='research_none'
            self.purchase_state='purchase_draft'
            self.service_state='service_none'

        elif self.contract_type=='Service' and self.service_state=='service_none':
            self.training_state='training_none'
            self.research_state='research_none'
            self.purchase_state='purchase_none'
            self.service_state='service_draft'
            
            # print("training_state:::::::::",self.training_state,"::::::::::::::::\n\n\n\n\n\n\n\n\n\n\n")
        elif self.contract_type=='Training' and self.training_state=='training_none':
            self.training_state='training_draft'
            self.research_state='research_none'
            self.purchase_state='purchase_none'
            self.service_state='service_none'
        
        elif self.contract_type=='Research' and self.research_state=='research_none':
            self.training_state='training_none'
            self.research_state='research_draft'
            self.purchase_state='purchase_none'
            self.service_state='service_none'
        # self.name=self.ext_of+self.contract_id.name
        # print "Research cont type training_state:::::::::",self.training_state,"::::::::::::::::\n"
        # print "Research cont type purchase_state:::::::::",self.purchase_state,"::::::::::::::::\n"
        # print "Research cont type research_state:::::::::",self.research_state,"::::::::::::::::\n\n\n\n\n\n\n\n\n\n\n"

        # print("training_state::",self.training_state,"research_state",self.research_state,"\n\n")
    @api.multi
    def update_status(self):
        for rec in self:
            if self.contract_type =='Goods':
                rec.write({'status':dict(self._fields['purchase_state'].selection).get(self.purchase_state)}) 

            elif self.contract_type =='Service':
                rec.write({'status':dict(self._fields['service_state'].selection).get(self.service_state)}) 

            elif self.contract_type =='Research':
                rec.write({'status':dict(self._fields['research_state'].selection).get(self.research_state)}) 

            elif self.contract_type =='Training':
                rec.write({'status':dict(self._fields['training_state'].selection).get(self.training_state)}) 


    @api.multi
    def purchase_submit(self):
        for rec in self:
            
            rec.write({'purchase_state': 'purchase_submit'})  

    @api.multi
    def service_submit(self):
        for rec in self:
            
            rec.write({'service_state': 'service_submit'})  


    # @api.multi
    # def purchase_submit(self):
    #     for rec in self:
            
    #         rec.write({'purchase_state': 'purchase_submit'})    
    
    # @api.multi
    # def service_draft(self):
    #     for rec in self:
            
    #         rec.write({'service_state': 'service_draft'})    
                

    @api.multi
    def training_draft(self):
        for rec in self:
            
            rec.write({'training_state': 'training_draft'})


    # @api.multi
    def training_submit(self):
        for rec in self:
            
            rec.write({'training_state': 'training_executive_director'})     


    @api.multi
    def training_executive_director(self):
        for rec in self:
            
            rec.write({'training_state': 'training_executive_director'})
            # print "training_submit:::"
    
    @api.multi
    def training_gm(self):
        for rec in self:
            rec.write({'training_state': 'training_gm'})

    @api.multi
    def training_legal_affairs(self):
        for rec in self:
            rec.write({'training_state': 'training_legal_affairs'})

    @api.multi
    def training_done(self):
        for rec in self:          
            rec.write({'training_state': 'training_done'})   

        if self.period_name=="w":
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(weeks=int(self.period) ) 

        if self.period_name=='m':
            # print ("\n\n\n","self.period::",self.period,"\n\n\n")
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(months=int(self.period) )
        
        if self.period_name=='y':
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(years=int(self.period) )
   

    @api.multi
    def training_reject(self):
        for rec in self:          
            rec.write({'training_state': 'training_reject'})
     



    @api.multi
    def research_submit(self):
        for rec in self:
            
            rec.write({'research_state': 'research_department'})      

    @api.multi
    def head_of_commitee(self):
        for rec in self:
            print ('contract_type:::',self.contract_id.contract_type,'\n\n\n')
            print ('self.contract_type',self.contract_type,'\n\n')
            self.contract_type=self.contract_id.contract_type
            rec.write({'research_state': 'head_of_commitee'})      

    @api.multi
    def research_done(self):
        for rec in self:                
            rec.write({'research_state': 'research_done'})      

        if self.period_name=="w":
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(weeks=int(self.period) ) 

        if self.period_name=='m':
            print ("\n\n\n","self.period::",self.period,"\n\n\n")
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(months=int(self.period) )
        
        if self.period_name=='y':
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(years=int(self.period) )

    # @api.multi
    # def research_reject(self):
    #     for rec in self:                
    #         rec.write({'research_state': 'research_reject'})  

    @api.multi
    def purchase_executive_director(self):
        for rec in self:
            print ('contract_type:::',self.contract_id.contract_type,'\n\n\n')
            print ('self.contract_type',self.contract_type,'\n\n')
            self.contract_type=self.contract_id.contract_type
            
            
            rec.write({'purchase_state': 'purchase_executive_director'})      
    
    @api.multi
    def service_executive_director(self):
        for rec in self:
            print ('contract_type:::',self.contract_id.contract_type,'\n\n\n')
            print ('self.contract_type',self.contract_type,'\n\n')
            self.contract_type=self.contract_id.contract_type
            
            
            rec.write({'service_state': 'service_executive_director'})      



    @api.multi
    def purchase_gm(self):
        for rec in self:    
            rec.write({'purchase_state': 'purchase_gm'})      

    @api.multi
    def service_gm(self):
        for rec in self:    
            rec.write({'service_state': 'service_gm'})      



    @api.multi
    def training_department(self):
        for rec in self:
            rec.write({'training_state': 'training_department'})   
            
               

    @api.multi
    def purchase_department(self):
        for rec in self:
            

            rec.write({'purchase_state': 'purchase_department'})      


    @api.multi
    def service_department(self):
        for rec in self:
            
            rec.write({'service_state': 'service_department'})      

    @api.multi
    def research_department(self):
        for rec in self:
            rec.write({'research_state': 'research_department'})            

         
    @api.multi
    def purchase_legal_affairs(self):
        for rec in self:
            rec.write({'purchase_state': 'purchase_legal_affairs'})      

    @api.multi
    def service_legal_affairs(self):
        for rec in self:
            rec.write({'service_state': 'service_legal_affairs'})      
 

    @api.multi
    def training_cancel(self):
        for rec in self:
            rec.write({'training_state': 'training_cancel'})      
            

 
    @api.multi
    def purchase_cancel(self):
        for rec in self:
            rec.write({'purchase_state': 'purchase_cancel'})     
    
    @api.multi
    def service_cancel(self):
        for rec in self:
            rec.write({'service_state': 'service_cancel'})     
                 
 

    @api.multi
    def research_cancel(self):
        for rec in self:     
            rec.write({'research_state': 'research_cancel'})       
 


    @api.multi
    def purchase_done(self):
        for rec in self:               
            rec.write({'purchase_state': 'purchase_done'})      

        if self.period_name=="w":
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(weeks=int(self.period) ) 

        if self.period_name=='m':
            print ("\n\n\n","self.period::",self.period,"\n\n\n")
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(months=int(self.period) )
        
        if self.period_name=='y':
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(years=int(self.period) )

    @api.multi
    def service_done(self):
        for rec in self:               
            rec.write({'service_state': 'service_done'})      

        if self.period_name=="w":
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(weeks=int(self.period) ) 

        if self.period_name=='m':
            print ("\n\n\n","self.period::",self.period,"\n\n\n")
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(months=int(self.period) )
        
        if self.period_name=='y':
            self.contract_id.contract_end_date=self.contract_id.contract_end_date + relativedelta(years=int(self.period) )

    
    @api.multi
    def research_reject(self):
        for rec in self:               
            rec.write({'research_state': 'research_reject'})

    @api.multi
    def purchase_reject(self):
        for rec in self:               
            rec.write({'purchase_state': 'purchase_reject'})

    @api.multi
    def service_reject(self):
        for rec in self:               
            rec.write({'service_state': 'service_reject'})

    @api.multi
    def training_reject(self):
        for rec in self:               
            rec.write({'training_state': 'training_reject'})
    
    # @api.multi
    # @api.depends('contract_type')
    # def _check_contract_type(self):
    #     if self.contract_type == 'Purchase':
    #         self.check_contract_type = False
    #     else:
    #         self.check_contract_type = False

    @api.model
    def create(self, values):        
        values['name'] = self.env['ir.sequence'].get('kamil.contracts.extension.req') or ' ' 
        return super(KamilContractsProjectExtensionRequest, self).create(values)


class kamilContractAttachments(models.Model):
    _name = 'kamil.contracts.extension.attachments'
    
    
    attachment_name = fields.Char(string='Attachment Name', required=True, track_visibility="always")
    attachment_id =fields.Many2one('kamil.contracts.extensions', track_visibility="always", ondelete='restrict')
    attachment = fields.Binary( track_visibility="always")
