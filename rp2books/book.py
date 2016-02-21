# -*- coding: utf-8 -*-
"""
The main controller class performing all the steps necessary to process...
"""

from .chapter import Chapter
from .package import generate_opf, generate_nav, generate_ncx, generate_cover
import shutil
import os
from StringIO import StringIO

import xml.etree.ElementTree as ET
class Data(object):
	"""This is just a Python trick: objects of this class behave pretty much like a dictionary, but also using
	the "." notation; this makes the code look nicer...
	"""
	def __setattr__(self, name, value):
		object.__setattr__(self, name, value)

	def __getitem__(self, name):
		return self.__dict__[name]

	def __setitem__(self, name, value):
		self.__setattr__(name, value)

	def __contains__(self, name):
		return name in self.__dict__


class Book:
	"""
	Top level creator of the the combined book. The main processing is done in the :py:meth:`process` method.
	:param config: Book configuration
	:type config: dictionary
	"""

	# noinspection PyPep8
	def __init__(self, config):
		self._config    = config
		self._chapters  = []
		self._book_data = Data()

		# Some generic metadata
		self._book_data.chapters = map(lambda d: Chapter(d["source"]), self._config["chapters"])
		self._book_data.title    = config["title"]
		self._book_data.id       = config["id"]
		self._book_data.date     = max([c.date for c in self._book_data.chapters])

		def intelligent_concat(x,y) :
			"""Add elements of the second array to the first only if it is not there..."""
			if len(x) == 0:
				return filter(lambda c: len(c) != 0, y)
			else:
				return x + filter(lambda c: len(c) and c not in x, y)
		all_editors = reduce(intelligent_concat, [c.creators for c in self._book_data.chapters], [])
		self._book_data.editors = "; ".join(all_editors).strip()


		self.opf   = generate_opf(self._book_data)
		self.nav   = generate_nav(self._book_data)
		self.ncx   = generate_ncx(self._book_data)
		self.cover = generate_cover(self._book_data)

		self.process()

	@property
	def book_data(self):
		"""The overall book data, collected from the configuration file and the chapters."""
		return self._book_data

	# noinspection PyPep8,PyUnresolvedReferences
	def process(self):
		"""
		Generate the files...
		:return:
		"""
		# All the file copying business...
		# The target directory should either be created, if not yet there. If it is there, it should be emptied first
		# Note that the target path is a simple file name, not a full path!
		to_copy   = ["META-INF/container.xml", "mimetype", "StyleSheets/TR/base.css", "Icons/w3c_main.png"]
		to_remove = ["mimetype", "nav.xhtml", "package.opf", "toc.ncx"]
		to_add    = [
			(self.opf, "package.opf", "http://www.idpf.org/2007/opf"),
			(self.nav, "nav.xhtml", "http://www.w3.org/1999/xhtml"),
			(self.ncx, "toc.ncx", "http://www.daisy.org/z3986/2005/ncx/"),
			(self.cover, "cover.xhtml", "http://www.w3.org/1999/xhtml")
		]
		target    = self._config["target"]

		# The target directory should be emptied and created
		try:
			shutil.rmtree(target)
		except OSError:
			pass
		os.makedirs(target)

		# Each chapter, ie, the corresponding book directory, must be copied to the target
		# TODO: what if the unpacked book is not available???

		def copy_chapter(c):
			"""
			Copy a full chapter into the target, and then prune it by removing the local admin files.

			:param c: a chapter
			:type c: :py:class:`chapter.Chapter` object
			:return:
			"""
			c_target = os.path.join(target, os.path.basename(c.source))
			shutil.copytree(c.source, c_target)

			# some files should be removed from that target, though
			shutil.rmtree(os.path.join(c_target, "META-INF"))
			map(lambda f: os.remove(os.path.join(c_target, f)), to_remove)
		map(copy_chapter, self.book_data.chapters)

		# Some elements should be copied from one of the chapters into the 'main' part
		s_chapter = self.book_data.chapters[0].source

		def copy_item(tc):
			"""
			Copy one file, possibly creating the directories on the fly

			:param tc: path name for a file to copy
			"""
			if os.path.dirname(tc) != "":
				os.makedirs(os.path.join(target, os.path.dirname(tc)))
			shutil.copyfile(os.path.join(s_chapter, tc), os.path.join(target, tc))
		map(copy_item, to_copy)

		def write_admin_file(f):
			"""
			Write an admin file, generated for the chapter, into the the final directory (serializing the content)

			:param f: admin file like nav, package, etc
			:type f: tuple consisting of an ElementTree object, a filename, and a namespace URL (for default namespace)
			"""
			# Add the generated files
			f_element_tree, f_name, f_namespace = f
			ET.register_namespace('', f_namespace)
			content = StringIO()
			f_element_tree.write(content, encoding="utf-8", xml_declaration=True,  method="xml")
			with open(os.path.join(target, f_name), "w") as f_file:
				f_file.write(content.getvalue())
			content.close()
		map(write_admin_file, to_add)
		# default_namespace = f_namespace,

	def __repr__(self):
		retval = "%s" % self._config["title"]

		# for c in self._book_data.chapters:
		# 	retval += "\n... %s" % c
		# return retval
		# content = StringIO()
		# self.cover.write(content, encoding="utf-8", xml_declaration=True, method="xml")
		# return content.getvalue()

		# for nav in self._book_data.chapters:
		# 	retval += "\n... %s" % nav
		# return retval
		return retval



