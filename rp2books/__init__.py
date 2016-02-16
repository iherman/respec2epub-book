# -*- coding: utf-8 -*-
"""
Module entry point.
"""

import locale
import json
from .book import Book

__version__ = "0.5"
# noinspection PyPep8
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/copyright-software>'


class R2BError(Exception):
	"""
	rp2books specific Exception class; used to wrap normal exceptions, without adding any functionality.
	"""
	pass

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def start(config_file):
	"""
	Debug level for now...

	:param config_file:
	:return:
	"""
	with open(config_file) as f:
		config = json.load(f)

	the_book = Book(config)
	print the_book

