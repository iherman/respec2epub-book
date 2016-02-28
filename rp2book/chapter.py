# -*- coding: utf-8 -*-
"""
Abstraction for one “chapter”, i.e., one of the EPUB instances that together constitute the final book.
"""
import os.path
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from datetime import datetime


def clone_element(el):
	"""
	Clone an element

	:param el: incoming element
	:type el: :py:class:`ElementTree.Element`
	:return: cloned element
	:type: :py:class:`ElementTree.Element`
	"""
	# This is very ugly, I do not know why ElementTree does not have a method for this. Oh well...
	# The element is 'serialized' into a string, and then parsed back again.
	return ET.fromstring(ET.tostring(el, encoding = "utf-8", method = "xml"))


class Chapter(object):
	"""
	Class for a chapter, providing all the information that is necessary for the creation of “top level”
	administration files like tables of content or package files.

	:param directory_name: the directory in the file system containing the chapter. All information will be extracted with this as a base.
	:type directory_name: string
	"""

	# noinspection PyPep8
	def __init__(self, directory_name):
		self._source = directory_name if directory_name[-1] != '/' else directory_name[:-1]
		self._target = os.path.basename(self._source)
		self._opf = OPF(self)
		self._nav = Nav(self)
		self._ncx = NCX(self)

	def __repr__(self):
		retval = "Chapter '" + self.target + " at " + self.source + "'"
		# retval += repr(self.nav)
		return retval

	@property
	def opf(self):
		"""The root of the navigation, an :py:class:`ElementTree.Element` object"""
		return self._opf

	@property
	def nav(self):
		"""Abstraction for the information in the package file; an instance of :py:class:`.NAV`."""
		return self._nav.nav

	@property
	def ncx(self):
		"""Abstraction for the information in the package file; an array of :py:class:`ElementTree.Element` objects for the table of content."""
		return self._ncx.toc

	@property
	def source(self):
		"""Directory name pointing at the chapter."""
		return self._source

	@property
	def target(self):
		"""Target directory for the copied chapter"""
		return self._target

	@property
	def title(self):
		"""Chapter title"""
		return self.opf.title

	@property
	def date(self):
		"""Chapter title"""
		return self.opf.date

	@property
	def creators(self):
		"""Chapter creator"""
		return self.opf.creators


