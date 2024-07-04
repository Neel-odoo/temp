from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    report_location_ids = fields.Many2many('stock.location', string='locations', readonly=False)
