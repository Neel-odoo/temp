from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    report_location_ids = fields.Many2many(related='company_id.report_location_ids', readonly=False)
