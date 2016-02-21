# Notes on book generation

## To Dos

## Top level driver part:

* [ ] All the files are created in a folder
* [ ] The config file contains a "target", which is the 'short name' of the overall book
* Depending on whether the unpacked version is also required or not, the target for the unpacked version is either the local directory (named with 'short name') or a temporary (and unique) subdirectory thereof
* The first step is to get each chapter unpacked into the target area (first option wins)
    * [ ] if a file name is given in the configuration's "source" field and it is a directory, that is copied into the target area; the basename of the source will be the name of the directory within the target
    * [ ] if a file name is given in the configuration's "source" field, and it is a file, it is considered to be an ebook, will be unpacked with the result put into the target area; the basename without suffix will be the directory name
    * [ ] if a "url" field is provided, it will be used as a reference to an epub file, and treated like the previous item (this may be for later)
* [ ] after all processing is done, if a book is required, the the target folder is packed and stored
* [ ] if the file is not required, the corresponding directory is removed


## Steps to be taken for the generation of content

* [x] All folders must be copied under the same folder
* [x] Copy one of the `Stylesheet` folders to the top level (essentially, to get the `base.css` file)
* [x] Copy one of the `Icons` folders to the top level (to get the logos/icons)
* [x] Create (or copy) the META-INF folder with its content
* [x] Create (or copy) the mimetype file
* [x] Each chapter should be retrieved and the configuration file completed (see above)
* [x] Create a `package.opf` file
	* [x] The metadata part is probably generated from the configuration
	* [x] Copy the manifest content of the individual package files, modifying
		* [x] `href` values should be extended to include the directory name at the front
		* [x] `id` values should be extended to include the directory name at the front with a '-'
		* [x] remove `nav.xhtml`, `toc.ncx`
	* [x] Copy the spine content of the individual package files, modifying the `idref` values by adding the directory name with a '-' before the values. Precede the list with a reference to `cover.xhtml` (with id `start`)
	* [x] Add the `nav.xhtml`, `toc.ncx`, and `cover.xhtml` (with id `start`) files to the new package file
* [x] Create the `nav.xhtml`
	* [x] Add a `cover.xhtml` reference as the first entry of the TOC
	* [x] Content of each individual nav item in the chapters' `nav.xhtml` is
		* [x] added as a separate `<li>` element of an overall `<ol>`
		* [x] add the title of the respective book (with numbering)
		* [x] clone the full `ul` or `ol`
		* [x] all the references are modified by adding the directory name on the front
		* [x] copy the updated cloned element to the current position
	* [x] Modify the `bodymatter` to include an `Overview` entry for each chapter (with the correct path)
* [x] Create the `toc.ncx`
	* [x] Meta, `<docTitle>`, and `<docAuthor>` have to use the ID in the configuration files
	* [x] Add a local reference to a cover page as a first entry
	* [x] List, in order, the entries of the chapters' `toc.ncx` files but
		* [x] The references must be updated
		* [x] the `navorder` and `id` must be recalculated. Care should be taken to rename the `cover` value as an `id`
* [x] Create the cover page
	* [x] The title should come from the configuration file
	* [x] In contrast to the usual cover, there should be no characterization (Rec, etc) in the template
	* [x] The author and date should come from the configuration file
* [x] As a cleanup, some files may be removed from the chapters (reduce epubcheck warnings...)
	* [x] mimetype
	* [x] toc.ncx, nav.xhtml
	* [x] META-INF directory


## Future Optimization, beautification
* [ ] Go through each Overview files, and change the URLs to a relative one. This can be done via textual change, using a change set in the configuration file...
* [ ] The toc.ncx could be improved by providing a two level TOC; but may not be worth the trouble...
