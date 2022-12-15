import json
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import requests

class Blog_Post(models.Model):
    _inherit = "blog.post"

    image_variant = fields.Image("Variant Image")
    id_noticia = fields.Char(string="Id Noticia")

    @api.model
    def write1(self, values):
        """Override default Odoo write function and extend."""
        # Do your custom logic here
        return super(Blog_Post, self).write(values)

    def get_noticias(self,id_n=1):
        datos = self.env["api.custom"].search([('active', '=', True)])
        for rec in datos:
            token = rec.token

            headers = {"Content-Type": "application/json", "Authorization":token}
            query = """
                    query
                    noticiasNaiconales
                    {
        
                        getNoticias {
                            status
                            message
                            noticias{
                                FechaPublicacion
                                Oid
                                Titulo
                                Descripcion
                                Orden
                                UrlImagen
                                UrlLink
                                Activo
                            }
                      }
                    }"""
            r = requests.post(url=rec.url, json={'query': query}, headers=headers)
            r.encoding = 'utf-8'
            datos_rec = []
            status = ""
            blog = []
            blogp = self.env["blog.post"]
            if r.status_code == 200:
                data = json.loads(r.text)
                status = data['data']['getNoticias']['status']
                if str(status) == "True":
                    datos_rec = data['data']['getNoticias']['noticias']
                else:
                    token = rec.set_wizard()

                    headers = {"Content-Type": "application/json", "Authorization":token}
                    r = requests.post(url=rec.url, json={'query': query}, headers=headers)
                    data = json.loads(r.text)
                    datos_rec = data['data']['getNoticias']['noticias']
                if datos_rec != None:
                    datos_fil = sorted(datos_rec, key=lambda k: k['FechaPublicacion'], reverse=True)
                    for noti in datos_fil:
                        url=noti['UrlImagen']
                        link = ""
                        if noti['UrlLink']:
                            if noti['UrlLink'] !="#":
                                link="<a href='"+ str(noti['UrlLink']) + "' target='_blank'> Mas Información</a>"
                        arb = False
                        if str(noti['Activo']) == "True":
                            arb = True
                        blog.append({
                            "blog_id": id_n,
                            "id_noticia":noti['Oid'],
                            "active": True,
                            "name": noti['Titulo'],
                            "content": "<p>" + noti['Descripcion'] + "</p><br>"+ link,
                            # "is_published": arb,
                            "post_date": datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S"),
                            "write_date": datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S"),
                            "published_date": datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S"),
                            "subtitle": "",
                            "website_meta_description": noti['Descripcion'],
                            "website_meta_keywords": "Morena, Noticias",
                            "website_meta_title": noti['Titulo'],
                            # "website_meta_title": noti['Titulo'],
                            "cover_properties": '{"background_color_class": "o_cc3", "background-image": "url('+ url +')", "opacity": "0.2", "resize_class": "o_half_screen_height"}',

                        })
                        bubl = blogp.search([

                            ('id_noticia', '=', noti['Oid']),

                        ])
                        if bubl:
                            for bp in bubl:
                                bp['blog_id'] = id_n
                                bp['name'] = noti['Titulo']
                                bp['cover_properties'] = '{"background_color_class": "o_cc3", "background-image": "url('+ url +')", "opacity": "0.2", "resize_class": "o_half_screen_height"}'
                                bp['active'] = arb
                                bp['is_published'] = arb
                                bp['content'] = "<p>" + noti['Descripcion'] + "</p><br>" + link


                                date = datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S")

                                bp['post_date'] = date
                                bp['write_date'] = date
                                bp['published_date'] = date

                                bp.post_date = date
                                bp.write_date = date
                                bp.published_date = date
                        else:
                            blogp.create({
                            "blog_id": id_n,
                            "active": True,
                            "id_noticia": noti['Oid'],
                            "name": noti['Titulo'],
                            "content": "<p>" + noti['Descripcion'] + "</p><br>"+ link,
                            "is_published": arb,
                            "post_date": datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S"),
                            "write_date": datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S"),
                            "published_date": datetime.strptime(noti['FechaPublicacion'], "%Y-%m-%d %H:%M:%S"),
                            "subtitle": "",
                            "website_meta_description": noti['Descripcion'],
                            "website_meta_keywords": "Morena, Noticias",
                            "website_meta_title": noti['Titulo'],
                            # "website_meta_title": noti['Titulo'],
                            "cover_properties": '{"background_color_class": "o_cc3", "background-image": "url('+ url +')", "opacity": "0.2", "resize_class": "o_half_screen_height"}',

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

