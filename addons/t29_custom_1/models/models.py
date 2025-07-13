from odoo import models, fields

class T29CustomOneModel(models.Model):
    _name = 't29_custom_1.model'
    _description = 'T29 Custom 1 Model'

    name = fields.Char(string="Name")