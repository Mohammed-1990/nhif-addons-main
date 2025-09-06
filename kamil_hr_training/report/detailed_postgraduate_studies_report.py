from odoo import models,fields,api
import math

class reportDetailedPostgraduateStudies(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_training.detailed_studies_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []

        employee_id = data['form']['employee_id']
        if employee_id:
            domain.append(('id','=',employee_id))
        
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date_from','>=',date_from))

        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date_to','<=',date_to))

        specialization = data['form']['specialization']
        if specialization:
            domain.append(('specialization','=',specialization))

        country = data['form']['country']
        if country:
            domain.append(('country','=',country))

        university_id = data['form']['university_id']
        if university_id:
            domain.append(('university_id','=',university_id))



        docs = []
        for mission in self.env['study.mission'].search(domain):
            support_type = ''
            support_value = 0.00
            support_type_list = []
            support_amount_list = []
            expenses = self.env['training.expenses'].search([('study_mission','=',mission.id)])
            support_count = 0
            for expense in expenses:
                for line in expense.line_ids:
                    if line.support_type not in support_type_list:
                        support_type_list.append(line.support_type)
            for support in support_type_list:
                total = 0.00
                for expense in expenses:
                    for line in expense.line_ids:
                        if line.support_type.id == support.id:
                            total += line.support_value
                            support_count += 1
                if support_count == 1:
                    support_type = support.name
                    support_value = total
                else:
                    support_amount_list.append({'support_type':support.name,
                        'support_value':total,})

            docs.append({'name':mission.name,
                'specialization':mission.specialization.name,
                'university_id':mission.university_id.name,
                'country':mission.country.name,
                'date_from':mission.date_from,
                'date_to':mission.date_to,
                'branch':mission.employee_id.company_id.name,
                'employee_id':mission.employee_id.name,
                'department_id':mission.department_id.name,
                'functional_id':mission.functional_id.name,
                'support_amount_list':support_amount_list,
                'support_count':support_count,
                'support_type':support_type,
                'support_value':support_value,
                })



       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }