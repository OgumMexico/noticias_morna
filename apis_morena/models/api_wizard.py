import json
from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
import logging
import os
import time
import base64
import requests
from requests.structures import CaseInsensitiveDict
from requests.auth import HTTPBasicAuth

class apiCustom(models.Model):
    _name = 'api.custom'
    _description = "Configuracion de Apis Noticias"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre de Instancia", required=True, track_visibility='onchange')
    color = fields.Integer('Color')
    user = fields.Char(string="Usuario o correo", required=True, track_visibility='onchange')
    password = fields.Char(string="Contraseña", required=True, track_visibility='onchange')
    active = fields.Boolean(string="Activado")
    date = fields.Datetime(string="Fecha Hora")
    token = fields.Text(string="Token")

    url = fields.Char(string="Url Conexion", required=True, track_visibility='onchange', default="https://servicios-comites.morena.app/graphql" )

    def get_instance(self):
        """
        function is used for returning
        current form view of instance.

        """
        return {
            'name': _('Instance'),
            'view_mode': 'form',
            'res_model': 'api.custom',
            'res_id': self.id,
            'domain': [],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',

        }

    def get_wizard(self):
        for api in self:
            if api.active:
                headers = {"Content-Type": "application/json"}
                url_services = api.url
                query = """{
                              login(email: \""""+ api.user +"\", password: \""+ api.password+ "\" "+""") {
                              status
                               message
                              token
                              }
                              }"""
                r = requests.post(url=url_services, json={'query': query}, headers=headers)
                r.encoding = 'utf-8'
                token=""
                status=""
                data = json.loads(r.text)
                if r.status_code == 200:
                    status = data['data']['login']['status']
                    # if str(status) == "true":
                    token = data['data']['login']['token']
                    api.token = token
                    date = fields.Date.context_today(self)
                status_code = str(r.status_code)


                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': status_code,
                        'message': token,
                        'type': 'success',  # types: success,warning,danger,info
                        'sticky': True,  # True/False will display for few seconds if false
                    },
                }
                return notification

    def set_wizard(self):
        for api in self:
            token = ""
            if api.active:
                headers = {"Content-Type": "application/json"}
                url_services = api.url
                query = """{
                              login(email: \""""+ api.user +"\", password: \""+ api.password+ "\" "+""") {
                              status
                               message
                              token
                              }
                              }"""
                r = requests.post(url=url_services, json={'query': query}, headers=headers)
                r.encoding = 'utf-8'

                status = ""
                data = json.loads(r.text)
                if r.status_code == 200:
                    status = data['data']['login']['status']
                    # if status:
                    token = data['data']['login']['token']
                    api.token = token
                    date = fields.Date.context_today(self)


                return token
            else:
                return token