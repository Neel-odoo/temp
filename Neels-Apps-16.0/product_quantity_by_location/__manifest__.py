# -*- coding: utf-8 -*-
{
    'name': 'Products Quantity By Locations',
    'category': 'Inventory',
    
    'sequence': 10,
    'summary': """Display all Products Quantity By Locations.""",
    'description': """
        Module Description:
            This module will show all Products Quantity By Locations.
    """,
    'depends': ['base', 'stock', 'point_of_sale', 'pos_epson_printer'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_quant_views.xml',
        'views/res_users.xml',
        
    ],
# 'assets': {
#         'web.assets_backend': [
#             'web_enterprise/static/src/**/*.js',
#         ],
#     },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 25,
    "currency": 'USD',
}
