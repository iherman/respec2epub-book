# The config file

A JSON file with one object.

## Top level properties:

* `title` (required): Title of the whole book. Required
* `id` (required): ID of the book, to be added to the package file. Required
* `target` (required?): Target directory (relative to the current directory) for the unpacked book. The packed version will use the same name as basename
*  `chapters` (required): Array of chapter references:
    * if it is a directory name: the content is an unzipped version of the generated EPUB (the content is *copied* to the target)
    * if it is either a local or remote EPUB file (with an `.epub` extension), the content is unzipped into a local, temporary file
 