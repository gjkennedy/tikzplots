"""
The following functions implement 2D plotting functions for tikz.

These allow you to generate a string that contains the tikz/LaTeX
commands that will create 2D line plots over a given domain. These can
be customized by adding commands to the string that will generate the
axes, title, labels etc. that may be required.
"""

def get_header(font_package='helvet'):
    """Return the header file"""
    s = '\\documentclass{article}\n'
    s += '\\usepackage[usenames,dvipsnames]{xcolor}\n'
    s += '\\usepackage{tikz}\n'
    s += '\\usepackage[active,tightpage]{preview}\n'
    s += '\\usepackage{amsmath}\n'
    if font_package is not None:
        s += '\\usepackage{%s}\n'%(font_package)
    s += '\\usepackage{sfmath}\n'
    s += '\\PreviewEnvironment{tikzpicture}\n'
    s += '\\setlength\PreviewBorder{5pt}\n'
    return s

def get_begin_tikz(xdim=1.0, ydim=1.0, xunit='cm', yunit='cm',
                   use_sf=True):
    """Get the portion of the string that starts the figure"""
    s = '\\begin{document}\n'
    s += '\\begin{figure}[h]\n'
    s += get_begin_tikz_picture(xdim=xdim, ydim=ydim, xunit=xunit, yunit=yunit,
                                use_sf=use_sf)
    return s

def get_begin_tikz_picture(xdim=1.0, ydim=1.0, xunit='cm', yunit='cm',
                           use_sf=True):
    s = '\\begin{tikzpicture}[x=%f%s, y=%f%s]\n'%(
        xdim, xunit, ydim, yunit)
    if use_sf:
        s += '\\sffamily\n'
    return s

def get_end_tikz_picture():
    s = '\\end{tikzpicture}'
    return s

def get_end_tikz():
    """Get the final string at the end of the document"""
    s = get_end_tikz_picture()
    s += '\\end{figure}'
    s += '\\end{document}'
    return s

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def get_tableau20():
    """Return 20 nice colors"""
    tableau20 = [(31, 119, 180), (174, 199, 232),
                 (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138),
                 (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213),
                 (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210),
                 (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141),
                 (23, 190, 207), (158, 218, 229)]
    return tableau20

def get_blue_red_colors(n):
    red = hex_to_rgb('c23616')
    white = (255, 255, 255)
    blue = hex_to_rgb('192a56')

    rgb = []
    for i in range(n):
        if i < n/2:
            u = 0.75*i/(n-1)
        else:
            u = 0.25 + 0.75*i/(n - 1)

        if u > 0.5:
            w1 = 0.0
            w2 = 2*(u - 0.5)
            w3 = 1 - 2*(u - 0.5)
        else:
            w1 = 1 - 2*u
            w2 = 0.0
            w3 = 2*u
        rgb.append((min(255, int(w1*blue[0] + w2*red[0] + w3*white[0])), 
                    min(255, int(w1*blue[1] + w2*red[1] + w3*white[1])),
                    min(255, int(w1*blue[2] + w2*red[2] + w3*white[2]))))

    return rgb

def get_colors(name):
    if name == 'tableau20':
        return get_tableau20()
    if name == 'blue-green':
        hexa = ['48466d', '3d84a8', '46cdcf', 'abedd8']
    elif name == 'orange-green':
        hexa = ['ffba5a', 'c0ffb3', '52de97', '2c7873']
    elif name == 'germany':
        hexa = ['2d4059', 'ea5455', 'f07b3f', 'ffd460']
    else:
        hexa = ['00b894', '00cec9', '0984e3', '6c5ce7', 
                'b2bec3', 'fdcb6e', 'e17055', 'd63031',
                'e84393', '2d3436']

    rgb = []
    for h in hexa:
        rgb.append(hex_to_rgb(h))
    return rgb

