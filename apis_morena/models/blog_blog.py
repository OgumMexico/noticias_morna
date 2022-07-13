import json
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import requests

class Blog_Post(models.Model):
    _inherit = "blog.post"

    image_variant = fields.Image("Variant Image")

    @api.model
    def write1(self, values):
        """Override default Odoo write function and extend."""
        # Do your custom logic here
        return super(Blog_Post, self).write(values)

    def get_noticias(self):
        datos = self.env["api.custom"].search([('active', '=', True)])
        for rec in datos:
            token = rec.token

            headers = {"Content-Type": "application/json", "Authorization":token}
            query = """
                    query
                    noticiasNaiconales
                    {
        
                        getNoticias
                        {
                            status
                            message
                            noticias
                            {
                                Titulo
                                Descripcion
                                FechaPublicacion
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
                    for noti in datos_rec:
                        url=noti['UrlImagen']
                        link=noti['UrlLink']
                        arb = False
                        if str(noti['Activo']) == "True":
                            arb = True
                        blog.append({
                            "blog_id": 1,
                            "active": True,
                            "name": noti['Titulo'],
                            "content": "<p>" + noti['Descripcion'] + "</p><br><a href='"+ link + "' target='_blank'> Mas Información</a>",
                            # "is_published": arb,
                            # "post_date": noti['Titulo'],
                            "subtitle": "",
                            "website_meta_description": noti['Descripcion'],
                            "website_meta_keywords": "Morena, Noticias",
                            "website_meta_title": noti['Titulo'],
                            # "website_meta_title": noti['Titulo'],
                            "cover_properties": '{"background_color_class": "o_cc3", "background-image": "url('+ url +')", "opacity": "0.2", "resize_class": "o_half_screen_height"}',

                        })
                        bubl = blogp.search([

                            ('name', '=', noti['Titulo']),
                            ('website_meta_description', '=', noti['Descripcion']),
                            ('cover_properties', '=', '{"background_color_class": "o_cc3", "background-image": "url('+ url +')", "opacity": "0.2", "resize_class": "o_half_screen_height"}'),
                        ])
                        if bubl:
                            for bp in bubl:
                                bp['active'] = arb
                                bp['content'] = "<p>" + noti['Descripcion'] + "</p><br><a href='"+ link + "' target='_blank'> Mas Información</a>"
                        else:
                            blogp.create({
                            "blog_id": 1,
                            "active": True,
                            "name": noti['Titulo'],
                            "content": "<p>" + noti['Descripcion'] + "</p><br><a href='"+ link + "' target='_blank'> Mas Información</a>",
                            "is_published": arb,
                            # "post_date": noti['Titulo'],
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

