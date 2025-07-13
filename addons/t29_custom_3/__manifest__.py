{
    'name': 'T29 Custom 3',
    'version': '16.0.1.0.0',
    'category': 'Custom',
    'summary': 'Third custom module, depends on t29_custom_2',
    'description': """
        T29 Custom 3 depends on T29 Custom 2.
    """,
    'author': 'Your Company',
    'depends': ['base', 't29_custom_2'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}