def _get_intersections(x1, x2, y1, y2,
                       xmin, xmax, ymin, ymax):
    """
    Get the intersection points along the line segment:

    (x1, y1) + u*(x2 - x1, y2 - y1) = (xmin/xmax, ymin/ymax)

    and sort them for convenience.
    """

    # Keep track of the original points
    dx = x2 - x1
    dy = y2 - y1

    umin = 0.0
    umax = 1.0
    if dx > 0.0:
        umin = max(umin, (xmin - x1)/dx)
        umax = min(umax, (xmax - x1)/dx)
    elif dx < 0.0:
        umin = max(umin, (xmax - x1)/dx)
        umax = min(umax, (xmin - x1)/dx)
    else:
        # dx = 0, be careful here..
        if x1 < xmin or x1 > xmax:
            return None

    if dy > 0.0:
        umin = max(umin, (ymin - y1)/dy)
        umax = min(umax, (ymax - y1)/dy)
    elif dy < 0.0:
        umin = max(umin, (ymax - y1)/dy)
        umax = min(umax, (ymin - y1)/dy)
    else:
        if y1 < ymin or y1 > ymax:
            return None

    if umin > umax:
        return None

    return umin, umax

def _get_tri_edges(tri):
    """
    Get the edges for the triangular mesh
    """
    return [[tri[1], tri[2]], [tri[2], tri[0]], [tri[0], tri[1]]]

def _get_planar_tri_edges(npts, tris):
    """
    Uniquely order and create the connectivity for a planar triangular mesh
    """

    # Find the nodes associated with the triangle
    node_to_tris = []
    for i in range(npts):
        node_to_tris.append([])

    for index, tri in enumerate(tris):
        node_to_tris[tri[0]].append(index)
        node_to_tris[tri[1]].append(index)
        node_to_tris[tri[2]].append(index)

    # Assign edge numbers for each edge
    edges = []
    edge_to_tris = []
    num_edges = 0

    tri_to_edges = []
    for i in range(len(tris)):
        tri_to_edges.append([-1, -1, -1])

    for tri_index, tri in enumerate(tris):
        for e1_index, e1 in enumerate(_get_tri_edges(tri)):
            if tri_to_edges[tri_index][e1_index] < 0:
                match = False
                for adj_index in node_to_tris[e1[0]]:
                    if adj_index != tri_index:
                        for e2_index, e2 in enumerate(_get_tri_edges(tris[adj_index])):
                            if ((e1[0] == e2[0] and e1[1] == e2[1]) or
                                (e1[1] == e2[0] and e1[0] == e2[1])):
                                match = True
                                tri_to_edges[tri_index][e1_index] = num_edges
                                tri_to_edges[adj_index][e2_index] = num_edges
                                edges.append((e1[0], e1[1]))
                                edge_to_tris.append((tri_index, adj_index))
                                num_edges += 1
                                break
                    if match:
                        break

                if not match:
                    edges.append((e1[0], e1[1]))
                    edge_to_tris.append((tri_index, -1))
                    tri_to_edges[tri_index][e1_index] = num_edges
                    num_edges += 1

    return edges, tri_to_edges, edge_to_tris

