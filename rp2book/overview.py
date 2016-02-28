# -*- coding: utf-8 -*-
"""
Modifying the Overview files of each chapter to ensure mutual references among chapters (when appropriate) instead of
using references to the TR documents.

"""
import os.path
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from StringIO import StringIO


# noinspection PyPep8
def _replace_references(root, uri_patterns):
	"""
	Convert the references within one file

	:param root: The root of the file; an `ElementTree.ElementTree` object
	:param uri_patterns: the uri patterns to take care of
	:type uri_patterns: Array of (from,to) tuples
	"""
	for a in root.findall(".//{http://www.w3.org/1999/xhtml}a"):
		if a.get("class") == "u-url": continue
		for (a_from, a_to) in uri_patterns:
			href = a.get("href")
			if href is None: continue
			if href.startswith(a_from + '#'):
				a.set("href", href.replace(a_from + '#', a_to + "Overview.xhtml#"))
			elif href.startswith(a_from + "Overview.html#"):
				a.set("href", href.replace(a_from + "Overview.html#", a_to + "Overview.xhtml#"))
			elif href == a_from:
				a.set("href", a_to)


def _convert_chapter(chapter, config):
	"""
	Convert one chapter: read in the source Overview.xhtml file, make the necessary changes, and serialize the result
	in the target directory

	:param chapter: One chapter
	:type chapter: :py:class:`.chapter.Chapter`
	:param config: Top level configuration
	:type config: :py:class:`.book.Config`
	"""
	# First, parse the Overview file to get to the content
	root = ET.parse(os.path.join(chapter.source, "Overview.xhtml"))
	_replace_references(root, config.uri_patterns)
	content = StringIO()
	root.write(content, encoding="utf-8", xml_declaration=True, method="xml")
	with open(os.path.join(config.target, chapter.target, "Overview.xhtml"), "w") as f_file:
		f_file.write(content.getvalue())
	content.close()


# noinspection PyPep8
def convert_overviews(config):
	"""
	Convert the Overview files by using the (from,to) pairs in the configuration. Wrapper around the :py:func:`_convert_chapter` function.

	:param config: Top level configuration
	:type config: :py:class:`.book.Config`
	"""
	if len(config.uri_patterns) != 0:
		ET.register_namespace('', "http://www.w3.org/1999/xhtml")
		for c in config.chapters: _convert_chapter(c, config)
