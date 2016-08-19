# -*- coding: utf-8 -*-
"""
Module entry point.
"""

import locale
from .book import Book

__version__ = "1.1"
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


def start(config, package = False, folder = True):
	"""
	Just a shorthand for Book. Using this method ensures the proper setting of the locale to en_US,
	necessary for the W3C specific date format.

	:param config: Reference to the JSON configuration file
	:param package: flag on whether the packaged version, ie, the "real" ebook should be generated
	:param folder: flag whether the unpacked folder should be kept
	"""
	Book(config, package, folder)

