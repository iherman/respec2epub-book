# -*- coding: utf-8 -*-
"""
Generation of the  :py:class:`ElementTree.Element` objects for the top level configuration data (package, tables of contents, cover).
"""

from rp2epub.templates import PACKAGE, NAV, NAV_CSS_NO_NUMBERING, TOC, COVER
from rp2epub.config import DATE_FORMAT_STRING
from rp2epub.utils import Utils
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, SubElement


def generate_opf(book_data):
	"""
    Generation of a new OPF object, combining the OPF information from the chapters.

    :param book_data: a data object collecting the necessary information for the creation of the new package file
    :return: Root of the generated package file; and :py:class:`ElementTree.Element` object
    """
	def add_manifest_item(the_manifest, bid, href, media_type, properties=None):
		"""
        Creation of a new manifest item. (Function to be used in a 'map')

        :param the_manifest: the whole manifest (parent of the item)
        :param bid: value of @id
        :param href: value of @href
        :param media_type: media type
        :param properties: list of possible values to be added to the `properties` attribute
        """
		item = SubElement(the_manifest, "{http://www.idpf.org/2007/opf}item")
		item.set("id", bid)
		item.set("href", href)
		item.set("media-type", media_type)
		if properties is not None:
			item.set("properties", properties)

	def add_metadata_item(the_opf, path, value, ns="http://purl.org/dc/elements/1.1/"):
		"""
        Add a metadata item.

        :param the_opf: metadata element (parent of the item)
        :param path: element to add the metadata item to; it may be extended with an attribute value in XPath syntax
        :param value: value to be set for the metadata
        :param ns: namespace of used in the path
        """
		item = the_opf.find((".//{%s}" % ns) + path)
		assert item is not None
		item.text = value

	# Parse the raw manifest file
	ET.register_namespace('', "http://www.idpf.org/2007/opf")
	opf = ElementTree(ET.fromstring(PACKAGE))
	# The manifest:
	manifest = opf.find(".//{http://www.idpf.org/2007/opf}manifest")
	metadata = opf.findall(".//{http://www.idpf.org/2007/opf}metadata")[0]

	# Manifest metadata
	add_metadata_item(opf, "title", book_data.title)
	add_metadata_item(opf, "identifier", book_data.id)
	add_metadata_item(opf, "meta[@property='dcterms:modified']", book_data.date.strftime(DATE_FORMAT_STRING), ns="http://www.idpf.org/2007/opf")
	add_metadata_item(opf, "meta[@property='dcterms:date']", book_data.date.strftime(DATE_FORMAT_STRING), ns="http://www.idpf.org/2007/opf")
	for editor in book_data.editors :
		creator = SubElement(metadata, "{http://purl.org/dc/elements/1.1/}creator")
		creator.set("role", "editor")
		creator.text = editor
		creator.tail = "\n    "
	for author in book_data.authors :
		creator = SubElement(metadata, "{http://purl.org/dc/elements/1.1/}creator")
		creator.set("role", "author")
		creator.text = author
		creator.tail = "\n    "

	# Add the static entries
	add_manifest_item(manifest, "nav", "nav.xhtml", "application/xhtml+xml", properties="nav")
	add_manifest_item(manifest, "start", "cover.xhtml", "application/xhtml+xml")
	add_manifest_item(manifest, "ncx", "toc.ncx", "application/x-dtbncx+xml")

	# Here is the real meat: collect all the chapter manifest items, and add them to the local manifest
	map(lambda x: manifest.append(x), reduce(lambda x, y: x + y, [c.opf.manifest for c in book_data.chapters], []))

	# A similar action should be done with the spine element
	spine = opf.find(".//{http://www.idpf.org/2007/opf}spine")
	map(lambda x: spine.append(x), reduce(lambda x, y: x + y, [c.opf.spine for c in book_data.chapters], []))

	return opf


