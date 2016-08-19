# The config file

A JSON file with one object.

## Top level properties:

* `title` (required): Title of the whole book. Required
* `id` (required): ID of the book, to be added to the package file. Required
* `target` (required): Target directory (relative to the current directory) for the unpacked book. The packed version will use the same name as basename 
* `chapters` (required): Array of chapter references (in order). The reference can be
    * a directory name: the content is an unzipped version of the generated EPUB (the content is *copied* to the target)
    * a local EPUB file (with an `.epub` extension), the content of which is unzipped into a local, temporary file (and removed after processing)
    * a URL to a remote EPUB file (with an `.epub` extension), the content of which is downloaded and unzipped into a local, temporary file (and removed after processing)
* `uripatterns` (optional): Array of tuples (represented as two-element arrays in JSON) of “from” and “to” pairs. The
  “from” is an absolute URL (typically a dated URL in the W3C TR space), and “to” is the corresponding relative URL
  to be used as a reference to another chapter within the same generated book. The goal is to ensure that cross references
  among chapters happen within the same book, instead of using absolute references.
 
 