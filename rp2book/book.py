# -*- coding: utf-8 -*-
"""
The main controller classes, performing all the steps necessary to produce the book.
"""

from .chapter import Chapter
from .package import generate_opf, generate_nav, generate_ncx, generate_cover
from .overview import convert_overviews
from rp2epub.utils import HttpSession
from rp2epub import R2EError
import sys
import urlparse
import tempfile
import zipfile
import shutil
import os
from StringIO import StringIO
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


# noinspection PyPep8
# noinspection PyBroadException,PyUnusedLocal
class Config(object):
	"""
    “Configuration” class, collecting all necessary information on the book (and its chapters) that are necessary for
    further processing. Most of the data are collected in the initialization phase by extracting it from the
    JSON or YAML data provided by the user, other data are refreshed/added by the :py:class:`Book` instance making use of
    this class.

    The only processing part of this class is establishing the chapter sources. If the sources are epub files (either
    locally or via an HTTP(S) URI), the content is unpacked on the fly into a temporary directory. This means that,
    as far as the upper layers are concerned, chapter sources are always viewed as directory names on the local file system.

    Before processing further, a sanity check on the configuration file is also performed, raising an exception in case
    of a problem. The attributes of the class are:

    :py:attr:`title`: Title of the book

    :py:attr:`id`: Unique ID of the book

    :py:attr:`target`: Target name of the generated EPUB and/or the generated folder

    :py:attr:`sources`: Array of chapter references, referring to folders on the local file system

    :py:attr:`chapters`: Array of :py:class:`.chapter.Chapter` references, filled by the enclosing object at initialization time

    :py:attr:`date`: Date of publication, filled by the enclosing object at initialization time

    :py:attr:`toRemoveDir`: Temporary directory storing, possibly, unpacked epub instances for further processing. The directory is removed at closure, see :py:meth:`.close`.

    :py:attr:`editors`: Collected editors, filled by the enclosing object at initialization time

    :py:attr:`opf`: An :py:class:`ElementTree.Element` object, representing the final OPF file, filled by the enclosing object at initialization time

    :py:attr:`nav`: An :py:class:`ElementTree.Element` object, representing the final NAV file, filled by the enclosing object at initialization time

    :py:attr:`ncx`: An :py:class:`ElementTree.Element` object, representing the final NCX file, filled by the enclosing object at initialization time

    :py:attr:`ncx`: An :py:class:`ElementTree.Element` object, representing the final cover page, filled by the enclosing object at initialization time

    :py:attr:`uri_patterns`: Array of (`from`,`to`) pairs of URI-s (`to` is typically a relative URI) to replace URI references in the various Overview files.

    """
	# noinspection PyPep8
	def __init__(self, json_config_source):
		"""
        :param json_config_source: file name for the json configuration file
        :type json_config_source: string
        :raises: :py:exc:`.R2BError`: raised if the JSON parsing leads to problems, if the configuration is incorrect, or if the HTTP(S) access or the unpacking has issues (if applicable)
        """
		try:
			json_config = self._parse_config(json_config_source)
		except:
			from . import R2BError
			(ty, value, traceback) = sys.exc_info()
			raise R2BError("Configuration file parsing issues in '%s': %s" % (json_config_source, value))

		# Sanity check on the configuration file
		self._check_config(json_config)

		self.title  = json_config["title"]
		self.id     = json_config["id"]
		self.target = json_config["target"]

		# All these must be filled by subsequent calls
		self.chapters     = []
		self.sources      = []
		self.toRemoveDir  = ""
		self.date         = None
		self.editors      = []
		self.authors      = []
		self.opf          = None
		self.nav          = None
		self.ncx          = None
		self.cover        = None
		self.uri_patterns = [] if "uripatterns" not in json_config else [tuple(t) for t in json_config["uripatterns"]]

		self._extract_data(json_config)

	def _extract_data(self, json_config):
		"""
        Extract books into a temporary directory if the source refers to an EPUB instance rather than a directory.
        The `sources` array in the object will contain, after this processing, the reference to either the original source (in case that
        was a directory) or the temporary directory that contains the unpacked book.

        Processing must end with a call to :py:meth:`close` which ensures a proper closure/removal of the temporary
        directory.

        :param json_config: the original JSON configuration file with the array of chapter references
        """
		# If this detects a problem, an exception is raised!

		# This is the temporary directory where unpacked books are temporarily placed
		self.toRemoveDir = tempfile.mkdtemp(prefix="rp2books_")

		def create_source(source):
			"""
            If source is a directory, it is returned unchanged. Otherwise it is considered to be a zip file,
            and is unzipped into the temporary directory.

            :param source: source name, as provided in the json_config
            :return: real source path, to be used by further processing
            """
			def close_and_raise(error):
				"""
                Close the class (ie, remove the temporary directory) and raise an error

                :param error: error message string
                """
				from . import R2BError
				self.close()
				raise R2BError(error)

			if os.path.isdir(source):
				return source
			elif os.path.isfile(source):
				# Need the basename, this will be used as a source directory name
				dir_name = os.path.join(self.toRemoveDir, os.path.basename(source).rsplit(".", 1)[0])
				# This directory has to be created
				os.mkdir(dir_name)
				try:
					with zipfile.ZipFile(source) as the_book:
						the_book.extractall(dir_name)
					return dir_name
				except zipfile.BadZipfile:
					close_and_raise("'%s' is not a correct zip file" % source)
			else:
				# last possibility: this is a URL
				try:
					session = HttpSession(source, raise_exception = True)
					if session.media_type != "application/epub+zip":
						close_and_raise("'%s' is not of the correct media type" % source)
					else:
						# The file has to be downloaded to the temporary directory...
						# First, get the 'logical' name that will be used
						path = urlparse.urlparse(source).path
						# this should not happen, but one may never know
						path = (path if path[-1] != '/' else path[:-1]).split('/')[-1]

						# Place to download the zip file to:
						downloaded_file = os.path.join(self.toRemoveDir, "http_download_" + path)
						# Place to unzip the zip file to
						dir_name = os.path.join(self.toRemoveDir, path.rsplit(".", 1)[0])

						# Download the file from HTTP:
						with open(downloaded_file, 'w') as downloaded_book:
							downloaded_book.write(session.data.read())

						# Unzip it and store it
						with zipfile.ZipFile(downloaded_file) as the_book:
							the_book.extractall(dir_name)
						return dir_name
				except zipfile.BadZipfile:
					close_and_raise("'%s' is not a correct zip file" % source)
				except R2EError as e:
					close_and_raise("Problem accessing '%s': %s" % (source, e.value))
				except:
					(ty, value, traceback) = sys.exc_info()
					close_and_raise("Problem accessing '%s': %s" % (source, value))

		self.sources = [create_source(d) for d in json_config["chapters"]]

	def close(self):
		"""
        Clean up the temporary area.

        Note that the object has `__enter__` and `__exit__` methods (the latter invoking this method), i.e., the object can be used as a context manager.
        In other words, the object can be (and should be) used via the::

           with Config(json_file) as config:
             ...

        pattern, which ensures that this method will be invoked even if an exception was raised somewhere.
        """
		try:
			shutil.rmtree(self.toRemoveDir)
		except:
			# This means there was no such directory yet; this exception can be ignored
			pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()
		return False

	@staticmethod
	def _check_config(config):
		"""
        Check the config file. In case of problems an error message is raised in the form of an exception.

        :param config: config file to check
        :raises: :py:exc:`.R2BError`
        """
		from . import R2BError
		error = []
		if "title" not in config:
			error.append("No title is provided")
		if "id" not in config:
			error.append("No ID is provided")
		if "chapters" not in config or len(config["chapters"]) == 0:
			error.append("No chapters are provided")
		chapter_sources = []
		for c in config["chapters"]:
			if c in chapter_sources:
				error.append("Duplicate chapter (%s)" % c)
			else:
				chapter_sources.append(c)
		if len(error) != 0:
			raise R2BError("Error in configuration: " + (";".join(error)))
		return config

	@staticmethod
	def _parse_config(config_file):
		"""
        Parsing the config file, which may either be a JSON file (ie, suffix ".js" or ".json") or a YAML file (ie, suffix ".yaml").

        In fact, the fallback format is also JSON, so if no suffix is matched, that is used.

        :param config_file:
        :return: parsed config
        :rtype: dict
        """
		if config_file.endswith(".yaml"):
			import yaml
			with open(config_file) as f:
				return yaml.load(f)
		else:
			import json
			with open(config_file) as f:
				return json.load(f)

	def __repr__(self):
		retval = ""
		retval += "Title: %s\n" % self.title
		retval += "ID: %s\n" % self.id
		retval += "Date: %s\n" % self.date
		retval += "Editors: %s\n" % self.editors
		retval += "Authors: %s\n" % self.editors
		retval += "Sources: %s\n" % self.sources
		retval += "Target: %s\n" % self.target
		retval += "Directory to be removed: %s\n" % self.toRemoveDir
		retval += "URI replacement patterns: %s\n" % self.uri_patterns
		retval += "Chapter objects %s\n" % self.chapters
		retval += "Overall OPF object %s\n" % self.opf
		retval += "Overall NAV object %s\n" % self.nav
		retval += "Overall NCX object %s\n" % self.ncx
		retval += "Overall Cover object %s\n" % self.cover
		return retval


