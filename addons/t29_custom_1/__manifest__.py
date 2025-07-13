{
    'name': 'T29 Custom 1',
    'version': '1.0.0',
    'category': 'Custom',
    'summary': 'Base custom module for Odoo deployment demo',
    'description': """
        T29 Custom 1 is the base custom module for demonstration.
    """,
    'author': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}