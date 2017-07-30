# arcmap_2maps_per_page
Python script to generate PDF map series with 2 maps per page

*If this project interests you and you want more information or you
need help with it please contact me, if I don't get feedback I will
not continue to improve it. -- brian@wildsong.biz*

This script was written for a project that initially required a 22"x34"
sheet with 2 map per sheet and 4 total sheets.  Since ArcMap
10.5.1 doesn't support this directly with Data Driven Pages, I wrote
this code.

Halfway through the project it turned out that the first 6 maps
needed to be on the first three sheets and that maps 7 and 8 each
needed a separate full sheet. More code.

Then it turned out we needed two separate map sets. One with some
layers turned on and the other with different layers... so more code.

When I decided to publish it I took most of the hard coded constants
out of the python and for convenience put them into a JSON formatted
text file called settings.json.

# Code

Runs under the python that comes with ArcMap 10.5, version 2.7.13.
I have also tested it under Anaconda python 3.x that has been modified
to use ESRI's arcpy module.

## Files

* generate_map_series.py - Run this to generate a series of PDF files
* utils.py - extra code imported by generate_map_series.py
* settings.json - a sample control file used as input for the script
* testlayout.mxd - a sample ArcMap MXD file
* indexforddp - describes the maps to be generated (a shapefile)
* places - just some dots (another shapefile)

## How to run it

Open a command window, navigate to where you downloaded and type like this.

 ````bash
 python generate_map_series.py settings.json
 ````

If python is not on your path, use the full path, for example,

 ````bash
 C:\Python27\ArcGISx6410.5\python generate_map_series.py settings.json
 ````

I don't have a python toolbox set up for it, for this tool that would
just be extra work right now. I run it from the command line. This has
a bonus - it does not tie up ArcMap while it runs, I can immediately
go back to mapping while it cranks out 10 or 20 maps in background.

## What it does

Given a json file with settings, it reads an MXD file.  Using
information from the settings and the MXD, it generates a series of
PDF files.

## What it looks for in the MXD file

The MXD file has to have two frames defining the two maps in your
layout.  Optionally there can be a third to define a locator map.

The MXD has to have the second frame set to use a "data driven pages" index.
The script will read a "layout" column to decide it it needs to generate a one-
or two-map page.

The index feature class can define where the locator map should be
rendered on each page, it uses two columns for this "loc_map_x" and
"loc_map_y". The numbers you put in these columns are just in page
units (inches for me) with the origin at the lower left corner.

## Other notes

I used the "credits" field in the data frame is just a way to insert
some text into the layout that I can control from python. In my example
it puts "Map N" under each map, where "N" is the page number 1...5.

## Sample layout

This is what one page from the sample MXD looks like.

![Sample topo maps 1 and 2](https://github.com/Geo-CEG/arcmap_2maps_per_page/blob/master/map_series_sample.png)

### Multiple maps

In the data driven pages index (the shapefile called "indexforddp" in
this repo) the column "layout" is set to 2 for this page so there are
2 maps. If it were set to 1 then the top map would be removed and the
lower one would expand to fill the printable area.

### Wandering locator map

In my example, I move the little locator map around just to show how
it's done. I wish I could leave the locator fixed in one location on
my layouts but sometimes it ends up obscuring important details on one
map in a series so I put this feature in to allow for that.

The sample generates two series, one with a topo layer as the basemap
and one with an aerial photo as the basemap.

# Additional resources

See the article that inspired me to try this project, [Combining data driven pages with pythona and arcpy mapping](https://blogs.esri.com/esri/arcgis/2010/12/14/combining-data-driven-pages-with-python-and-arcpy-mapping/)

There are a lot of options for the exportToPDF function.
Refer to [ExportToPDF](https://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-mapping/exporttopdf.htm) at ESRI web site
