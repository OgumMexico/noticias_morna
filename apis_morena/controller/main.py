import json

from odoo import http
from odoo.http import request


class ModelName(http.Controller):

    @http.route(['/regeneracion'], type="http", auth="public", website=True)
    def set_regeneracion(self):
        data = request.env['web.regenracion'].sudo().search([("status", "=", True)])
        datos_filv1 = sorted(data, key=lambda k: k.date, reverse=True)

        values = set(map(lambda x: x['year'], data))
        newlist = {x: [y for y in data if y['year'] == x] for x in values}
        datos_fil = sorted(newlist, reverse=True)

        dat = {
            "datas": datos_fil,
            "row": datos_filv1,
        }

        return request.render('apis_morena.web_regeneracion_pub', dat)

    @http.route(['/directorio'], type="http", auth="public", website=True)
    def set_directorio(self):
        data = request.env['web.directorio'].sudo().search([("status", "=", True)])
        datos_filv1 = sorted(data, key=lambda k: k.orden)

        dat = {
            "row": datos_filv1,
        }

        return request.render('apis_morena.web_directorio_pub', dat)

    @http.route(['/trasparencia'], type="http", auth="public", website=True)
    def set_trasparencia(self):
        data = request.env['web.transparencia'].sudo().search([("status", "=", True)])
        # datos_filv1 = sorted(data, key=lambda k: k.date, reverse=True)

        dat = {
            "row": data,
        }

        return request.render('apis_morena.web_trasparencia_pub', dat)