class OPF(object):
	"""
	Abstraction of the package file, providing the run-time information important for processing.
	Its expected name and position within the chapter is `package.opf`.
	"""

	def __init__(self, chapter):
		"""
		:param chapter: the chapter object
		:type chapter: :py:class:`Chapter`
		:return:
		"""
		# First, parse the package file to get to the content
		ET.register_namespace('', "http://www.idpf.org/2007/opf")
		root = ET.parse(os.path.join(chapter.source, "package.opf")).getroot()

		# First get the simple metadata
		self._title = root.find(".//{http://purl.org/dc/elements/1.1/}title").text

		dt = root.find(".//{http://www.idpf.org/2007/opf}meta[@property='dcterms:date']").text
		# TODO: the format string should be imported from the rp2epub package!
		self._date = datetime.strptime(dt, "%Y-%m-%dT%M:%S:00Z")

		creator = root.find(".//{http://purl.org/dc/elements/1.1/}creator").text
		self._creators = creator.replace(" (editors)", "").replace(" (editor)", "") + "; "

		# Get the manifest entries
		self._manifest = self._get_manifest(chapter.target, root)

		# Get the spine
		self._spine = self._get_spine(chapter.target, root)

	@property
	def title(self):
		"""The title of the chapter"""
		return self._title

	@property
	def date(self):
		"""The date of the publication (as a datetime object)"""
		return self._date

	@property
	def creators(self):
		"""The creators' string"""
		return map(lambda x: x.strip(), self._creators.split(';'))

	@property
	def manifest(self):
		"""The cloned manifest data: an array of :py:class:`ElementTree.Element` objects"""
		return self._manifest

	@property
	def spine(self):
		"""The cloned spine data: an array of :py:class:`ElementTree.Element` objects"""
		return self._spine

	@staticmethod
	def _get_manifest(dir_name, root):
		""" Collect the manifest entries, converting them on the fly, namely:

		- change the `@href` attributes to include the directory name
		- change the `@id` attributes to include the directory name (normalized to '-' instead of '/')
		- removing entries for navigation

		:param dir_name: the directory in the file system containing the chapter. All information will be extracted with this as a base.
		:type dir_name: string
		:param root: the Root element of the package file
		:type root: :py:class:`ElementTree.Element`
		:return: a list of :py:class:`ElementTree.Element` objects
		"""

		def convert_item(item):
			"""
			Clone and convert an item to be included in the cloned list of manifest items by updating the `@href` values
			(to point at the chapter).

			Navigation and ncx items are filtered out (returning None); those are not used on the book level.

			:param item: old item
			:type item: :py:class:`ElementTree.Element` object
			:return:
			"""
			if item.get("id") == "nav" or item.get("id") == "ncx":
				return None
			else:
				cloned_item = clone_element(item)
				cloned_item.set("href", dir_name + "/" + cloned_item.get("href"))
				cloned_item.set("id", dir_name.replace("/", "-") + "-" + cloned_item.get("id"))
				return cloned_item

		return filter(lambda i: i is not None, map(convert_item, root.findall(".//{http://www.idpf.org/2007/opf}item")))

	@staticmethod
	def _get_spine(dir_name, root):
		""" Collect the spine entries, converting them on the fly, namely:

		- change the `@idref` attributes to include the directory name (normalized to '-' instead of '/')
		- removing entries for start

		:param dir_name: the directory in the file system containing the chapter. All information will be extracted with this as a base.
		:type dir_name: string
		:param root: the Root element of the package file
		:type root: :py:class:`ElementTree.Element`
		:return: a list of :py:class:`ElementTree.Element` objects
		"""

		def convert_item(item):
			"""
			Clone and convert an item to be included in the cloned list of spine items by updating the `@idref` values
			(to point at the chapter). To be used in a `map` function

			:param item: old item
			:type item: :py:class:`ElementTree.Element` object
			:return:
			"""
			cloned_item = clone_element(item)
			cloned_item.set("idref", dir_name.replace("/", "-") + "-" + cloned_item.get("idref"))
			return cloned_item

		return filter(lambda i: i is not None, map(convert_item, root.findall(".//{http://www.idpf.org/2007/opf}itemref")))

	def __repr__(self):
		retval = "        %s\n" % self.title
		retval += "        %s\n" % self.date
		retval += "        %s\n" % self.creators
		retval += "        Manifest:\n"
		for i in self.manifest:
			retval += "        -- %s\n" % ET.tostring(i)
		retval += "        Spine:\n"
		for i in self.spine:
			retval += "        -- %s\n" % ET.tostring(i)
		return retval


class Nav(object):
	"""
	Abstraction of the new type navigation (TOC) file, providing the run-time information important for processing.
	Its expected name and position within the chapter is `nav.xhtml`.
	"""

	def __init__(self, chapter):
		"""
		:param chapter: the chapter object
		:type chapter: :py:class:`Chapter`
		"""
		# First, parse the package file to get to the content
		root = ET.parse(os.path.join(chapter.source, "nav.xhtml")).getroot()
		nav = root.find(".//{http://www.w3.org/1999/xhtml}nav[@id='toc']/{http://www.w3.org/1999/xhtml}ol")
		assert nav is not None
		self._nav = clone_element(nav)
		# Change the reference for an <a> Element to include the directory name
		for a in self._nav.findall(".//{http://www.w3.org/1999/xhtml}a"):
			a.set("href", chapter.target + '/' + a.get('href'))

	@property
	def nav(self):
		"""The navigation root element itself, an ElementTree.Element object"""
		return self._nav

	def __repr__(self):
		retval = "...   Nav:"
		for i in self.nav:
			retval += "        %s\n" % i
		return retval


class NCX(object):
	"""
	Abstraction of the old type TOC file, providing the run-time information important for processing.
	Its expected name and position within the chapter is `toc.ncx`.
	"""

	def __init__(self, chapter):
		"""
		:param chapter: the chapter object
		:type chapter: :py:class:`Chapter`
		"""
		def clone_and_change_src(e):
			"""
			Convert a TOC item, by cloning and changing the target reference.

			:param e: the original element
			:type e: ElementTree.Element object
			:return: the cloned and modified element
			"""
			cloned_e = clone_element(e)
			a = cloned_e.find(".//{http://www.daisy.org/z3986/2005/ncx/}content")
			assert a is not None
			a.set("src", chapter.target + '/' + a.get('src'))
			return cloned_e

		# First, parse the package file to get to the content
		root = ET.parse(os.path.join(chapter.source, "toc.ncx")).getroot()

		# Collect each element, changing the reference on the fly
		self._toc = map(clone_and_change_src, root.findall(".//{http://www.daisy.org/z3986/2005/ncx/}navPoint"))

	@property
	def toc(self):
		"""An array of an ElementTree.Element objects"""
		return self._toc

