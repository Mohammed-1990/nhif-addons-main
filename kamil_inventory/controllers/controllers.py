# -*- coding: utf-8 -*-
from odoo import http

# class PlainModule(http.Controller):
#     @http.route('/plain_module/plain_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plain_module/plain_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plain_module.listing', {
#             'root': '/plain_module/plain_module',
#             'objects': http.request.env['plain_module.plain_module'].search([]),
#         })

#     @http.route('/plain_module/plain_module/objects/<model("plain_module.plain_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plain_module.object', {
#             'object': obj
#         })