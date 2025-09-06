from odoo import models,fields,api
import math

class reportBriefPostgraduateStudies(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.kamil_hr_training.brief_postgraduate_studies_report_view'

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

        TheProgram = self.env['study.mission'].search(domain)

        docs = []
        for mission in self.env['study.mission'].search(domain):
                    docs.append({'name':mission.name,
                        'specialization':mission.specialization.name,
                        'university_id':mission.university_id.name,
                        'country':mission.country.name,
                        'date_from':mission.date_from,
                        'date_to':mission.date_to,
                        # 'city_id':mission.city_id,
                        'employee_id':mission.employee_id.name,
                        'department_id':mission.department_id.name,
                        'functional_id':mission.functional_id.name,


                        })



       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }