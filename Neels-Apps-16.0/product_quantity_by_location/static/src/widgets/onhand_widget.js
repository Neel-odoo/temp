odoo.define('product_quantity_by_location.quantity_by_locations_tree_view_pos', function (require) {
    "use strict";

    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.on_hand_quantity_button', this.onHandQuantityClicked.bind(this));
            }
        },
        onHandQuantityClicked: function (event) {
            event.preventDefault();
            var recordID = $(event.currentTarget).data('id'); // Assuming you have a data attribute 'data-id' containing the record ID
            debugger
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Stock Move Lines',
                res_model: 'stock.move.line',
                domain: [['quant_id', '=', recordID]], // Replace 'quant_id' with the actual field name relating stock move lines to on hand quantity
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
    });
});
