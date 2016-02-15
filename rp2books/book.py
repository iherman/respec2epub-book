# -*- coding: utf-8 -*-
"""
The main controller class performing all the steps necessary to process...
"""

from .chapter import Chapter
from .package import generate_opf, generate_nav, generate_ncx
from StringIO import StringIO


class Data(object):
	"""This is just a Python trick: objects of this class behave pretty much like a dictionary, but also using
	the "." notation; this makes the code look nicer...
	"""
	def __setattr__(self, name, value):
		object.__setattr__(self,name,value)

	def __getitem__(self,name):
		return self.__dict__[name]

	def __setitem__(self, name, value):
		self.__setattr__(name,value)

	def __contains__(self, name):
		return name in self.__dict__


class Book:
	"""
	Top level creator of the the combined book. The main processing is done in the :py:meth:`process` method.
	:param config: Book configuration
	:type config: dictionary
	"""
	def __init__(self, config):
		self._config    = config
		self._chapters  = []
		self._book_data = Data()

		# Some generic metadata
		self._book_data.chapters = map(lambda d: Chapter(d["directory"]), self._config["chapters"])
		self._book_data.title    = config["title"]
		self._book_data.id       = config["id"]
		self._book_data.date     = max([c.date for c in self._book_data.chapters])
		self._book_data.editors  = reduce(lambda x,y: x + y, [c.creators for c in self._book_data.chapters], "").strip()[:-1]

		self.process()

	def process(self):
		self.opf = generate_opf(self._book_data)
		self.nav = generate_nav(self._book_data)
		self.ncx = generate_ncx(self._book_data)

	def __repr__(self):
		retval = "%s" % self._config["title"]

		# for c in self._book_data.chapters:
		# 	retval += "\n... %s" % c
		# return retval
		content = StringIO()
		self.ncx.write(content, encoding="utf-8", xml_declaration=True, method="xml")
		return content.getvalue()

		# for nav in self._book_data.chapters:
		# 	retval += "\n... %s" % nav
		# return retval