# noinspection PyPep8Naming
def generate_nav(book_data):
	"""
    Generation of a new NAV object, combining the OPF information from the chapters.

    :param book_data: a data object collecting the necessary information for the creation of the new package file
    :return: Root of the generated nav.xhtml file; an :py:class:`ElementTree.Element` object
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
	date.set("content", book_data.date.strftime(DATE_FORMAT_STRING))

	ol = SubElement(navMap, "{http://www.w3.org/1999/xhtml}ol")
	li = SubElement(ol, "{http://www.w3.org/1999/xhtml}li")
	li.set("class", "tocline")
	a = SubElement(li, "{http://www.w3.org/1999/xhtml}a")
	a.set("href", "cover.xhtml")
	a.text = "Cover"
	a.set("class", "toc")

	# The landmark part of the nav file has to be changed; there is no explicit cover page
	li_landmark = nav.findall(".//{http://www.w3.org/1999/xhtml}a[@href='Overview.xhtml']")[0]
	li_landmark.set("href", "cover.xhtml")

	for c in book_data.chapters:
		cli = SubElement(ol, "{http://www.w3.org/1999/xhtml}li")
		cli.set("class", "tocline")
		ca = SubElement(cli, "{http://www.w3.org/1999/xhtml}a")
		ca.set("href", "%s/cover.xhtml" % c.target)
		ca.text = c.title
		ca.set("class", "tocxref")
		cli.append(c.nav)

	return nav


# noinspection PyPep8
def generate_ncx(book_data):
	"""
    Generation of a new NCX object, combining the OPF information from the chapters.

    :param book_data: a data object collecting the necessary information for the creation of the new package file
    :return: Root of the generated package file; an :py:class:`ElementTree.Element` object
    """
	def massage_and_add_toc(toc, order):
		"""
        Add a toc item to `nav_map`, modifying its play order and its @id value. To be used in a `map` function

        :param toc: the item to be added (and ElementTree Element instance)
        :param order: play order value (essentially: index into the array of chapter's toc entries, shifted with the chapter number)
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
	txt.text   = Utils.editors_to_string(book_data.editors)

	# Set the book ID
	meta_id = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}meta[@name='dtb:uid']")[0]
	meta_id.set('content', book_data.id)

	play_order = 2
	nav_map = ncx.find(".//{http://www.daisy.org/z3986/2005/ncx/}navMap")
	assert nav_map is not None
	for c in book_data.chapters:
		map(massage_and_add_toc, c.ncx, range(play_order, play_order + len(c.ncx)))
		play_order += len(c.ncx)

	return ncx


# noinspection PyPep8
def generate_cover(book_data):
	"""
    Create a cover page object for ``cover.xhtml``.

    :param book_data: a data object collecting the necessary information for the creation of the new package file
    :return: Root of the generated package file; an :py:class:`ElementTree.Element` object
    """
	# Setting the default namespace; this is important when the file is generated
	ET.register_namespace('', "http://www.w3.org/1999/xhtml")
	cover = ElementTree(ET.fromstring(COVER))

	# Set the title
	title      = cover.findall(".//{http://www.w3.org/1999/xhtml}title")[0]
	title.text = book_data.title

	# Set the authors in the meta
	editors = cover.findall(".//{http://www.w3.org/1999/xhtml}meta[@name='author']")[0]
	editors.set("content", Utils.editors_to_string(book_data.editors))

	# Set the title in the text
	title      = cover.findall(".//{http://www.w3.org/1999/xhtml}h1[@id='btitle']")[0]
	title.text = book_data.title

	# Set the editors
	editors      = cover.findall(".//{http://www.w3.org/1999/xhtml}p[@id='editors']")[0]
	editors.text = book_data.editors

	if len(book_data.editors) != 0 :
		editors = cover.findall(".//{http://www.w3.org/1999/xhtml}p[@id='editors']")[0]
		editors.text = Utils.editors_to_string(book_data.editors)

	# Set the authors
	if len(book_data.authors) != 0 :
		authors = cover.findall(".//{http://www.w3.org/1999/xhtml}p[@id='authors']")[0]
		authors.text = Utils.editors_to_string(book_data.authors, editor=False)

	# Set a pointer to the original
	orig      = cover.findall(".//{http://www.w3.org/1999/xhtml}a[@id='ref_original']")[0]
	orig.text = "original documents"
	orig.tag = "span"

	# Set the correct copyright date
	span      = cover.findall(".//{http://www.w3.org/1999/xhtml}span[@id='cpdate']")[0]
	span.text = book_data.date.strftime("%Y")

	return cover



