#!/usr/bin/env python
from __future__ import print_function
import sys, os, json
import arcpy
from utils import dictlist

""" See the README.md file for complete information! """

f2_hgt = max_height = 0

def usage():
    print("""Usage: python generate_map_series.py <settings.json>
where "<settings.json>" is the name of a file describing the map
series you want to print.""")
    exit(1)

def get_element(mxd, name):
    for e in arcpy.mapping.ListLayoutElements(mxd):
        if e.name == name:
            return e
    return None

def get_frames(mxd):
    """ Return a list frames[] with the dataframes we need for this project. 
Side effect: find the positions of the frames and put them in globals. """
    global f2_hgt, max_height

    # Your MXD is expected to have these, in this order
    # 
    # data frame 0 : first map
    # data frame 1 : second map
    # data frame 2 : locator map (optional)
    
    frames = []

    frames.append(arcpy.mapping.ListDataFrames(mxd)[0])
    frames.append(arcpy.mapping.ListDataFrames(mxd)[1])

    # Edges of the two big data frames
    # Maybe we don't use all of these in this project
    # but it might be nice to have them around.
    
    f1_y   = frames[0].elementPositionY
    f1_hgt = frames[0].elementHeight
    f2_hgt = frames[1].elementHeight
    f2_y = frames[1].elementPositionY
    max_height = f1_y + f1_hgt - f2_y

    # Append the locator frame or an empty entry
    try:
        locator = arcpy.mapping.ListDataFrames(mxd)[2]
    except IndexError:
        # Append NONE
        locator = None
    frames.append(locator)

    return frames

def read_page_definitions(fc, locator=None):
    """ Use the feature class 'fc' to define each page """

    pages = []

    try:
        desc = arcpy.Describe(fc)
        shape_name = desc.shapeFieldName

        # I should check to see which fields are actually in the feature class
        # instead of using "locator" parameter

        fields = ["SHAPE@", "pagenumber", "scale", "rotation", "layout"]
        if locator:
            fields.extend(["loc_map_x", "loc_map_y"])

            # 0 shape
            # 1 pagenumber
            # 2 scale
            # 3 rotation
            # 4 layout
            # 5 loc_map_x (optional)
            # 6 loc_map_y (optional)

        rows = arcpy.da.SearchCursor(fc, fields)
        
    except Exception as e:
        print("Can't read page definitions \"%s\", %s" % (fc,e))
        return pages
    
    dpages = {}
    for row in rows:
        pagenum = row[1]
        dpages[pagenum] = row
    del rows

    # Sort the dictionary dpages into a 'pages' list
    for p in sorted(dpages):
        row = dpages[p]
        pagenumber = row[1]
        pages.append(row)
        
    return pages

def export_pages(mxd, frames, pdfbase):
    """ Export Data Driven Pages
Columns in DDP index control 1 or 2 map layout and ref map location. 
Returns the number of PDF files generated. """

    ddp = mxd.dataDrivenPages
    ddp_layer_source = ddp.indexLayer.dataSource
    print("DDP layer", ddp_layer_source)

    f1 = frames[0]
    f2 = frames[1]
    locator = frames[2]
    print("%s, %s" % (f1.name, f2.name))
    ddp_layer = read_page_definitions(ddp_layer_source, locator)
    # returns a sorted list with each page described in a tuple (xy,rotation,pagenumber,scale)

    ddp_index = 0
    page_count = 0
    while ddp_index < len(ddp_layer):
        print()
        print("====")
        print("ddp_index", ddp_index)
        sys.stdout.flush()

        p = ddp_layer[ddp_index]

        if p[4] == 1:
            print("single map layout")

            # Make frame 1 invisible
            f2_visible(False)

            # Set up frame 2
            # Order matters!
            #   0 adjust frame size
            #   1 set rotation
            #   2 set extent
            #   3 set scale

            # Make frame 2 fill the page
            f2.elementHeight = max_height
            
            rotation = p[3]
            if rotation == None: rotation = 0
            f2.rotation = rotation
            f2.extent   = p[0].extent
            if p[2] != None: f2.scale = p[2]
            f2.credits  = "map %d" % (ddp_index+1)
            print("%d scale:%s rotation:%s" % (ddp_index, f2.scale, f2.rotation))
            
            basename = pdfbase + str(ddp_index+1)

        else:
            print("two map layout")

            f2_visible(True)
            f1.credits = "map %d" % (ddp_index+1)

            # Make frame 2 its normal size
            f2.elementHeight = f2_hgt
            
            # Set up frame 1

            rotation = p[3]
            if rotation == None: rotation = 0
            f1.rotation = rotation
            f1.extent   = p[0].extent
            if p[2] != None: f1.scale = p[2]
            print("%d scale:%s rotation:%s" % (ddp_index, f1.scale, f1.rotation))
            # Make map 2 fit on 1/2 page

            ddp_index += 1
            p = ddp_layer[ddp_index]

            # Set up frame 2

            rotation = p[3]
            if rotation == None: rotation = 0
            f2.rotation = rotation
            f2.extent = p[0].extent
            if p[2] != None: f2.scale = p[2]
            f2.credits = "map %d" % (ddp_index+1)
            print("%d scale:%s rotation:%s" % (ddp_index, f2.scale, f2.rotation))
            basename = pdfbase + str(ddp_index) + "_" + str(ddp_index+1)

        # Position the reference map, if we have one.
        # The numbers in the DDP index layer have to make sense for your layout!
        # In my sample project I move it around at the top of the page.

        if locator:
            locator.elementPositionX = p[5]
            locator.elementPositionY = p[6]
            print("locator %s,%s" % (locator.elementPositionX, locator.elementPositionY))

        tmppdf = basename + ".pdf"
        print("Exporting to %s" % tmppdf)

        # Remove the file so we know we're building on a new one.
        if os.path.exists(tmppdf):
            os.unlink(tmppdf)

        # *** NOTE NOTE NOTE *** To get the locator map to highlight
        # "extent indicators" correctly you have to use the ddp
        # exportToPDF method. I don't want ArcMap messing with extent
        # of Frame 1 and Frame 2, so I put an extra dataframe in the
        # MXD, and tie the DDP index to it.
        #
        # If you never use a locator map with extent indicators
        # you could use this instead, it's not as confusing:
