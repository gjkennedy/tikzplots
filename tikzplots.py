'''
The following functions implement 2D plotting functions for tikz.

These allow you to generate a string that contains the tikz/LaTeX
commands that will create 2D line plots over a given domain. These can
be customized by adding commands to the string that will generate the
axes, title, labels etc. that may be required.
'''

def get_header(font_package='helvet'):
    '''Return the header file'''
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
    '''Get the portion of the string that starts the figure'''
    s = '\\begin{document}\n'
    s += '\\begin{figure}[h]\n'
    s += '\\begin{tikzpicture}[x=%f%s, y=%f%s]\n'%(
        xdim, xunit, ydim, yunit)
    if use_sf:
        s += '\\sffamily\n'
    return s

def get_end_tikz():
    '''Get the final string at the end of the document'''
    s = '\\end{tikzpicture}'
    s += '\\end{figure}'
    s += '\\end{document}'
    return s

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def get_tableau20():
    '''Return 20 nice colors'''
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
    '''
    Get the intersection points along the line segment:

    (x1, y1) + u*(x2 - x1, y2 - y1) = (xmin/xmax, ymin/ymax)

    and sort them for convenience.
    '''

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

def get_2d_plot(xvals, yvals, xscale=1, yscale=1,
                line_dim='thick', color='black', fill_color='white',
                xmin=None, xmax=None, ymin=None, ymax=None,
                symbol=None, symbol_dim='thin', symbol_size=0.15):
    '''
    Create a string representing the 2D plot of a series of
    linesegments. If ymin/ymax, xmin/xmax are specified, clip the plot
    to the box
    '''

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
                        s += r'(%f, %f) '%(xscale*((1.0 - u)*xvals[i] + u*xvals[i+1]),
                                           yscale*((1.0 - u)*yvals[i] + u*yvals[i+1]))
                        draw_on = True

                    u = inter[1]
                    s += r'-- (%f, %f) '%(xscale*((1.0 - u)*xvals[i] + u*xvals[i+1]),
                                          yscale*((1.0 - u)*yvals[i] + u*yvals[i+1]))

                    if u < 1.0:
                        s += ';\n'
                        draw_on = False
                else:
                    u = inter[0]
                    s += r'\draw[%s, color=%s] '%(line_dim, color)
                    s += r'(%f, %f) '%(xscale*((1.0 - u)*xvals[i] + u*xvals[i+1]),
                                       yscale*((1.0 - u)*yvals[i] + u*yvals[i+1]))
                    u = inter[1]
                    s += r'-- (%f, %f);'%(xscale*((1.0 - u)*xvals[i] + u*xvals[i+1]),
                                          yscale*((1.0 - u)*yvals[i] + u*yvals[i+1]))
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
                    xscale*xvals[i], yscale*yvals[i], 0.5*symbol_size)
    elif symbol == 'square':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f, %f) rectangle (%f, %f);'%(
                    symbol_dim, color, fill_color,
                    xscale*xvals[i] - 0.5*symbol_size,
                    yscale*yvals[i] - 0.5*symbol_size,
                    xscale*xvals[i] + 0.5*symbol_size,
                    yscale*yvals[i] + 0.5*symbol_size)
    elif symbol == 'triangle':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f,%f) '%(
                    symbol_dim, color, fill_color,
                    xscale*xvals[i] - 0.45*symbol_size,
                    yscale*yvals[i] - 0.5*symbol_size)
                s += '-- (%f,%f) -- (%f,%f) -- cycle;\n'%(
                    xscale*xvals[i] + 0.45*symbol_size,
                    yscale*yvals[i] - 0.5*symbol_size,
                    xscale*xvals[i], yscale*yvals[i] + 0.5*symbol_size)
    elif symbol == 'delta':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f,%f) '%(
                    symbol_dim, color, fill_color,
                    xscale*xvals[i] - 0.45*symbol_size,
                    yscale*yvals[i] + 0.5*symbol_size)
                s += '-- (%f,%f) -- (%f,%f) -- cycle;\n'%(
                    xscale*xvals[i] + 0.45*symbol_size,
                    yscale*yvals[i] + 0.5*symbol_size,
                    xscale*xvals[i],
                    yscale*yvals[i] - 0.5*symbol_size)
    elif symbol == 'diamond':
        for i in range(n):
            if ((xvals[i] >= xmin and xvals[i] <= xmax) and
                (yvals[i] >= ymin and yvals[i] <= ymax)):
                s += r'\draw[%s, color=%s, fill=%s] (%f,%f) '%(
                    symbol_dim, color, fill_color,
                    xscale*xvals[i] - 0.5*symbol_size, yscale*yvals[i])
                s += '-- (%f,%f) -- (%f,%f) -- (%f,%f) -- cycle;\n'%(
                    xscale*xvals[i], yscale*yvals[i] - 0.5*symbol_size,
                    xscale*xvals[i] + 0.5*symbol_size, yscale*yvals[i],
                    xscale*xvals[i], yscale*yvals[i] + 0.5*symbol_size)

    return s

def get_bar_chart(bars, color_list=None, x_sep=0.25,
                  xmin=None, xmax=None, ymin=None, ymax=None,
                  line_dim='thick', xscale=1, yscale=1,
                  bar_width=None, bar_offset=None):
    '''Get the string for a bar chart'''

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
                    xscale*x1, yscale*y1, xscale*x2, yscale*y2)

    return s

