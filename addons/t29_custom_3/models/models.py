from odoo import models, fields

class T29Custom3Model(models.Model):
    _name = 't29_custom_3.model'
    _description = 'T29 Custom 3 Model'

    name = fields.Char(string="Name")
    custom_2_ref = fields.Many2one('t29_custom_2.model', string="T29 Custom 2 Reference")