# Notes on book generation

There is a configuration file that contains
* Title of overall publication
* Authors of overall publication
* ID for the overall publication
* Date of overall publication
* For each chapter:
	* file name for the directory
	* title of the chapter

Out of these, the following fields may be extracted:

* Authors of overall publication: Copy the fields from the respective cover (or package file), remove the '(Editors)' text from the beginning, and concatenate the whole thing
* Date of overall publication: take the dates from the package file, and take the later date
* Title of each publication

## Steps to be taken

* [ ] All folders must be copied under the same folder
* [ ] Copy one of the `Stylesheet` folders to the top level (essentially, to get the `base.css` file)
* [ ] Copy one of the `Icons` folders to the top level (to get the logos/icons)
* [ ] Create (or copy) the META-INF folder with its content
* [ ] Create (or copy) the mimetype file
* [ ] Each chapter should be retrieved and the configuration file completed (see above)
* [ ] Create a `package.opf` file
	* [ ] The metadata part is probably generated from the configuration
	* [ ] Copy the manifest content of the individual package files, modifying
		* [ ] `href` values should be extended to include the directory name at the front
		* [ ] `id` values should be extended to include the directory name at the front with a '-'
		* [ ] remove `nav.xhtml`, `toc.ncx`
	* [ ] Copy the spine content of the individual package files, modifying the `idref` values by adding the directory name with a '-' before the values. Precede the list with a reference to `cover.xhtml` (with id `start`)
	* Add the `nav.xhtml`, `toc.ncx`, and `cover.xhtml` (with id `start`) files to the new package file
* [ ] Create the `nav.xhtml`
	* [ ] Add a `cover.xhtml` reference as the first entry of the TOC
	* [ ] Content of each individual nav item in the chapters' `nav.xhtml` is
		* [ ] added as a separate `<li>` element of an overall `<ol>`
		* [ ] add the title of the respective book (with numbering)
		* [ ] clone the full `ul` or `ol`
		* [ ] all the references are modified by adding the directory name on the front
		* [ ] copy the updated cloned element to the current position
	* [ ] Modify the `bodymatter` to include an `Overview` entry for each chapter (with the correct path)
* [ ] Create the `toc.ncx`
	* [ ] Meta, `<docTitle>`, and `<docAuthor>` have to use the ID in the configuration files
	* [ ] Add a local reference to a cover page as a first entry
	* [ ] List, in order, the entries of the chapters' `toc.ncx` files but
		* [ ] The references must be updated
		* [ ] the `navorder` and `id` must be recalculated. Care should be taken to rename the `cover` value as an `id`
* [ ] Create the cover page
	* [ ] The title should come from the configuration file
	* [ ] In contrast to the usual cover, there should be no characterization (Rec, etc) in the template
	* [ ] The author and date should come from the configuration file
* [ ] As a cleanup, some files may be removed from the chapters (reduce epubcheck warnings...)
	* [ ] mimetype
	* [ ] toc.ncx, nav.xhtml
	* [ ] META-INF directory
* [ ] Zip the content...

## Optimization, beautification
* Go through each Overview files, and change the URLs to a relative one. This can be done via textual change, using a change set in the configuration file...
* The toc.ncx could be improved by providing a two level TOC; but may not be worth the trouble
