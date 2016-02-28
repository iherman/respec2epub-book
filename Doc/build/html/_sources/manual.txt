.. Respec to EPUB documentation master file, created by
   sphinx-quickstart on Wed Aug 12 15:42:46 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Command line tool manual
========================


When using the command line tool, the result is an EPUB3 file in the current folder (with the ``.epub`` suffix), and whose name is provided
by the configuration file. If requested, the folder will also include the unpacked version of the generated EPUB.


This script that can be invoked from the command as follows::

    usage: rp2book [-h] [-r] [-b] [-f] [-t] config

    Generate EPUB3 for a collection of EPUB3 documents, themselves generated from W3C TR documents
    originally in respec format.

    positional arguments:
        config        file name for the JSON configuration file

    optional arguments:
      -h, --help      show this help message and exit
      -b, --book      Create an EPUB3 package
      -f, --folder    Create a folder with the book content


