{
    'name': 'T29 Custom 2',
    'version': '1.0.0',
    'category': 'Custom',
    'summary': 'Second custom module, depends on t29_custom_1',
    'description': """
        T29 Custom 2 depends on T29 Custom 1.
    """,
    'author': '',
    'depends': ['base', 't29_custom_1'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}