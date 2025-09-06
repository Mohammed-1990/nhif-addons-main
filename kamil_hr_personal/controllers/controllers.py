# -*- coding: utf-8 -*-
from odoo import http

# class KamilHrPersonal(http.Controller):
#     @http.route('/kamil_hr_personal/kamil_hr_personal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kamil_hr_personal/kamil_hr_personal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kamil_hr_personal.listing', {
#             'root': '/kamil_hr_personal/kamil_hr_personal',
#             'objects': http.request.env['kamil_hr_personal.kamil_hr_personal'].search([]),
#         })

#     @http.route('/kamil_hr_personal/kamil_hr_personal/objects/<model("kamil_hr_personal.kamil_hr_personal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kamil_hr_personal.object', {
#             'object': obj
#         })