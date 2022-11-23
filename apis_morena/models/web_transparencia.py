import json
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import requests


class WebTransparencia(models.Model):
    _name = 'web.transparencia'
    _description = 'Listado tranparencia'
    _inherit = ['mail.thread']

    name = fields.Char(string="titulo", required=True, track_visibility='onchange')
    Oid = fields.Char(string="Oid", required=True, track_visibility='onchange')
    descripcion = fields.Char(string="Descripcion", required=True, track_visibility='onchange')
    orden = fields.Char(string="Orden")
    image = fields.Char(string="Url Imagen")
    archivo = fields.Char(string="Url archivo")
    date = fields.Datetime(string="Fecha de Publicacion", track_visibility='onchange')
    status = fields.Boolean(string="Activo", required=True, track_visibility='onchange')

    def get_all_tranparencia(self, estado=0):
        datos = self.env["api.custom"].search([('active', '=', True)])
        for rec in datos:
            token = rec.token

            headers = {"Content-Type": "application/json", "Authorization": token}
            query = """
            query { 
              getTransparencia(idEstado: """ + str(estado) + """) { 
                status 
                message 
                transparencia { 
                  FechaActualizacion 
                  Enlaces { 
                    Oid 
                    TituloEnlace 
                    DescripcionEnlace 
                    FechaPublicacionEnlace 
                    OrdenEnlace 
                    UrlimagenEnlace 
                    UrlLinkEnlace 
                    ActivoEnlace 
                  } 
                } 
              } 
            }
                       """
            r = requests.post(url=rec.url, json={'query': query}, headers=headers)
            r.encoding = 'utf-8'
            datos_rec = []
            status = ""
            blog = []
            blogp = self.env["web.transparencia"]
            if r.status_code == 200:
                data = json.loads(r.text)
                status = data['data']['getTransparencia']['status']
                if str(status) == "True":
                    datos_rec = data['data']['getTransparencia']['transparencia']['Enlaces']
                else:
                    token = rec.set_wizard()

                    headers = {"Content-Type": "application/json", "Authorization": token}
                    r = requests.post(url=rec.url, json={'query': query}, headers=headers)
                    data = json.loads(r.text)
                    datos_rec = data['data']['getTransparencia']['transparencia']['Enlaces']
                if datos_rec != None:
                    datos_fil = sorted(datos_rec, key=lambda k: k['FechaPublicacionEnlace'], reverse=True)
                    for noti in datos_fil:
                        url = noti['UrlLinkEnlace']
                        link = ""
                        # if noti['UrlLinkEnlace']:
                        #     if noti['UrlLinkEnlace'] != "#":
                        #         link = "<a href='" + str(noti['UrlLink']) + "' target='_blank'> Mas Información</a>"
                        arb = False
                        if str(noti['ActivoEnlace']) == "True":
                            arb = True

                        bubl = blogp.search([
                            ('Oid', '=', noti['Oid']),
                        ])
                        if bubl:
                            for bp in bubl:
                                # bp['active'] = arb
                                bp['status'] = arb
                                bp['name'] = noti['TituloEnlace']
                                bp['descripcion'] = noti['DescripcionEnlace']
                                bp['image'] = noti['UrlimagenEnlace'] if noti['UrlimagenEnlace'] != " " else ""
                                bp['archivo'] = noti['UrlLinkEnlace'] if noti['UrlLinkEnlace'] != " " else ""
                        else:
                            blogp.create({
                                "name": noti['TituloEnlace'],
                                "Oid": noti['Oid'],
                                "descripcion": noti['DescripcionEnlace'],
                                "orden": noti['OrdenEnlace'],
                                # "is_published": arb,
                                "image": noti['UrlimagenEnlace'] if noti['UrlimagenEnlace'] != " " else "",
                                "archivo": noti['UrlLinkEnlace'] if noti['UrlLinkEnlace'] != " " else "",
                                # "date": datetime.strptime(noti['FechaPublicacionEnlace'], "%Y-%m-%d %H:%M:%S"),
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