class Book:
	"""
    Top level creator of the the combined book. The following steps are performed:

    1. a :py:class:`.chapter.Chapter` object is created for each chapter, yielding information like individual table of contents, date, authors, etc
    2. the “top level” configuration information are created (through calls to the :py:func:`.package.generate_opf`, :py:func:`.package.generate_nav`, :py:func:`.package.generate_cover`, and :py:func:`.package.generate_ncx` functions), yielding a series of :py:class:`ElementTree.Element` objects
    3. the various files are copied and/or generated into a target directory (in the :py:meth:`_generate_files` method)
    4. the `Overview.xhtml` files are modified by changing the mutual references (through the :py:func:`.overview.convert_overviews` function)
    5. the final target is zipped into an `epub` file (if applicable)
    6. the target directory is removed (if applicable)

    :param json_config: file name for the json or yaml configuration file
    :type json_config: str
    """
	# noinspection PyPep8
	def __init__(self, json_config, package, folder):
		with Config(json_config) as config:
			# Extract information for chapters
			config.chapters = [Chapter(source) for source in config.sources]

			# Some generic metadata
			config.date = max([c.date for c in config.chapters])

			def intelligent_concat(x, y):
				"""Add elements of the second list to the first only if it is not there already.
                Using sets was not really an option because sets do not necessary keep the order, and this was simpler then creating a separate OrderedSet class.
                :param x: array
                :param y: array
                :returns: the "concatenated" array
                """
				return x + [c for c in y if c not in x]
			config.editors = reduce(intelligent_concat, [c.editors for c in config.chapters], [])
			config.authors = reduce(intelligent_concat, [c.authors for c in config.chapters], [])

			config.ncx   = generate_ncx(config)
			config.nav   = generate_nav(config)
			config.cover = generate_cover(config)
			config.opf   = generate_opf(config)

			self._generate_files(config)
			convert_overviews(config)

			# Finalizing the output: possibly generate an epub file, and remove the sources
			if package:
				# We have to get a list of all the files to be added
				files = []
				container_path = os.path.join("META-INF","container.xml")
				for (dirpath, dirnames, filenames) in os.walk(config.target):
					for f in filenames:
						source = os.path.join(dirpath, f)
						# Remove the files that must be on top, ie, must be put into the zip file explicitly; see below
						if f == "mimetype" or source.endswith(container_path):
							continue
						target = source.replace(config.target, "", 1)
						target = target if target[0] != os.sep else target[len(os.sep):]
						files.append((source, target))

				with zipfile.ZipFile(config.target + '.epub', 'w') as the_book:
					# These two files should be on the top of the zip file, the first without compression
					# (This is part of the epub spec)
					the_book.write(os.path.join(config.target, "mimetype"), "mimetype", zipfile.ZIP_STORED)
					the_book.write(os.path.join(config.target, container_path), container_path)
					# The rest of the content can just be done as it comes
					for (source, target) in files: the_book.write(source, target)
			if not folder:
				shutil.rmtree(config.target)

		# This is mainly needed for debug...
		self._config = config

	@property
	def config(self):
		"""The overall book data, collected from the configuration file and the chapters."""
		return self._config

	# noinspection PyPep8,PyUnresolvedReferences
	@staticmethod
	def _generate_files(book_data):
		"""
        Generate all the files. This means

        1. The target folder is created
        2. Each chapter is copied into the target, though removing the `META-INF` and `mimetype` files
        3. Style files and logos, needed for the overall cover page, are copied into the top level folder
        3. The various top level configuration files (OPF, NAV, NCX, and cover) are added to the folder (serializing the corresponding ElementTree.Element objects)

        :param book_data: The book data
        :type book_data: :py:class:`.Config` instance
        """
		# All the file copying business...
		# The target directory should either be created, if not yet there. If it is there, it should be emptied first
		# Note that the target path is a simple file name, not a full path!

		# Lists of various file names with different actions
		# Files to copy from the first chapter to the top level
		to_copy   = [os.path.join("META-INF","container.xml"),
					 "mimetype",
					 os.path.join("StyleSheets","TR","base.css"),
					 os.path.join("Icons", "w3c_main.png")
					 ]
		# Files to remove from each chapter
		to_remove = ["mimetype", "nav.xhtml", "package.opf", "toc.ncx"]
		# Files to add to the top level; the values are ElementTree Elements; the third item is the default
		# file name, to make things look proper when the XML is serialized.
		to_add    = [
			(book_data.opf, "package.opf", "http://www.idpf.org/2007/opf"),
			(book_data.nav, "nav.xhtml", "http://www.w3.org/1999/xhtml"),
			(book_data.ncx, "toc.ncx", "http://www.daisy.org/z3986/2005/ncx/"),
			(book_data.cover, "cover.xhtml", "http://www.w3.org/1999/xhtml")
		]

		# The target directory for the book
		target = book_data.target

		# The target directory should be emptied and created
		try:
			shutil.rmtree(target)
		except OSError:
			pass
		os.makedirs(target)

		# Each chapter, ie, the corresponding book directory, must be copied to the target
		for c in book_data.chapters:
			c_target = os.path.join(target, os.path.basename(c.source))
			shutil.copytree(c.source, c_target)

			# some files should be removed from that target, though
			shutil.rmtree(os.path.join(c_target, "META-INF"))
			for f in to_remove: os.remove(os.path.join(c_target, f))

		# Some elements should be copied from one of the chapters into the 'main' part
		s_chapter = book_data.chapters[0].source
		for tc in to_copy:
			# Copy one file, possibly creating the directories on the fly
			if os.path.dirname(tc) != "":
				os.makedirs(os.path.join(target, os.path.dirname(tc)))
			shutil.copyfile(os.path.join(s_chapter, tc), os.path.join(target, tc))

		# Write the top level admin files, generated from the chapters, into the the final directory (serializing the content on the fly)
		for (f_element_tree, f_name, f_namespace) in to_add:

			ET.register_namespace('', f_namespace)
			content = StringIO()
			f_element_tree.write(content, encoding="utf-8", xml_declaration=True, method="xml")
			with open(os.path.join(target, f_name), "w") as f_file:
				f_file.write(content.getvalue())
			content.close()

	def __repr__(self):
		return repr(self.config)