def _get_2d_tri_contour_lines(x, y, vals, tris, edges, tri_to_edges, edge_to_tris, lev):
    """
    Get a list of the (x,y) coordinates of lines that make up a contour level
    on a contour plot
    """

    # Find all the edge intersections
    has_intersect = []
    intersect = []
    for tri in tris:
        inter = []
        count = 0
        for e_index, e in enumerate(_get_tri_edges(tri)):
            if ((vals[e[1]] < lev and vals[e[0]] > lev) or
                (vals[e[0]] < lev and vals[e[1]] > lev)):
                u = (lev - vals[e[0]])/(vals[e[1]] - vals[e[0]])
                xi = (1.0 - u)*x[e[0]] + u*x[e[1]]
                yi = (1.0 - u)*y[e[0]] + u*y[e[1]]
                inter.append((xi, yi))
                count += 1
            else:
                inter.append(None)
        intersect.append(inter)
        if count == 2:
            has_intersect.append(True)
        else:
            has_intersect.append(False)

    # Now, try and find all of the lines
    lines = []
    for tri_index, tri in enumerate(tris):
        if has_intersect[tri_index]:
            # Find the intersections
            X, Y = [], []

            # Find the intersecting edges
            tri_edges = []
            for i, e_index in enumerate(tri_to_edges[tri_index]):
                if intersect[tri_index][i] is not None:
                    X.append(intersect[tri_index][i][0])
                    Y.append(intersect[tri_index][i][1])
                    tri_edges.append(e_index)

            # We've finished plotting this triangle, move on to the next
            has_intersect[tri_index] = False

            prev_edge = tri_edges[1]
            next_tri_index = edge_to_tris[prev_edge][0]
            if next_tri_index == tri_index:
                next_tri_index = edge_to_tris[prev_edge][1]

            # Find the triangles associated with the intersection3
            while next_tri_index >= 0:
                for i, e_index in enumerate(tri_to_edges[next_tri_index]):
                    if (e_index != prev_edge and intersect[next_tri_index][i] is not None):
                        X.append(intersect[next_tri_index][i][0])
                        Y.append(intersect[next_tri_index][i][1])
                        prev_edge = e_index
                        has_intersect[next_tri_index] = False

                        next_tri_index = -1
                        if has_intersect[edge_to_tris[prev_edge][0]]:
                            next_tri_index = edge_to_tris[prev_edge][0]
                        elif has_intersect[edge_to_tris[prev_edge][1]]:
                            next_tri_index = edge_to_tris[prev_edge][1]
                        break

            prev_edge = tri_edges[0]
            next_tri_index = edge_to_tris[prev_edge][0]
            if next_tri_index == tri_index:
                next_tri_index = edge_to_tris[prev_edge][1]

            while next_tri_index >= 0:
                for i, e_index in enumerate(tri_to_edges[next_tri_index]):
                    if (e_index != prev_edge and intersect[next_tri_index][i] is not None):
                        X.insert(0, intersect[next_tri_index][i][0])
                        Y.insert(0, intersect[next_tri_index][i][1])
                        prev_edge = e_index
                        has_intersect[next_tri_index] = False

                        next_tri_index = -1
                        if has_intersect[edge_to_tris[prev_edge][0]]:
                            next_tri_index = edge_to_tris[prev_edge][0]
                        elif has_intersect[edge_to_tris[prev_edge][1]]:
                            next_tri_index = edge_to_tris[prev_edge][1]
                        break

            lines.append((X, Y))

    return lines

