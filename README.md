# Introduction

GPML2SVG is a command line and Python API for the conversion of pathways marked up 
using [GPML][gpml] to SVG.

The command-line interface is currently basic. Simply call the script with the name of the 
GPML file to convert. The resulting SVG will be saved using the same name, with the
extension change to `.svg`. The resulting SVG is marked up with object identifiers, 
and links to relevant databases.

The python interface offers a single function call to which you can optionally provide
colouring information (for data visualisation) and links for custom XRefs.

The sofware is in development as an extension to [MetaPath][metapath-github].

The current development focus is on providing synonym-linking (to allow data to be provided 
using different identifiers to those in the map) and an improved command line interface. 
Please [report bugs and issues][gpml2svg-github-issues]

# License

GPML2SVG is available free for any use under the [New BSD license](http://en.wikipedia.org/wiki/BSD_licenses#3-clause).

# Related software

> To draw pathways in GPML you can use [PathVisio][pathvisio]. A public collection of pathways is available 
via [WikiPathways][wikipathways]. 

 [metapath-github]: https://github.com/mfitzp/metapath
 [gpml2svg-github-issues]: https://github.com/mfitzp/gpml2svg/issues

 [pathvisio]: http://www.pathvisio.org/
 [wikipathways]: http://wikipathways.org/
 [gpml]: http://www.wikipathways.org/index.php/Help:Frequently_Asked_Questions#What_is_GPML.3F