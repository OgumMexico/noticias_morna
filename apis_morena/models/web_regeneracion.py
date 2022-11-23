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
                                bp['name'] = noti['TituloRegeneracion']
                                bp['descripcion'] = noti['DescripcionRegeneracion']
                                bp['image'] = noti['UrlimagenRegeneracion']
                                bp['archivo'] = noti['UrlLinkRegeneracion']
                                bp['date'] = date
                                bp['year'] = date.year
                        else:

                            blogp.create({
                                "name": noti['TituloRegeneracion'],
                                "Oid": noti['Oid'],
                                "descripcion": noti['DescripcionRegeneracion'],
                                "orden": noti['OrdenRegeneracion'],
                                # "is_published": arb,
                                "image": noti['UrlimagenRegeneracion'],
                                "archivo": noti['UrlLinkRegeneracion'],
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


    """ 
    <section class="s_text_block o_colored_level pb0 pt32" data-snippet="s_text_block" data-name="Text" style="background-image: none;">
        <div class="s_allow_columns container">
          <p>
            <font class="bg-black" style="font-weight: bolder; font-size: 24px;">Publicaciones 2022 &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp;&amp;nbsp;</font>
            <br/>
          </p>
        </div>
      </section>
      <section class="s_three_columns pb32 o_colored_level o_cc o_cc1 pt0" data-vcss="001" data-snippet="s_three_columns" data-name="Columns" style="background-image: none;" data-original-title="" title="" aria-describedby="tooltip871504">
        <div class="container">
          <div class="row d-flex align-items-stretch" data-original-title="" title="" aria-describedby="tooltip682604">
            <div class="s_col_no_bgcolor pt0 pb24 col-lg-4">
              <div class="card h-100 border bg-o-color-5" style="border-width: 10px !important; border-color: rgb(136, 42, 44) !important;">
                <a href="http://34.75.53.151/oaxaca/regeneracion/Regeneracion-Ene-Feb.pdf" target="_blank">
                  <img class="card-img-top float-left" src="/web/image/1070-ea1bb94f/PORTADA-REGENERACI%C3%93N-1.jpg" alt="" loading="lazy" data-original-title="" title="" aria-describedby="tooltip974257" data-original-id="1070" data-original-src="/web/image/1070-ea1bb94f/PORTADA-REGENERACI%C3%93N-1.jpg" data-mimetype="image/jpeg" style=""/>
                </a>
                <div id="regeneracion" class="card-body">
                  <hr class="solid"/>
                  <h3 class="card-title" style="text-align: center;">
                    <span style="border-width: 1px; border-style: solid;" class="btn btn-custom"/>
                    <span style="font-size: 24px;">Regeneración Enero- Febrero 2022</span>
                    <br/>
                  </h3>
                  <p class="card-text o_default_snippet_text">
                    <br/>
                  </p>
                </div>
              </div>
            </div>
            <div class="s_col_no_bgcolor pt0 pb24 col-lg-4">
              <div class="card h-100 border bg-o-color-5" style="border-width: 10px !important; border-color: rgb(136, 42, 44) !important;">
                <a href="http://34.75.53.151/oaxaca/regeneracion/Regeneracion-Mar-Abr.pdf" target="_blank" data-original-title="" title="">
                  <img class="card-img-top" src="/web/image/1080-92ab5bf5/REGENERACION-01.jpg" alt="" loading="lazy" data-original-title="" title="" aria-describedby="tooltip974257" style="" data-original-id="1078" data-original-src="/web/image/1078-048ac92d/REGENERACION-01.jpg" data-mimetype="image/jpeg" data-resize-width="690"/>
                </a>
                <div id="regeneracion" class="card-body">
                  <hr class="solid"/>
                  <h3 class="card-title" style="text-align: center;">
                    <span style="font-size: 24px;">Regeneración Marzo- Abril 2022</span>
                    <br/>
                  </h3>
                  <p class="card-text o_default_snippet_text">
                    <br/>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    
    
    """