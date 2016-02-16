# -*- coding: utf-8 -*-
"""
Generation of the package file
"""

from rp2epub.templates import PACKAGE, NAV, NAV_CSS_NO_NUMBERING, TOC, COVER
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, SubElement


def generate_opf(book_data):
	"""
	Generation of a new OPF file that combines the information from different chapters.

	:param book_data: a data object collecting the necessary information for the creation of the new package file
	:return: Root of the generated package file; and ElementTree Element object
	"""
	def add_manifest_item(manifest, id, href, media_type):
		"""
		Creation of a new manifest item. (Function to be used in a 'map')

		:param manifest: the whole manifest (parent of the item)
		:param id: value of @id
		:param href: value of @href
		:param media_type: media type
		"""
		item = SubElement(manifest, "{http://www.idpf.org/2007/opf}item")
		item.set("id", id)
		item.set("href", href)
		item.set("media-type", media_type)

	def add_metadata_item(opf, path, value, ns="http://purl.org/dc/elements/1.1/"):
		"""
		Add a metadata item.

		:param opf: metadata element (parent of the item)
		:param path: element to add the metadata item to; it may be extended with an attribute value in XPath syntax
		:param value: value to be set for the metadata
		:param ns: namespace of used in the path
		"""
		item = opf.find((".//{%s}" % ns) + path)
		assert item is not None
		item.text = value

	# Parse the raw manifest file
	ET.register_namespace('', "http://www.idpf.org/2007/opf")
	opf = ElementTree(ET.fromstring(PACKAGE))

	# Manifest metadata
	add_metadata_item(opf, "title", book_data.title)
	add_metadata_item(opf, "identifier", book_data.id)
	add_metadata_item(opf, "meta[@property='dcterms:modified']", book_data.date.strftime("%Y-%m-%dT%M:%S:00Z"), ns="http://www.idpf.org/2007/opf")
	add_metadata_item(opf, "meta[@property='dcterms:date']", book_data.date.strftime("%Y-%m-%dT%M:%S:00Z"), ns="http://www.idpf.org/2007/opf")
	add_metadata_item(opf, "creator", book_data.editors)

	# The manifest:
	manifest = opf.find(".//{http://www.idpf.org/2007/opf}manifest")

	# Add the static entries
	add_manifest_item(manifest, "nav", "nav.xhtml", "application/xhtml+xml")
	add_manifest_item(manifest, "start", "cover.xhtml", "application/xhtml+xml")
	add_manifest_item(manifest, "ncx", "toc.ncx", "application/x-dtbncx+xml")

	# Here is the real meat: collect all the chapter manifest items, and add them to the local manifest
	map(lambda x: manifest.append(x), reduce(lambda x, y: x + y, [c.opf.manifest for c in book_data.chapters], []))

	# A similar action should be done with the spine element
	spine = opf.find(".//{http://www.idpf.org/2007/opf}spine")
	map(lambda x: spine.append(x), reduce(lambda x, y: x + y, [c.opf.spine for c in book_data.chapters], []))

	return opf


