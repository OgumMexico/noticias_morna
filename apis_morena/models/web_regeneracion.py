import json
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import requests

class WebRegeneracion(models.Model):
    _name = 'web.regenracion'
    _description = 'Listado de Regeneraciones de Morena'
    _inherit = ['mail.thread']

    name = fields.Char(string="Titulo", required=True, track_visibility='onchange')
    Oid = fields.Char(string="oid", required=True, track_visibility='onchange')
    descripcion = fields.Char(string="Descripcion", required=True, track_visibility='onchange')
    date = fields.Datetime(string="Fecha de Publicacion", required=True, track_visibility='onchange')
    year = fields.Integer(string="Año Publicacion")
    image = fields.Char(string="Url Imagen", track_visibility='onchange')
    archivo = fields.Char(string="Url archivo", track_visibility='onchange')
    orden = fields.Integer(string="Orden")
    status = fields.Boolean(string="Activo", required=True, track_visibility='onchange')


    def get_all_regenracion(self):
        datos = self.env["api.custom"].search([('active', '=', True)])
        for rec in datos:
            token = rec.token

            headers = {"Content-Type": "application/json", "Authorization": token}
            query = """
               query{ 
                  getAllRegeneracion{ 
                    status 
                    message 
                    regeneracion{ 
                      Oid 
                      TituloRegeneracion 
                      DescripcionRegeneracion 
                      FechaPublicacionRegeneracion 
                      OrdenRegeneracion 
                      UrlimagenRegeneracion 
                      UrlLinkRegeneracion 
                      ActivoRegeneracion 
                    } 
                  } 
                }
                          """
            r = requests.post(url=rec.url, json={'query': query}, headers=headers)
            r.encoding = 'utf-8'
            datos_rec = []
            status = ""
            blog = []
            blogp = self.env["web.regenracion"]
            if r.status_code == 200:
                data = json.loads(r.text)
                status = data['data']['getAllRegeneracion']['status']
                if str(status) == "True":
                    datos_rec = data['data']['getAllRegeneracion']['regeneracion']
                else:
                    token = rec.set_wizard()

                    headers = {"Content-Type": "application/json", "Authorization": token}
                    r = requests.post(url=rec.url, json={'query': query}, headers=headers)
                    data = json.loads(r.text)
                    datos_rec = data['data']['getAllRegeneracion']['regeneracion']
                if datos_rec != None:
                    datos_fil = sorted(datos_rec, key=lambda k: k['FechaPublicacionRegeneracion'], reverse=True)
                    for noti in datos_fil:
                        url = noti['UrlLinkRegeneracion']
                        link = ""
                        # if noti['UrlLinkEnlace']:
                        #     if noti['UrlLinkEnlace'] != "#":
                        #         link = "<a href='" + str(noti['UrlLink']) + "' target='_blank'> Mas Información</a>"
                        arb = False
                        if str(noti['ActivoRegeneracion']) == "True":
                            arb = True

                        bubl = blogp.search([
                            ('Oid', '=', noti['Oid']),
                        ])
                        date = datetime.strptime(noti['FechaPublicacionRegeneracion'], "%Y-%m-%d %H:%M:%S")
                        if bubl:
                            for bp in bubl:
                                # bp['active'] = arb
                                bp['status'] = arb
                                bp['name'] = noti['TituloRegeneracion'] if noti['TituloRegeneracion'] != " " else ""
                                bp['descripcion'] = noti['DescripcionRegeneracion'] if noti['DescripcionRegeneracion'] != " " else ""
                                bp['image'] = noti['UrlimagenRegeneracion'] if noti['UrlimagenRegeneracion'] != " " else ""
                                bp['archivo'] = noti['UrlLinkRegeneracion'] if noti['UrlLinkRegeneracion'] != " " else ""
                                bp['date'] = date
                                bp['year'] = date.year
                        else:

                            blogp.create({
                                "name": noti['TituloRegeneracion'] if noti['TituloRegeneracion'] != " " else "",
                                "Oid": noti['Oid'],
                                "descripcion": noti['DescripcionRegeneracion'] if noti['DescripcionRegeneracion'] != " " else "",
                                "orden": noti['OrdenRegeneracion'] if noti['OrdenRegeneracion'] != " " else "",
                                # "is_published": arb,
                                "image": noti['UrlimagenRegeneracion'] if noti['UrlimagenRegeneracion'] != " " else "",
                                "archivo": noti['UrlLinkRegeneracion'] if noti['UrlLinkRegeneracion'] != " " else "",
                                "date": date,
                                "year": date.year,
                                "status": arb,
                            })

                # if blog != None:
                #     self.write1(blog)

                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': str(token),
                        'message': str(blog),
                        'type': 'success',  # types: success,warning,danger,info
                        'sticky': True,  # True/False will display for few seconds if false
                    },
                }
                return notification