def get_2d_quad_contour_plot(x, y, vals, quads, levs, lev_colors=None, line_dim='thick',
                            xscale=1.0, xbase=0.0, yscale=1.0, ybase=0.0,
                            xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Create a 2d contour plot for a set of quads
    """
    s = ''

    # Make sure that the levels and colors match
    if (lev_colors is None or
        (isinstance(lev_colors, list) and len(lev_colors) != len(levs))):
        lev_colors = ['black']*len(levs)

    tris = []
    for quad in quads:
        tris.append([quad[0], quad[1], quad[2]])
        tris.append([quad[0], quad[2], quad[3]])

    # Get the edges and tri_to_edges/edge_to_tris data structures
    npts = len(x)
    edges, tri_to_edges, edge_to_tris = _get_planar_tri_edges(npts, tris)

    for index, lev in enumerate(levs):
        line_list = _get_2d_tri_contour_lines(x, y, vals, tris, edges, tri_to_edges, edge_to_tris, lev)

        for line in line_list:
            s += get_2d_plot(line[0], line[1], xscale=xscale, xbase=xbase,
                             yscale=yscale, ybase=ybase, line_dim=line_dim,
                             color=lev_colors[index],
                             xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    return s

def get_2d_tri_contour_plot(x, y, vals, tris, levs, lev_colors=None, line_dim='thick',
                            xscale=1.0, xbase=0.0, yscale=1.0, ybase=0.0,
                            xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Create a 2d contour plot for a set of triangles
    """
    s = ''

    # Make sure that the levels and colors match
    if (lev_colors is None or
        (isinstance(lev_colors, list) and len(lev_colors) != len(levs))):
        lev_colors = ['black']*len(levs)

    # Get the edges and tri_to_edges/edge_to_tris data structures
    npts = len(x)
    edges, tri_to_edges, edge_to_tris = _get_planar_tri_edges(npts, tris)

    for index, lev in enumerate(levs):
        line_list = _get_2d_tri_contour_lines(x, y, vals, tris, edges, tri_to_edges, edge_to_tris, lev)

        for line in line_list:
            s += get_2d_plot(line[0], line[1], xscale=xscale, xbase=xbase,
                             yscale=yscale, ybase=ybase, line_dim=line_dim,
                             color=lev_colors[index],
                             xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    return s

def get_2d_plot(xvals, yvals, xscale=1.0, xbase=0.0, yscale=1.0, ybase=0.0,
                line_dim='thick', color='black', fill_color='white',
                xmin=None, xmax=None, ymin=None, ymax=None,
                symbol=None, symbol_dim='thin', symbol_size=0.15):
    """
    Create a string representing the 2D plot of a series of
    linesegments. If ymin/ymax, xmin/xmax are specified, clip the plot
    to the box
    """

    # Map the points to the drawing
    if ymin is None:
        ymin = min(yvals)
    if xmin is None:
        xmin = min(xvals)

    if ymax is None:
        ymax = max(yvals)
    if xmax is None:
        xmax = max(xvals)

    s = ''
    n = min(len(yvals), len(xvals))
    if line_dim is not None:
        draw_on = False

        for i in range(n-1):
            inter = _get_intersections(xvals[i], xvals[i+1],
                                       yvals[i], yvals[i+1],
                                       xmin, xmax, ymin, ymax)

            if inter is not None:
                if symbol is None:
                    u = inter[0]
                    if not draw_on:
                        s += r'\draw[%s, color=%s] '%(line_dim, color)
                        s += r'(%f, %f) '%(
                            xscale*((1.0 - u)*xvals[i] + u*xvals[i+1] - xbase),
                            yscale*((1.0 - u)*yvals[i] + u*yvals[i+1] - ybase))
                        draw_on = True

                    u = inter[1]
                    s += r'-- (%f, %f) '%(
                        xscale*((1.0 - u)*xvals[i] + u*xvals[i+1] - xbase),
                        yscale*((1.0 - u)*yvals[i] + u*yvals[i+1] - ybase))

                    if u < 1.0:
                        s += ';\n'
                        draw_on = False
                else:
                    u = inter[0]
                    s += r'\draw[%s, color=%s] '%(line_dim, color)
                    s += r'(%f, %f) '%(
                        xscale*((1.0 - u)*xvals[i] + u*xvals[i+1] - xbase),
                        yscale*((1.0 - u)*yvals[i] + u*yvals[i+1] - ybase))
                    u = inter[1]
                    s += r'-- (%f, %f);'%(
                        xscale*((1.0 - u)*xvals[i] + u*xvals[i+1] - xbase),
                        yscale*((1.0 - u)*yvals[i] + u*yvals[i+1] - ybase))
                    s += '\n'

        if symbol is None:
            if draw_on:
                s += ';\n'

    if symbol == 'circle':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f, %f) circle (%g);'%(
                    symbol_dim, color, fill_color,
                    xscale*(xvals[i] - xbase),
                    yscale*(yvals[i] - ybase), 0.5*symbol_size)
    elif symbol == 'square':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f, %f) rectangle (%f, %f);'%(
                    symbol_dim, color, fill_color,
                    xscale*(xvals[i] - xbase) - 0.5*symbol_size,
                    yscale*(yvals[i] - ybase) - 0.5*symbol_size,
                    xscale*(xvals[i] - xbase) + 0.5*symbol_size,
                    yscale*(yvals[i] - ybase) + 0.5*symbol_size)
    elif symbol == 'triangle':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f,%f) '%(
                    symbol_dim, color, fill_color,
                    xscale*(xvals[i] - xbase) - 0.45*symbol_size,
                    yscale*(yvals[i] - ybase) - 0.5*symbol_size)
                s += '-- (%f,%f) -- (%f,%f) -- cycle;\n'%(
                    xscale*(xvals[i] - xbase) + 0.45*symbol_size,
                    yscale*(yvals[i] - ybase) - 0.5*symbol_size,
                    xscale*(xvals[i] - xbase),
                    yscale*(yvals[i] - ybase) + 0.5*symbol_size)
    elif symbol == 'delta':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f,%f) '%(
                    symbol_dim, color, fill_color,
                    xscale*(xvals[i] - xbase) - 0.45*symbol_size,
                    yscale*(yvals[i] - ybase) + 0.5*symbol_size)
                s += '-- (%f,%f) -- (%f,%f) -- cycle;\n'%(
                    xscale*(xvals[i] - xbase) + 0.45*symbol_size,
                    yscale*(yvals[i] - ybase) + 0.5*symbol_size,
                    xscale*(xvals[i] - xbase),
                    yscale*(yvals[i] - ybase) - 0.5*symbol_size)
    elif symbol == 'diamond':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f,%f) '%(
                    symbol_dim, color, fill_color,
                    xscale*(xvals[i] - xbase) - 0.5*symbol_size,
                    yscale*(yvals[i] - ybase))
                s += '-- (%f,%f) -- (%f,%f) -- (%f,%f) -- cycle;\n'%(
                    xscale*(xvals[i] - xbase),
                    yscale*(yvals[i] - ybase) - 0.5*symbol_size,
                    xscale*(xvals[i] - xbase) + 0.5*symbol_size,
                    yscale*(yvals[i] - ybase),
                    xscale*(xvals[i] - xbase),
                    yscale*(yvals[i] - ybase) + 0.5*symbol_size)

    return s

