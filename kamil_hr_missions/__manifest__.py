#App-Script business Solution
#    Copyright (C) 2017-2020 app-script (<http://www.app-script.com>).
{
	'name' : 'kamil HR - Missions',
	'version' : '0.1',
	'author' : 'AlmedTech',
	'category' : 'hr',
	'summary' : """
		Employee missions, 
	""",

	'depends' : ['hr','kamil_hr_benefits_wages','html_text'],
	'data': [
		# 'security/security.xml',
		'security/ir.model.access.csv',
		'security/security_view.xml',
		'sequences/sequence.xml',
        'views/hr_missions.xml',
        'report/missions_assigned_report.xml',
        'report/mission_allowance.xml',
        'report/mission_petty.xml',
		
	],

	'installable': True,
	'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