def generate_nav(book_data):
	"""
	Generation of a new nav file that combines the information from different chapters.

	:param book_data: a data object collecting the necessary information for the creation of the new package file
	:return: Root of the generated nav.xhtml file; and ElementTree Element object
	"""
	ET.register_namespace('', "http://www.w3.org/1999/xhtml")
	ET.register_namespace('epub', "http://www.idpf.org/2007/ops")
	nav = ElementTree(ET.fromstring(NAV % NAV_CSS_NO_NUMBERING))

	navMap = nav.find(".//{http://www.w3.org/1999/xhtml}nav[@id='toc']")
	h2 = SubElement(navMap, "{http://www.w3.org/1999/xhtml}h2")
	h2.text = "Table of Contents"

	# Set the title
	title = nav.findall(".//{http://www.w3.org/1999/xhtml}title")[0]
	title.text = book_data.title + " - Table of Contents"

	# Set the date
	date = nav.findall(".//{http://www.w3.org/1999/xhtml}meta[@name='date']")[0]
	date.set("content", book_data.date.strftime("%Y-%m-%dT%M:%S:00Z"))

	ol = SubElement(navMap, "{http://www.w3.org/1999/xhtml}ol")
	li = SubElement(ol, "{http://www.w3.org/1999/xhtml}li")
	a = SubElement(li, "{http://www.w3.org/1999/xhtml}a")
	a.set("href", "cover.xhtml")
	a.text = "Cover"
	a.set("class", "toc")

	# The landmark part of the nav file has to be changed; there is no explicit cover page
	li_landmark = nav.findall(".//{http://www.w3.org/1999/xhtml}a[@href='Overview.xhtml']")[0]
	li_landmark.set("href", "cover.xhtml")

	for c in book_data.chapters:
		cli = SubElement(ol, "{http://www.w3.org/1999/xhtml}li")
		cli.set("class","tocline")
		ca = SubElement(cli, "{http://www.w3.org/1999/xhtml}a")
		ca.set("href", "%s/cover.xhtml" % c.directory_name)
		ca.text = c.title
		ca.set("class","tocxref")
		cli.append(c.nav.nav)

	return nav


def generate_ncx(book_data):
	"""
	Generation of a new NCX file that combines the information from different chapters.

	:param book_data: a data object collecting the necessary information for the creation of the new package file
	:return: Root of the generated package file; and ElementTree Element object
	"""
	def massage_and_add_toc(toc, order):
		"""
		Add a toc item to `nav_map`, modifying its play order and its @id value. To be used in a `map` function

		:param toc: the item to be added (and ElementTree Element instance)
		:param order: play order value
		"""
		toc.set("playOrder", "%s" % order)
		toc.set("id", "nav%s" % order)
		nav_map.append(toc)

	ET.register_namespace('', "http://www.daisy.org/z3986/2005/ncx/")
	ncx = ElementTree(ET.fromstring(TOC))

	# Set the title
	title    = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}docTitle")[0]
	txt      = SubElement(title, "{http://www.daisy.org/z3986/2005/ncx/}text")
	txt.text = book_data.title

	# Set the authors
	authors    = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}docAuthor")[0]
	txt        = SubElement(authors, "{http://www.daisy.org/z3986/2005/ncx/}text")
	txt.text   = book_data.editors

	# Set the book ID
	meta_id = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}meta[@name='dtb:uid']")[0]
	meta_id.set('content', book_data.id)

	play_order = 2
	nav_map = ncx.find(".//{http://www.daisy.org/z3986/2005/ncx/}navMap")
	assert nav_map is not None
	for c in book_data.chapters:
		map(massage_and_add_toc, c.ncx.toc, range(play_order, play_order+len(c.ncx.toc)))
		play_order += len(c.ncx.toc)

	return ncx


def generate_cover(book_data):
	"""
	Create a cover page: ``cover.xhtml``.
	"""
	# Setting the default namespace; this is important when the file is generated
	ET.register_namespace('', "http://www.w3.org/1999/xhtml")
	cover = ElementTree(ET.fromstring(COVER))

	# Set the title
	title      = cover.findall(".//{http://www.w3.org/1999/xhtml}title")[0]
	title.text = book_data.title

	# Set the authors in the meta
	editors      = cover.findall(".//{http://www.w3.org/1999/xhtml}meta[@name='author']")[0]
	editors.set("content", book_data.editors)

	# Set the title in the text
	title      = cover.findall(".//{http://www.w3.org/1999/xhtml}h1[@id='btitle']")[0]
	title.text = book_data.title

	# Set the editors
	editors      = cover.findall(".//{http://www.w3.org/1999/xhtml}p[@id='editors']")[0]
	editors.text = book_data.editors

	# Set a pointer to the original
	orig      = cover.findall(".//{http://www.w3.org/1999/xhtml}a[@id='ref_original']")[0]
	orig.text = "original documents"
	orig.tag = "span"

	# Set the correct copyright date
	span      = cover.findall(".//{http://www.w3.org/1999/xhtml}span[@id='cpdate']")[0]
	span.text = book_data.date.strftime("%Y")

	return cover