def get_bar_chart(bars, color_list=None, x_sep=0.25,
                  xmin=None, xmax=None, ymin=None, ymax=None,
                  line_dim='thick', xscale=1.0, xbase=0.0,
                  yscale=1, ybase=0.0,
                  bar_width=None, bar_offset=None):
    """Get the string for a bar chart"""

    if color_list is None:
        color_list = len(bars[0])*['black']

    s = ''
    for i in range(len(bars)):
        if bar_width is None:
            bw = (1.0 - x_sep)/len(bars[i])
        else:
            bw = bar_width

        boff = 0.0
        if bar_offset is not None:
            boff = bar_offset

        for j in range(len(bars[i])):
            x1 = (i+1) + boff + (j+0.05)*bw
            x2 = (i+1) + boff + (j+0.95)*bw
            if xmin is not None:
                x1 = max(x1, xmin)
                x2 = max(x2, xmin)
            if xmax is not None:
                x1 = min(x1, xmax)
                x2 = min(x2, xmax)

            y1 = ymin
            y2 = bars[i][j]
            if ymin is not None:
                y1 = max(y1, ymin)
                y2 = max(y2, ymin)
            if ymax is not None:
                y1 = min(y1, ymax)
                y2 = min(y2, ymax)

            if y2 > ymin:
                s += r'\draw[%s, color=%s, fill=%s, fill opacity=0.3]'%(
                    line_dim, color_list[j], color_list[j])
                s += ' (%f, %f) rectangle (%f, %f);'%(
                    xscale*(x1 - xbase), yscale*(y1 - ybase),
                    xscale*(x2 - xbase), yscale*(y2 - ybase))

    return s