def get_2d_axes(xmin, xmax, ymin, ymax,
                axis_style='r-style',
                xscale=1, yscale=1,
                xticks=[], yticks=[],
                xtick_labels=None, ytick_labels=None,
                tick_font='normalsize', tick_size='semithick',
                label_font='Large', xlabel='x', ylabel='y',
                xlabel_offset=0.1, ylabel_offset=0.15,
                axis_size='thick', axis_color='gray',
                tick_frac=0.05, ):
    '''Draw the axes on the plot'''

    # Find the tick size
    tick_dim = min(tick_frac*(ymax - ymin)*yscale,
                   tick_frac*(xmax - xmin)*xscale)

    # Draw the axes
    s = ''
    if axis_style == 'r-style':
        if len(xticks) >= 2:
            s += '\\draw[%s, color=%s] (%f, %f) -- (%f,%f) -- (%f,%f) -- (%f, %f);'%(
                axis_size, axis_color,
                xscale*xticks[0], yscale*ymin - tick_dim,
                xscale*xticks[0], yscale*ymin,
                xscale*xticks[-1], yscale*ymin,
                xscale*xticks[-1], yscale*ymin - tick_dim)
        if len(yticks) >= 2:
            s += '\\draw[%s, color=%s] (%f, %f) -- (%f,%f) -- (%f,%f) -- (%f, %f);'%(
                axis_size, axis_color,
                xscale*xmin - tick_dim, yscale*yticks[0],
                xscale*xmin, yscale*yticks[0],
                xscale*xmin, yscale*yticks[-1],
                xscale*xmin - tick_dim, yscale*yticks[-1])
    else:
        s += '\\draw[%s, color=%s] (%f,%f) -- (%f,%f);'%(
            axis_size, axis_color, xscale*xmin, yscale*ymin,
            xscale*xmax, yscale*ymin)
        s += '\\draw[%s, color=%s] (%f,%f) -- (%f,%f);'%(
            axis_size, axis_color, xscale*xmin, yscale*ymin,
            xscale*xmin, yscale*ymax)

    # Draw the x-label
    if xlabel is not None:
        s += '\\draw[font=\\%s] (%f, %f) node[below] {%s};'%(
            label_font, 0.5*xscale*(xmin + xmax),
            yscale*(ymin - xlabel_offset*(ymax - ymin)),
            xlabel)

    # Draw the y-label
    if ylabel is not None:
        s += '\\draw[font=\\%s] (%f, %f) node[rotate=90] {%s};'%(
            label_font, xscale*(xmin - ylabel_offset*(xmax - xmin)),
            0.5*yscale*(ymin + ymax),
            ylabel)

    # Draw the ticks on the graph
    if axis_style == 'r-style':
        if xtick_labels is None:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%g};\n'%(
                    xscale*xticks[i], yscale*ymin,
                    xscale*xticks[i], yscale*ymin - tick_dim, xticks[i])
        else:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%s};\n'%(
                    xscale*xticks[i], yscale*ymin,
                    xscale*xticks[i], yscale*ymin - tick_dim, xtick_labels[i])

        # Draw the ticks on the graph
        if ytick_labels is None:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%g};\n'%(
                    xscale*xmin, yscale*yticks[i],
                    xscale*xmin - tick_dim, yscale*yticks[i],
                    yticks[i])
        else:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%s};\n'%(
                    xscale*xmin, yscale*yticks[i],
                    xscale*xmin - tick_dim, yscale*yticks[i],
                    ytick_labels[i])
    else:
        if xtick_labels is None:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%g};\n'%(
                    xscale*xticks[i], yscale*ymin + tick_dim,
                    xscale*xticks[i], yscale*ymin, xticks[i])
        else:
            for i in range(len(xticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[below] {%s};\n'%(
                    xscale*xticks[i], yscale*ymin + tick_dim,
                    xscale*xticks[i], yscale*ymin, xtick_labels[i])

        # Draw the ticks on the graph
        if ytick_labels is None:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%g};\n'%(
                    xscale*xmin + tick_dim, yscale*yticks[i],
                    xscale*xmin, yscale*yticks[i],
                    yticks[i])
        else:
            for i in range(len(yticks)):
                s += '\\draw[font=\\%s, %s, color=%s, text=black] '%(
                    tick_font, tick_size, axis_color)
                s += '(%f, %f) -- (%f, %f) node[left] {%s};\n'%(
                    xscale*xmin + tick_dim, yscale*yticks[i],
                    xscale*xmin, yscale*yticks[i],
                    ytick_labels[i])

    return s

def get_legend_entry(x, y, length, xscale=1, yscale=1,
                     font_size='large',
                     line_dim='thick', color='black',
                     symbol=None, symbol_dim='thin',
                     symbol_size=0.15, label=''):
    '''Add a single entry to the legend'''

    # Plot a line segment
    xvals = [x - 0.5*length, x + 0.5*length]
    yvals = [y, y]

    s = get_2d_plot(xvals, yvals, xscale=xscale, yscale=yscale,
                    line_dim=line_dim, color=color,
                    symbol=symbol, symbol_dim=symbol_dim,
                    symbol_size=symbol_size)

    s += '\\draw[font=\\%s] (%f,%f) node[right] {%s};'%(
        font_size, xscale*(x + 0.75*length), yscale*y, label)

    return s
