# -*- coding: utf-8 -*-
from odoo import http

# class Hr(http.Controller):
#     @http.route('/hr/hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr/hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr.listing', {
#             'root': '/hr/hr',
#             'objects': http.request.env['hr.hr'].search([]),
#         })

#     @http.route('/hr/hr/objects/<model("hr.hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr.object', {
#             'object': obj
#         })