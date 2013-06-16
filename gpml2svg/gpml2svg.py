#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re, cgi, codecs, copy
try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader

from collections import defaultdict
from optparse import OptionParser


# Standard definitions
et.register_namespace('', 'http://pathvisio.org/GPML/2013a')


def get_edge( x, y, xo, yo, xt, yt):
    # Define a box by xo->xo+width, yo->yo+width
    # determine where on that box the given point rests
    # number 0-3 in CSS order (top, right, bottom, left)
    constraints = [
        ( xo, xt, yo, yo ),
        ( xt, xt, yo, yt ),
        ( xo, xt, yt, yt ),
        ( xo, xo, yo, yt ),
    ]    
    
    for n, [x1, x2, y1, y2] in enumerate(constraints):
        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return n
            
    return None

def get_direction(x1, y1, x2, y2):

    # There are some wobblyness in the points
    # ideally should get an angle and \/ == up etc.
    # ofs = [ (0, -20), (20, 0), (0, 20), (-20, 0) ]

    if abs(x1-x2) >= abs(y1-y2): # Horizontal
        if x1 > x2:
            return 1
        else:
            return 3
            
    elif abs(y1-y2) > abs(x1-x2):
        if y1 > y2:
            return 0
        else:
            return 2

def get_styles( o, restyle ):

    styles = []
    stylek = set( restyle.keys() ) & set( o.attrib.keys() )

    for s in stylek:
        if isinstance( restyle[s], dict ):
            styles.append( restyle[s][ o.attrib[s] ] )
        else:
            styles.append( restyle[s] % o.attrib[s].lower() )

    return styles


