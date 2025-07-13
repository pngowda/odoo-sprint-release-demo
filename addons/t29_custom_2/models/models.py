from odoo import models, fields

class T29Custom2Model(models.Model):
    _name = 't29_custom_2.model'
    _description = 'T29 Custom 2 Model'

    name = fields.Char(string="Name")
    custom_1_ref = fields.Many2one('t29_custom_1.model', string="T29 Custom One Reference")