from odoo import fields, models, _
from odoo.exceptions import UserError

class QuantReportCustom(models.Model):
    _name = 'quant.report.custom'
    _description = 'Quant Report'
    _auto = False

    product_id = fields.Many2one('product.product', string="Product")
    product_categ_id = fields.Many2one('product.category', string="Product Category")
    location_id = fields.Many2one('stock.location', string="Location")
    on_hand_quantity = fields.Float(string="On Hand Quantity", default=0)
    unposted_pos_quantity = fields.Float(string="Unposted POS Orders", default=0)
    available_quantity = fields.Float(string="Available Quantity", compute="_compute_available_quantity")
    quantity_in_transit = fields.Float(string="Quantity In Transit", compute="_compute_quantity_in_transit")
    expected_quantity = fields.Float(string="Expected Quantity", compute="_compute_expected_quantity")
    standard_price = fields.Float(string="Average Unit Cost", related="product_id.standard_price")
    stock_value = fields.Float(string="Stock Value", compute="_compute_stock_value")

    def _compute_available_quantity(self):
        for record in self:
            record.available_quantity = record.on_hand_quantity - record.unposted_pos_quantity

    def _compute_quantity_in_transit(self):
        self.env.cr.execute("""
                SELECT
                    CONCAT(sm.product_id, '_', sm.location_dest_id) AS name,
                    sum(sm.product_uom_qty) AS quantity_in_transit
                FROM
                    stock_move sm
                    LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
                    LEFT JOIN stock_picking_type spt ON spt.id = sp.picking_type_id AND spt.code IN ('incoming', 'internal')
                WHERE
                    sp.state NOT IN ('done', 'cancel')
                GROUP BY sm.product_id, sm.location_dest_id
        """)
        results = {result['name']:result['quantity_in_transit'] for result in self.env.cr.dictfetchall()}
        for record in self:
            key = "%s_%s" % (record.product_id.id, record.location_id.id)
            record.quantity_in_transit = results.get(key, 0)

    def _compute_expected_quantity(self):
        for record in self:
            record.expected_quantity = record.available_quantity + record.quantity_in_transit

    def _compute_stock_value(self):
        for record in self:
            record.stock_value = record.standard_price * record.on_hand_quantity

    @property
    def _table_query(self):
        if self.env.user.report_location_ids:
            location_ids = self.env.user.report_location_ids.ids
        else:
            warehouses = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id), ('active', '=', True)])
            location_ids = warehouses.lot_stock_id.ids

        wh_child_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
            [('id', 'child_of', location_ids)],
            ['id'],
        )]
        location_ids += wh_child_ids

        query = """
                SELECT DISTINCT ON (sq.product_id, sq.location_id)
                    sq.id,
                    pt.categ_id as product_categ_id,
                    sq.product_id,
                    sq.location_id,
                    sq.quantity AS on_hand_quantity,
                    CASE WHEN po.state!='done' THEN sum(pol.qty) ELSE 0 END as unposted_pos_quantity
                FROM
                    stock_quant AS sq
                    LEFT JOIN pos_order_line pol ON pol.product_id = sq.product_id
                    LEFT JOIN pos_order po ON po.id = pol.order_id
                    LEFT JOIN product_product pp ON pp.id = sq.product_id
                    LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        """
        if len(location_ids) == 1:
            query += """
                WHERE
                    sq.company_id = %s AND sq.location_id = %s
                GROUP BY sq.id, pt.categ_id, sq.product_id, sq.location_id, sq.quantity, po.state
            """ % (self.env.company.id, location_ids[0])
        else:
            query += """
                WHERE
                    sq.company_id = %s AND sq.location_id IN %s
                GROUP BY sq.id, pt.categ_id, sq.product_id, sq.location_id, sq.quantity, po.state
            """ % (self.env.company.id, tuple(location_ids))
        return query

    def action_open_transfers(self):
        if not self.quantity_in_transit:
            raise UserError(_("Pending Transfers are not Available for Location: %s", self.location_id.display_name))
        pickings = self.env['stock.picking'].search([
            ('location_dest_id', '=', self.location_id.id),
            ('picking_type_id.code', 'in', ['incoming', 'internal']),
            ('state', 'not in', ['done', 'cancel'])
        ])
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action

    def action_open_stock_move_lines(self):
        self.ensure_one()
        action = {
            'name': _('History'),
            'view_mode': 'list,form',
            'res_model': 'stock.move.line',
            'views': [(self.env.ref('stock.view_move_line_tree').id, 'list'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'context': {
                'search_default_product_id': self.product_id.id,
            },
        }
        return action
