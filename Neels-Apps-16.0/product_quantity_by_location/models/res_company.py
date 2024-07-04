from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_location_ids = fields.Many2many('stock.location', string='Locations')