def get_2d_axes(xmin, xmax, ymin, ymax,
                axis_style='r-style',
                xscale=1.0, xbase=0.0, yscale=1.0, ybase=0.0,
                xticks=[], yticks=[],
                xtick_labels=None, ytick_labels=None,
                tick_font='normalsize', tick_size='semithick',
                label_font='Large', xlabel='x', ylabel='y',
                xlabel_offset=0.1, ylabel_offset=0.15,
                axis_size='thick', axis_color='gray',
                tick_frac=0.05, ):
    """Draw the axes on the plot"""

    # Find the tick size
    tick_dim = min(tick_frac*(ymax - ymin)*yscale,
                   tick_frac*(xmax - xmin)*xscale)

    # Draw the axes
    s = ''
    if axis_style == 'r-style':
        if len(xticks) >= 2:
            s += '\\draw[%s, color=%s] (%f, %f) -- (%f,%f) -- (%f,%f) -- (%f, %f);'%(
                axis_size, axis_color,
                xscale*(xticks[0] - xbase),
                yscale*(ymin - ybase) - tick_dim,
                xscale*(xticks[0] - xbase), yscale*(ymin - ybase),
                xscale*(xticks[-1] - xbase), yscale*(ymin - ybase),
                xscale*(xticks[-1] - xbase), yscale*(ymin - ybase) - tick_dim)
        if len(yticks) >= 2:
            s += '\\draw[%s, color=%s] (%f, %f) -- (%f,%f) -- (%f,%f) -- (%f, %f);'%(
                axis_size, axis_color,
                xscale*(xmin - xbase) - tick_dim, yscale*(yticks[0] - ybase),
                xscale*(xmin - xbase), yscale*(yticks[0] - ybase),
                xscale*(xmin - xbase), yscale*(yticks[-1] - ybase),
                xscale*(xmin - xbase) - tick_dim, yscale*(yticks[-1] - ybase))
    else:
        s += '\\draw[%s, color=%s] (%f,%f) -- (%f,%f);'%(
            axis_size, axis_color,
            xscale*(xmin - xbase), yscale*(ymin - ybase),
            xscale*(xmax - xbase), yscale*(ymin - ybase))
        s += '\\draw[%s, color=%s] (%f,%f) -- (%f,%f);'%(
            axis_size, axis_color,
            xscale*(xmin - xbase), yscale*(ymin - ybase),
            xscale*(xmin - xbase), yscale*(ymax - ybase))

    # Draw the x-label
    if xlabel is not None:
        s += '\\draw[font=\\%s] (%f, %f) node[below] {%s};'%(
            label_font, 0.5*xscale*(xmin + xmax - xbase),
            yscale*(ymin - xlabel_offset*(ymax - ymin) - ybase),
            xlabel)

    # Draw the y-label
    if ylabel is not None:
        s += '\\draw[font=\\%s] (%f, %f) node[rotate=90] {%s};'%(
            label_font, xscale*(xmin - ylabel_offset*(xmax - xmin) - xbase),
            0.5*yscale*(ymin + ymax - ybase),
            ylabel)

    # Draw the ticks on the graph
    if axis_style == 'r-style':
        if xtick_labels is None:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%g};\n'%(
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase),
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase) - tick_dim,
                    xticks[i])
        else:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%s};\n'%(
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase),
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase) - tick_dim,
                    xtick_labels[i])

        # Draw the ticks on the graph
        if ytick_labels is None:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%g};\n'%(
                    xscale*(xmin - xbase), yscale*(yticks[i] - ybase),
                    xscale*(xmin - xbase) - tick_dim, yscale*(yticks[i] - ybase),
                    yticks[i])
        else:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%s};\n'%(
                    xscale*(xmin - xbase), yscale*(yticks[i] - ybase),
                    xscale*(xmin - xbase) - tick_dim, yscale*(yticks[i] - ybase),
                    ytick_labels[i])
    else:
        if xtick_labels is None:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%g};\n'%(
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase) + tick_dim,
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase),
                    xticks[i])
        else:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%s};\n'%(
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase) + tick_dim,
                    xscale*(xticks[i] - xbase), yscale*(ymin - ybase),
                    xtick_labels[i])

        # Draw the ticks on the graph
        if ytick_labels is None:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%g};\n'%(
                    xscale*(xmin - xbase) + tick_dim, yscale*(yticks[i] - ybase),
                    xscale*(xmin - xbase), yscale*(yticks[i] - ybase),
                    yticks[i])
        else:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%s};\n'%(
                    xscale*(xmin - xbase) + tick_dim, yscale*(yticks[i] - ybase),
                    xscale*(xmin - xbase), yscale*(yticks[i] - ybase),
                    ytick_labels[i])

    return s

def get_legend_entry(x, y, length, xscale=1.0, xbase=0.0,
                     yscale=1.0, ybase=0.0,
                     font_size='large',
                     line_dim='thick', color='black',
                     symbol=None, symbol_dim='thin',
                     symbol_size=0.15, label=''):
    """Add a single entry to the legend"""

    # Plot a line segment
    xvals = [x - 0.5*length, x + 0.5*length]
    yvals = [y, y]

    s = get_2d_plot(xvals, yvals, xscale=xscale, xbase=xbase,
                    yscale=yscale, ybase=ybase,
                    line_dim=line_dim, color=color,
                    symbol=symbol, symbol_dim=symbol_dim,
                    symbol_size=symbol_size)

    s += '\\draw[font=\\%s] (%f,%f) node[right] {%s};'%(
        font_size, xscale*(x + 0.75*length), yscale*y, label)

    return s