#        arcpy.mapping.ExportToPDF(mxd, tmppdf, 
#                                  resolution=600, image_quality="BEST")

        ddp.exportToPDF(tmppdf, "RANGE", str(ddp_index+1),
                        resolution=600, image_quality="BEST")

        page_count += 1
        ddp_index += 1

    del mxd
    return page_count

# If any of these elements exist they will be made invisible on single map pages
twopage_elements = ["Frame 1", "North Arrow 1", "Scale Bar 1", "Scale Text 1", "Credits 1"]
dvisible = {}

def f2_initialize(mxd):
    """ Save the locations of the elements that will be made "invisible" on single map pages. """
    global dvisible
    for e in arcpy.mapping.ListLayoutElements(mxd):
        if e.name in twopage_elements:
            dvisible[e] = e.elementPositionX
            
def f2_visible(state):
    """ Move these elements on or off the page to make them visible or invisible. """
    for e in dvisible:
        # I wish the "visible" property worked!
        if state:
            # Move it back to its starting position
            e.elementPositionX = dvisible[e]
        else:
            # Move it off the page
            e.elementPositionX = 1000 

class maplayers(object):
    
    def __init__(self, mxd):

        df_count = 0
        lyr_count = 0
        self.dlayers = dictlist()

        frames = get_frames(mxd)
        for df in frames:
            for lyr in arcpy.mapping.ListLayers(mxd, '*', df):
                lyr_count += 1
                (group,name) = os.path.split(lyr.longName)

                #print("group:%s | layer:%s" % (group, name))
                
                if group:
                    self.dlayers.add(group, lyr)
                self.dlayers.add(name, lyr)

            df_count += 1

        print(self.dlayers)
        return

    def set(self, name, state):
        if name in self.dlayers.dict:
            for lyr in self.dlayers.dict[name]:
                lyr.visible = state
            print(name, state)
        else:
            print("Can't find any layer named '%s'." % name)

def generate_mapset(mxd, frames, l, basename, controlled_layers):

    # Create a text file so that anyone looking at this folder
    # will know this script is generating new maps.
    
    semaphore = basename + "_IS_BUILDING.txt"
    fp = open(semaphore, "w")
    fp.write("Currently creating new maps, this file will be deleted when process completes.")
    fp.close()

    # Set visibility on any layers that are in the list
    
    for layer in controlled_layers:
        if layer[0] == '!':
            l.set(layer[1:], False)
        else:
            l.set(layer, True)

    count = export_pages(mxd, frames, basename)

    # Remove the "semaphore"; we're done with this set.
    os.unlink(semaphore)

    return count


# ===============

if __name__ == "__main__":

    try:
        jsonfile = sys.argv[1]
    except:
        usage()

    with open(jsonfile,"r") as fp:
        settings = json.load(fp)
#   print(json.dumps(settings, indent=4, separators=(',', ': ')))

    mxdfile = settings["mxdfile"]
    if not os.path.exists(mxdfile):
        print("MXD file \"%s\" does not exist." % mxdfile)
        exit(-1)
    (mxdfolder, mxdfile) = os.path.split(os.path.abspath(mxdfile))
    os.chdir(mxdfolder)
    
    try:
        # Put the generated files into a folder
        output_folder = settings["outputFolder"]
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
    except KeyError:
        # No output folder specified, use current directory
        output_folder = '.'
        
    try:
        mxd = arcpy.mapping.MapDocument(mxdfile)
    except Exception as e:
        print("Can't open MXD \"%s\", %s" % (mxdfile, e))
        exit(-1)

    all_layers = maplayers(mxd)

    # Find the data frames we will be manipulating.
    frames  = get_frames(mxd)

    # Save positions of the elements we need to "make invisible".
    f2_initialize(mxd)

    total = 0
    for map in settings["maps"]:
        basename = map["outputname"]
        try:
            # Get list of layers to alter
            layers = map["layers"]
        except KeyError:
            # No optional list, don't touch layers
            layers = []
        print(basename, layers)
        total += generate_mapset(mxd, frames, all_layers,
                                 os.path.join(output_folder,basename),
                                 layers)

    print()
    print("Total map files generated: %d" % total)

# That's all

