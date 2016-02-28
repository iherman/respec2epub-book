Configuration file
==================

A JSON file with one object.

Top level properties:
---------------------

-  ``title`` (required): Title of the whole book. Required
-  ``id`` (required): (Unique) ID of the book, to be added to the package file.
   Required
-  ``target`` (required): Target (relative to the current directory). The target will be used to create
   the final, unpacked directory (if required) and (using the ``.epub`` suffix) the EPUB file, if required.
-  ``chapters`` (required): Array of chapter references (in order). The reference can be

   -  a directory name: the content is an unzipped version of
      the generated EPUB (the content is *copied* to the target)
   -  a local EPUB file (with an ``.epub``
      extension), the content of which is unzipped into a local, temporary file (and removed after processing)
   -  a URL to a remote EPUB file (with an ``.epub``
      extension), the content of which is downloaded and unzipped into a local, temporary file (and removed after processing)

- ``uripatterns`` (optional): Array of tuples (represented as two-element arrays in JSON) of “from” and “to” pairs. The
  “from” is an absolute URL (typically a dated URL in the W3C TR space), and “to” is the corresponding relative URL
  to be used as a reference to another chapter within the same generated book. The goal is to ensure that cross references
  among chapters happen within the same book, instead of using absolute references.


Example
-------

The following example is for the collection of the “CSV on the Web” technology suite, where some of the generated EPUB files are
stored on a local disc, whereas some are extracted from the Web::

 {
     "title"       : "CSV on the Web",
	 "id"          : "https://www.w3.org/dpub/ebooks/csvw.epub",
	 "target"      : "csvw",
	 "chapters"    : [
	 	 "/User/ivan/W3C/WWW/TR/2016/NOTE-tabular-data-primer-20160225/tabular-data-primer.epub",
		 "/User/ivan/W3C/WWW/TR/2015/REC-tabular-data-model-20151217/tabular-data-model.epub",
		 "/User/ivan/W3C/WWW/TR/2015/REC-tabular-metadata-20151217/tabular-metadata.epub",
		 "/User/ivan/W3C/WWW/TR/2015/REC-csv2json-20151217/csv2json.epub",
		 "/User/ivan/W3C/WWW/TR/2015/REC-csv2rdf-20151217/csv2rdf.epub",
		 "https://www.w3.org/TR/2016/NOTE-csvw-html-20160225/csvw-html.epub",
		 "https://www.w3.org/TR/2016/NOTE-csvw-ucr-20160225/csvw-ucr.epub"
	 ],
	 "uripatterns" : [
		["http://www.w3.org/TR/2015/REC-tabular-data-model-20151217/", "../tabular-data-model/"],
		["http://www.w3.org/TR/2015/REC-tabular-metadata-20151217/", "../tabular-metadata/"],
		["http://www.w3.org/TR/2015/REC-csv2json-20151217/", "../csv2json/"],
		["http://www.w3.org/TR/2015/REC-csv2rdf-20151217/", "../csv2rdf/"],
		["http://www.w3.org/TR/2016/NOTE-csvw-html-20160225/", "../csvw-html/"],
		["http://www.w3.org/TR/2016/NOTE-tabular-data-primer-20160225/", "../tabular-data-primer/"]
	 ]
 }




