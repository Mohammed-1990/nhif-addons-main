from odoo import models,fields,api
import math

class ReportTotalExecuted(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """
    _name = 'report.kamil_hr_training.total_executed_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        date_from = data['form']['date_from']
        if date_from:
            domain.append(('date_from','>=',date_from))

        date_to = data['form']['date_to']
        if date_to:
            domain.append(('date_to','<=',date_to))

        training_type = data['form']['training_type']
        if training_type:
            domain.append(('training_type','=',training_type))

        country = data['form']['country']
        if country:
            domain.append(('country','=',country))
    
        programs = self.env['program.execution'].search(domain)

        internal_program = []
        external_program = []
        training_type_list = []
        for program in programs:
            if program.training_type not in training_type_list:
                training_type_list.append(program.training_type)
        
        total_programs_internal = 0
        total_participants_internal = 0   
        total_programs_external = 0
        total_participants_external = 0 
              
        for type in training_type_list:
            total_programs = 0
            total_participants = 0
            for program in programs:
                if program.program_type == 'internal' and program.training_type.id == type.id:
                    total_programs += 1
                    for line in program.line_ids:
                        total_participants += 1
            if total_programs != 0 and total_participants != 0:
                total_programs_internal += total_programs
                total_participants_internal += total_participants
                internal_program.append({'type':type.name,
                    'total_programs':total_programs,
                    'total_participants':total_participants,
                    })
        internal_program.append({'type':"الإجمالي",
                    'total_programs':total_programs_internal,
                    'total_participants':total_participants_internal,
                    })
        for type in training_type_list:
            total_programs = 0
            total_participants = 0
            for program in programs:
                if program.program_type == 'external' and program.training_type.id == type.id:
                    total_programs += 1
                    for line in program.line_ids:
                        total_participants += 1
            if total_programs != 0 and total_participants != 0:
                total_programs_external += total_programs
                total_participants_external += total_participants
                external_program.append({'type':type.name,
                    'total_programs':total_programs,
                    'total_participants':total_participants,
                    })
        external_program.append({'type':"الإجمالي",
            'total_programs':total_programs_external,
            'total_participants':total_participants_external,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'internal_program': internal_program,
            'external_program':external_program,
        }