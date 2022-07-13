{
    'name'         : "Apis Noticias",
    'author'       : 'Jesus de Nazareth de La Cruz',
    'category'     : 'Attendances',
    'summary'      : """Verificacion automatica de noticias en apis'""",
    'website'      : 'https://www.ogum.com.mx',
    'company'      : 'OGUM',
    'maintainer'   : 'Ogum',
    'description'  : """ Creacion de control de apis para noticias en la web.""",
    'version'      : '1.0',
    'depends'      : ['base', 'web',"mail", 'website_blog'],
    'data'         : [
        "security/ir.model.access.csv",
        'data/ir_cron.xml',
        'views/api_wizard.xml',
        'views/blog_blog.xml',
    ],
    'images': ['static/description/banner.png'],

    'license'      : 'LGPL-3',
    'installable'  : True,
    'application'  : True,
    "auto_install": False,

}
