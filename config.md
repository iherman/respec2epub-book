# The config file

A JSON file with one object.

## Top level properties:

* `title` (required): Title of the whole book. Required
* `id` (required): ID of the book, to be added to the package file. Required
* `target` (required?): Target directory (relative to the current directory) for the unpacked book. The packed version will use the same name as basename
*  `chapters` (required): Array of chapter objects

## Chapter properties

* `source` (required): Source directory for a chapter; a file name relative to the current directory when running the script. The file name is checked: if
  * it is a directory name: the content is copied to target; otherwise
  * it is a zipped file: the content is unzipped to the target; the basename of the file is used as a directory name
 