# -*- coding: utf-8 -*-
from distutils.core import setup
import rp2book

setup(
	name='rp2book',
	version=rp2book.__version__,
	packages=['rp2book'],
	scripts=['script/rp2book'],
	url='https://github.com/iherman/respec2epub-book',
	download_url='https://github.com/iherman/tr2epub/archive/master.zip',
	license='W3C © SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>',
	maintainer='Ivan Herman',
	maintainer_email='ivan@ivan-herman.net',
	author='Ivan Herman',
	author_email='ivan@ivan-herman.net',
	description='Generate and EPUB3 file as a collection of several EPUB3 files from respec based W3C Technical Reports',
	keywords='W3C EPUB3',
	platforms='any',
	install_requires=['html5lib', 'tinycss', 'respec2epub', 'pyyaml'],
	requires=['html5lib', 'tinycss', 'respec2epub', 'pyyaml'],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Information Technology',
		'License :: W3C Software Notice and License',
		'Programming Language :: Python :: 2.7'
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Documentation :: Sphinx',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
		'Topic :: Utilities'
	]
)
