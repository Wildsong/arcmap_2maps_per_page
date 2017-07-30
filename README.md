# arcmap_2maps_per_page
Python script to generate PDF map series with 2 maps per page 

This was written for a project that required a 22x34 sheet with 2
layouts per sheet and 4 total sheets.  Since ArcMap 10.5.1 doesn't
support this directly with Data Driven Pages, I wrote this code.

Halfway through the project it turned out that the first 6 maps
needed to be on the first three sheets and that maps 7 and 8 each
needed a separate full sheet. More code.

Then it turned out we needed two sets. One with some layers turned on
and the other with different layers... so more code.

Currently therefore the code is tied to my needs for this project
but once I have it running I will make it less specific. 

# Code

Runs under the python that comes with ArcMap 10.5, version 2.7.13.
I have also tested it under Anaconda python 3.x that has been modified
to use ESRI's arcpy module.

* generate_map_series.py - Run this to generate a series of PDF files
* utils.py - extra code imported by generate_map_series.py

# What it does

The script reads an MXD file,
uses a bunch of hard coded constants that are in the script
and generates a series of maps as PDF files.

Using the "credits" field in the data frame is just a way to insert
some text into the layout that I can control from python.

# What it looks for in the MXD file

The MXD has to be set up with a layer that serves as the index for the
"data driven pages". The script will find this layer (one thing you DON'T
have to hard code!)

It expects the first two data frames to define the upper and lower layouts
on the page. It expects the 3rd data frame to be a reference map.

The script extracts the page size and margins from the MXD layout.

Optionally you can add a 4th data frame and tie the DDP (data driven
pages) to that data frame but you don't really have to. You'd do that
to get access to the columns in the DDP index in "Dynamic Text"
objects in your layout. I use it to put "Sheet N of 5" in the title
block, where N is from the index column called "sheet_number".

Here is ASCII art.

```
    +-----------------------------+----+
    |                             |    |
    |            map 1            |  RefMap
    |                             +----+
    |                       scalebar N |
    +----------------------------------+
                  gutter
    +----------------------------------+
    |                                  |
    |            map 2                 |
    |                                  |
    |                       scalebar N |
    +----------------------------------+
```

## Constants hard coded into the script

They taught me never to put constants into code in Computer School
(and I berate other programmers for doing it) but it turns out to be
practical in the Real World, during conception and initial testing
stages, which is where this project is right now. Berate me if you must.

The MXD is hard coded in near the end of the file.

I will add the mini test MXD to this project.

Constants - currently it reads some constants from the top of the file that should be pulled from the MXD

It reads a column in the DDP index to decide if a given page should have
2 half page maps or 1 full page map.

It also reads a table (currently embedded in the source)
that tells it to generate a series of maps with different layers
turned on or off, in this case it does a set with a proposed alignment 1
and another with alignment 2 and does a set with contours and a set with
aerial photo, for a combined output of 20 PDF files.

# Running it

This is the easiest part. Open a command window and run it. No args.

 python generate_map_series.py

If python is not on your map use the full path, for example,

 C:\Python27\ArcGISx6410.5\python generate_map_series.py

I don't have any python toolbox set up for it, for this tool that would
just be extra work right now. I run it from the command line. This has
a huge bonus - it does not tie up ArcMap while it runs, I can immediately
go back to mapping while it cranks out 10 or 20 maps.

# Resources

See https://blogs.esri.com/esri/arcgis/2010/12/14/combining-data-driven-pages-with-python-and-arcpy-mapping/

There are a lot of options for the exportToPDF function.
Refer to https://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-mapping/exporttopdf.htm