import json
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import requests

class WebDirectorio(models.Model):
    _name = 'web.directorio'
    _description = 'Listado del directorio por estado'
    _inherit = ['mail.thread']

    name = fields.Char(string="Nombre Completo", required=True, track_visibility='onchange')
    Oid = fields.Char(string="Oid", required=True, track_visibility='onchange')
    cargo = fields.Char(string="Cargo",  track_visibility='onchange')
    titulo = fields.Char(string="Titulo", track_visibility='onchange')
    telefono = fields.Char(string="Telefono", track_visibility='onchange')
    correo = fields.Char(string="Correo", track_visibility='onchange')
    perfil = fields.Char(string="Perfil", track_visibility='onchange')
    face = fields.Char(string="Facebook", track_visibility='onchange')
    twit = fields.Char(string="Twitter", track_visibility='onchange')
    insta = fields.Char(string="Instagram", track_visibility='onchange')
    orden = fields.Integer(string="Orden")
    area = fields.Char(string="Area")
    status = fields.Boolean(string="Activo", required=True, track_visibility='onchange')


    def get_all_rdirectorio(self, estado=0):
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
                      
                      Directorio {
                        Oid
                        NombreCompleto
                        Cargo
                        Titulo
                        Telefono
                        Correo
                        Orden
                        Area
                        UrlFotoPerfil
                        UrlFacebook
                        UrlInstagram
                        UrlTwitter
                        Activo
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
            blogp = self.env["web.directorio"]
            if r.status_code == 200:
                data = json.loads(r.text)
                status = data['data']['getTransparencia']['status']
                if str(status) == "True":
                    datos_rec = data['data']['getTransparencia']['transparencia']['Directorio']
                else:
                    token = rec.set_wizard()

                    headers = {"Content-Type": "application/json", "Authorization": token}
                    r = requests.post(url=rec.url, json={'query': query}, headers=headers)
                    data = json.loads(r.text)
                    datos_rec = data['data']['getTransparencia']['transparencia']['Directorio']
                if datos_rec != None:
                    # datos_fil = sorted(datos_rec, key=lambda k: k['FechaPublicacionRegeneracion'], reverse=True)
                    for noti in datos_rec:
                        arb = False
                        if str(noti['Activo']) == "True":
                            arb = True

                        bubl = blogp.search([
                            ('Oid', '=', noti['Oid']),
                        ])
                        if bubl:
                            for bp in bubl:
                                # bp['active'] = arb
                                bp['status'] = arb
                                bp['name'] = noti['NombreCompleto'] if noti['NombreCompleto'] != " " else ""
                                bp['cargo'] = noti['Cargo'] if noti['Cargo'] != " " else ""
                                bp['titulo'] = noti['Titulo'] if noti['Titulo'] != " " else ""
                                bp['telefono'] = noti['Telefono'] if noti['Telefono'] != " " else ""
                                bp['correo'] = noti['Correo'] if noti['Correo'] != " " else ""
                                bp['perfil'] = noti['UrlFotoPerfil'] if noti['UrlFotoPerfil'] != " " else ""
                                bp['face'] = noti['UrlFacebook'] if noti['UrlFacebook'] != " " else ""
                                bp['insta'] = noti['UrlInstagram'] if noti['UrlInstagram'] != " " else ""
                                bp['twit'] = noti['UrlTwitter'] if noti['UrlTwitter'] != " " else ""
                                bp['orden'] = noti['Orden'] if noti['Orden'] != " " else ""
                                bp['area'] = noti['Area'] if noti['Area'] != " " else ""
                        else:
                            blogp.create({
                                "name": noti['NombreCompleto'] if noti['NombreCompleto'] != " " else "",
                                "Oid": noti['Oid'] if noti['Oid'] != " " else "",
                                "cargo": noti['Cargo'] if noti['Cargo'] != " " else "",
                                "titulo": noti['Titulo'] if noti['Titulo'] != " " else "",
                                "telefono": noti['Telefono'] if noti['Telefono'] != " " else "",
                                "correo": noti['Correo'] if noti['Correo'] != " " else "",
                                "orden": noti['Orden'] if noti['Orden'] != " " else "",
                                "perfil": noti['UrlFotoPerfil'] if noti['UrlFotoPerfil'] != " " else "",
                                "face": noti['UrlFacebook'] if noti['UrlFacebook'] != " " else "",
                                "insta": noti['UrlInstagram'] if noti['UrlInstagram'] != " " else "",
                                "twit": noti['UrlTwitter'] if noti['UrlTwitter'] != " " else "",
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