def gpml2svg(
    gpml, 
    node_colors = {},
#    synonyms = {},
    xrefs = {
        'HMDB': 'http://www.hmdb.ca/metabolites/%s',
        'WikiPathways': 'http://wikipathways.org/index.php/Pathway:%s',
        'Entrez Gene': 'http://www.ncbi.nlm.nih.gov/gene/%s',
    }
    ):



    graphrefs = dict()
    graphids = dict()  

    gpml = re.sub(' xmlns="[^"]+"', '', gpml, count=1) # Strip namespace

    tree = et.fromstring(gpml.encode('utf-8'))
    templateEngine = Engine(
                loader=FileLoader( '.' ),
                extensions=[CoreExtension()]
            )

    # Get root page canvas size, pathway name and copyright data from the header
    text = {}
    y = 0
    for k in ['Name', 'Last-Modified', 'Organism', 'License']:
        if k in tree.attrib:
            y += 15
            text[k] = (tree.attrib[k], y) 
    

    rootg = tree.find('Graphics')
    page = {
        'boardwidth':  rootg.attrib['BoardWidth'],
        'boardheight': rootg.attrib['BoardHeight'],
    }
    
    
    # Get all datanodes includes metabolites, genes, proteins, etc.
    # output mostly the same, determine changes in the template

    data_nodes = tree.iterfind('DataNode')
    data_nodes_svg = []

    grouped_nodes = defaultdict(list)

    restyle_n = {
        'FontWeight': 'font-weight:%s;',
        'FontSize': 'font-size:%spx;',
        'Valign': 'vertical-align:%s;',
        'Color': 'stroke:#%s;',
        'LineThickness': 'stroke-width:%spx;',
        }
        
    restyle_t = {
        'Color': 'fill:%s',
    }

    for dn in data_nodes:
        g = dn.find('Graphics')

        xc = float(g.attrib['CenterX'])
        yc = float(g.attrib['CenterY'])
            
        ntype = dn.attrib['Type'].lower()

        node_styles = get_styles( g, restyle_n )
        text_styles = get_styles( g, restyle_t )

        # Data visualisation
        xrs = list( dn.iterfind('Xref') )    
        for xr in xrs:
            if xr.attrib['ID'] in node_colors.keys():
                node_styles.append( 'fill:%s; stroke:%s;' % (node_colors[ xr.attrib['ID']][0] , node_colors[ xr.attrib['ID'] ][0] ) )
                text_styles.append( 'fill:%s;' % node_colors[ xr.attrib['ID']][1] )
                break
                
        url = ''
        xrs = list( dn.iterfind('Xref') )    
        for xr in xrs:
            if xr.attrib['Database'] in xrefs.keys():
                url = xrefs[ xr.attrib['Database'] ] % xr.attrib['ID']             
                break

        width  = float(g.attrib['Width'])
        height = float(g.attrib['Height'])

        xo = xc - (width/2)
        yo = yc - (height/2)

        
        if 'GroupRef' in dn.attrib:
            # is a grouped region add to group-list check 
            grouped_nodes[ dn.attrib['GroupRef'] ].append([ xo, yo, xo+width, yo+height])
            
        
        data = {
            'xc': xc,           'yc': yc,
            'xo': xo,           'yo': yo,
            'xt': xo + width,   'yt': yo + height,
            'width': width,     'height': height,
            'type': ntype,
            'url': url,
            'text_styles': text_styles, 'node_styles': node_styles, 
            'text': cgi.escape( dn.attrib['TextLabel'] ).split('\n'),
        }
        
        if 'GraphId' in dn.attrib:
            graphids[ dn.attrib['GraphId'] ] = data
        
        data_nodes_svg.append( data )


    restyle = {
        'FontWeight': 'font-weight:%s;',
        'FontSize': 'font-size:%spx;',
        'Valign': 'vertical-align:%s;',
        'Color': 'fill:#%s;',
        'LineThickness': 'stroke-width:%spx;',
        }

    labels = tree.iterfind('Label')
    labels_svg = []

    for label in labels:
        g = label.find('Graphics')

        xc = float(g.attrib['CenterX'])
        yc = float(g.attrib['CenterY'])

        styles = get_styles( g, restyle )

        labels_svg.append( {
            'xc': xc,           'yc': yc,
            'styles': styles,
            'text': cgi.escape( label.attrib['TextLabel'] ).split('\n'),
        })
    
    restyle = {
        'FontWeight': 'font-weight:%s;',
        'FontSize': 'font-size:%spx;',
        'Valign': 'vertical-align:%s;',
        'Color': 'stroke:#%s;',
        'FillColor': 'fill:#%s;',
        'LineThickness': 'stroke-width:%spx;',
        }

    shapes = tree.iterfind('Shape')
    shapes_svg = []

    for shape in shapes:
        g = shape.find('Graphics')

        styles = get_styles( g, restyle )

        xc = float(g.attrib['CenterX'])
        yc = float(g.attrib['CenterY'])

        width  = float(g.attrib['Width'])
        height = float(g.attrib['Height'])

        xo = xc - (width/2)
        yo = yc - (height/2)

        z = g.attrib['ZOrder']

    
        shape_type = g.attrib['ShapeType']

        if shape_type == 'RoundedRectangle':
            rx = 12
            ry = 12
        else:
            rx = 0
            ry = 0
    
        double_line_property = False
        attributes = shape.iterfind('Attribute')
        for attribute in attributes:
        
            if attribute.attrib['Key'] == 'org.pathvisio.DoubleLineProperty':
                double_line_property = True

        data = {
            'xc': xc,           'yc': yc,
            'xo': xo,           'yo': yo,
            'xt': xo + width,   'yt': yo + height,
            'width': width,     'height': height,
            'styles': styles,
            'rx': rx,           'ry': ry,

            'shape_type': shape_type,
        }
        
        shapes_svg.append(data)
        
        if 'GraphId' in shape.attrib:
            graphids[ shape.attrib['GraphId'] ] = data


        if double_line_property:
            datad = copy.copy(data)
            datad['xo'] += 6
            datad['yo'] += 6
            datad['width'] -= 12
            datad['height'] -= 12
            datad['rx'] -=6
            datad['ry'] -=6
             
            shapes_svg.append( datad )

    groups = tree.iterfind('Group')
    groups_svg = []
    
    for group in groups:
    
        xo = float('inf');
        yo = float('inf');
        xt = 0;
        yt = 0;
    
        items = grouped_nodes[ group.attrib['GroupId'] ]
    
        for i in items:
            xo = min( xo, i[0] )
            yo = min( yo, i[1] )

            xt = max( xt, i[2] )
            yt = max( yt, i[3] )

        try:
            gstyle = group.attrib['Style'].lower()
        except:
            gstyle = ''
        
        shapedef = {
            '':{ # Default rectange (also used for 'group'
                'xo': xo-8,           'yo': yo-8,
                'width': xt-xo+16,     'height': yt-yo+16,
                },
            'complex':{ # Hexagon (8 corners)
                'x1': xo-12, 'x2': xo+6, 'x3': xt-6, 'x4': xt+12, 'x5': xt+12, 'x6': xt-6, 'x7': xo+6, 'x8': xo-12,
                'y1': yo+6, 'y2': yo-12, 'y3': yo-12, 'y4': yo+6, 'y5': yt-6, 'y6': yt+12, 'y7': yt+12, 'y8': yt-6, 
                }
        
        }
        
        try:
            dims = shapedef[gstyle]
        except:
            dims = shapedef['']

        groups_svg.append( dict( {
                'gstyle': gstyle,
        }.items() + dims.items() ) )


    # Lines/interactions are visually identical; process the same
    
    restyle = {
        'FontWeight': 'font-weight:%s;',
        'FontSize': 'font-size:%spx;',
        'Valign': 'vertical-align:%s;',
        'Color': 'stroke:#%s;',
        'LineThickness': 'stroke-width:%spx;',
        'LineStyle':{'Broken':'stroke-dasharray:4,4;'}
        }    
           
    interactions = list( tree.iterfind('Interaction') ) + list( tree.iterfind('Line') )
    interactions_svg = []
    interactions_elbows_svg = []
    color_definitions = set()

    graphrefs = dict()

    for interaction in interactions:
        g = interaction.find('Graphics')

    
        ps = list( g.iterfind('Point') ) # Points as A->B
        anchors = g.iterfind('Anchor')
        # Iterate points, building a set of lines; add arrow heads where indicated
        
        path = []
        xp, yp = False, False
        for p in ps:
                
            x = float(p.attrib['X'])
            y = float(p.attrib['Y'])

            if 'GraphRef' in p.attrib:
                graphref = p.attrib['GraphRef']
                d = get_direction(xp, yp, x, y)

                graphrefs[ graphref ] = [x, y]
            else:
                graphref = False

            path.append( (x, y, graphref) )
            xp, yp = x, y
            
        
        try:
            marker_start = 's%s' % ps[0].attrib['ArrowHead']
        except:
            marker_start = ''
        
        try:
            marker_end = 'e%s' % ps[-1].attrib['ArrowHead']
        except:
            marker_end = ''
            
    
        styles = get_styles( g, restyle )

        # Still need this for the arrow tips/ends
        try:    
            color = g.attrib['Color']
        except:
            color = 'black'
        
        color_definitions.add( color )
    
        try:
            connector_type = g.attrib['ConnectorType']
        except:
            connector_type = ''

        anchor = []
        for a in anchors:
            anchor.append( a.attrib['GraphId'] )

        idata = {
                'path': path,
                #'xo': xo,           'yo': yo,
                #'xt': xt,           'yt': yt,
        
                'marker_start': marker_start,
                'marker_end': marker_end,
            
                'color': color,
                'anchor': anchor,
                
                'styles': styles,
        }
    
        if connector_type == 'Elbow':
            interactions_elbows_svg.append( idata )
        else:
            interactions_svg.append( idata )

    for interaction in interactions_elbows_svg:
        # Iterate through paths with elbows; 
        # Take initial points; if on an object draw out from the edge initially
        # Treat these extended positions as the 'start points'        
        # Anchors == intermediate points (treat the same)
        # Any line passing through an intermediate point *must* enter and exit in the same plane
        # e.g. --+-- therefore for each point determine the plane 
        
        # If target x> and destination x< (if both x> then not horizontal)
        
        path = interaction['path']
        ofs = [ (0, -20), (20, 0), (0, 20), (-20, 0) ]
        dirs = [ 'V', 'H', 'V', 'H' ]

        # Global drawing direction for this path (overall change)
        gdir = dirs[ get_direction( path[0][0], path[0][1], path[-1][0], path[-1][1]) ]
        
        # START: Draw out from the edge of origin box
        [xo, yo, graphref] = path[0]
        inpath = [ (xo, yo) ]
        if graphref in graphids:
            data = graphids[ graphref ]         
            e = get_edge( xo, yo, data['xo'], data['yo'], data['xt'], data['yt'] )
            if e != None: # We're on an edge apparently, draw out from it before starting
                d = dirs[ e ]
                xo, yo = xo+ofs[e][0], yo+ofs[e][1]
                inpath.append( (xo, yo) )
                path[0] = (xo, yo, graphref, d) # Amend the path, so we can just iterate through the middle and look left-right for all points

        # END: Draw out from edge of destination box
        [xd, yd, graphref] = path[-1]
        outpath = [ (xd, yd) ]
        if graphref in graphids:                
            # END: Draw out from the edge of destination box
            data = graphids[ graphref ]         
            e = get_edge( xd, yd, data['xo'], data['yo'], data['xt'], data['yt'] )
    
            if e != None: # We're on an edge apparently, draw out from it before starting
                d = dirs[ e ]
                xd, yd = xd+ofs[e][0], yd+ofs[e][1]
                outpath.append( (xd, yd) )
                path[-1] = (xd, yd, graphref, d)  # Amend the path, so we can just iterate through the middle and look left-right for all points

        # Insert anchor
        if set( interaction['anchor'] ) & set( graphrefs.keys() ):
            for anchor in interaction['anchor']:
                path.insert(1, tuple( graphrefs[ anchor ] + [ anchor ] + ['-'] ) )

        # Check if any of our points (start/end) are level with the anchor
        if len(path) > 2:

            for n in range( 1, len(path)-1):
                # We have some (only ever 1?).
                # Determine if possible to connect to next points horizontal, vertical, both
                # If exact connection; take that
                # If needs intermediate point;
                if  path[n][0] == path[n-1][0] or path[n][0] == path[n+1][0]: # Match an X draw vertically
                    inpath.append( (path[n][0], path[n-1][1]) )
                    inpath.append( (path[n][0], path[n][1]) )
                    inpath.append( (path[n][0], path[n+1][1]) )
                
                elif path[n][1] == path[n-1][1] or path[n][1] == path[n+1][1]: # Match an Y draw horizontally
                    inpath.append( (path[n-1][0], path[n][1]) )
                    inpath.append( (path[n][0], path[n][1]) )
                    inpath.append( (path[n+1][0], path[n][1]) )
                else: # Neither. PANIC.
                    # There is no cheat here; we're floating in space
                    # Just get both sides to continue drawing in the same direction
                    inpath.append( 
                        {
                            'H' : (path[n][0], path[n-1][1]),
                            'V' : (path[n-1][0], path[n][1])
                        }[ path[n-1][3] ] )

                    outpath.append( 
                        {
                            'H' : (path[n][0], path[n+1][1]),
                            'V' : (path[n+1][0], path[n][1])
                        }[ path[n+1][3] ] )
                    pass
                        
        else: # Neither. PANIC.
            # Draw straight hook
            options = {
                'H' : (path[-1][0], path[0][1]),
                'V' : (path[0][0], path[-1][1])
                }
            di = path[0][3] if path[0][3] in options else gdir #H/V
            inpath.append( options[di] )
            

        outpath.reverse()
        interaction['path'] = inpath + outpath
        
        # Remove duplicate points (not neccessary, but tidys resulting svg)
        nd = []
        [nd.append(i) for i in interaction['path'] if i not in nd]
        interaction['path'] = nd

        interactions_svg.append( interaction )
        # Check if x,y match anchor position
        # if matching, draw through that point to the end of current


    metadata = {
        'page': page,
        'text': text,
        'data_nodes': data_nodes_svg,
        'labels': labels_svg,
        'shapes': shapes_svg,
        'groups': groups_svg,
        'interactions': interactions_svg,
        'color_definitions': color_definitions,
        'graphrefs': graphrefs,
        'graphids': graphids,
    }

    template = templateEngine.get_template('gpml2svg.svg')

    return template.render( metadata )

def main():
    # Run from command line
    parser = OptionParser()

    parser.add_option("-f", "--file", dest="file", default=None,
                      help="load data file by name, name root used as basis for output graph filenames", metavar="FILE")

    (options, args) = parser.parse_args()


    f = open(options.file,'r')
    gpml = f.read().decode('utf8')
    f.close()

    svg = gpml2svg( gpml )

    outfile_name = options.file.replace('gpml','svg')
    o = codecs.open('test.svg','w','utf-8')
    o.write( svg )
    o.close()


if __name__ == "__main__":
    main()