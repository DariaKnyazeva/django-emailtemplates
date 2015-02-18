#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-emailtemplates',
    version='0.1',
    description='Templating system for application-generated emails',
    author='Michael O''Connor',
    author_email='michael@mcoconnor.net',
    url='https://github.com/DariaKnyazeva/django-emailtemplates.git@template_views',
    license='MIT',
    packages=[
        'emailtemplates',
        'emailtemplates.migrations',
    ],
    package_data={
        'emailtemplates': [
            'fixtures/*.json', 
            'templates/emailtemplates/*.html', 
            'static/emailtemplates/js/*.js',
        ]
    },
    install_requires=[
        'django-appconf',
        'django-compressor',
    ],
    extras_require = {
        'text_autogen':  ["html2text"],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
