import tikzplots as tikz
import numpy as np

n = 250
x = np.linspace(-1.25, 1.25, n)
y = np.linspace(-1.25, 1.25, n)

X, Y = np.meshgrid(x, y)
F = (1 - X)**2 + 100*(Y - X**2)**2

tris = []
for j in range(n-1):
    for i in range(n-1):
        tris.append([i + n*j, i+1 + n*j, i+1 + n*(j+1)])
        tris.append([i + n*j, i+1 + n*(j+1), i + n*(j+1)])

# Set the contour levels
levs = [0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
colors = tikz.get_blue_red_colors(len(levs))

# Create the header for the plot. Note that all the data is written to a string
# that is then printed out to the file
s = tikz.get_header()

# Add the string to the beginning of the figure. This sets the overall dimensions, and the
# units used to specify the dimensions
s += tikz.get_begin_tikz(xdim=2.0, ydim=2.0, xunit='in', yunit='in')

# Specify any tick locations
xticks = [-1.25, -1, 0, 1, 1.25]
yticks = [-1.25, -1, 0, 1, 1.25]

# Set the scale factor applied to the plotting data. This can also be used to
# indirectly control the thickness of all the lines. Smaller scaling factors
# produce thicker lines
xscale = 1.0
yscale = 1.0

# Set the view box in the data coordinates (scaling is applied after)
xmin = -1.30
xmax = 1.30
ymin = -1.30
ymax = 1.30

# Set relative dimensions of tick fraction
tick_frac = 0.01
xlabel_offset = 0.15
ylabel_offset = 0.08

# Set the contour colors
lev_colors = []
for index, c in enumerate(colors):
    s += r'\definecolor{contour%d}{RGB}{%d,%d,%d}'%(index, c[0], c[1], c[2])
    lev_colors.append('contour%d'%(index))

x = X.flatten()
y = Y.flatten()
vals = F.flatten()
s += tikz.get_2d_tri_contour_plot(x, y, vals, tris, levs, lev_colors=lev_colors,
                                  xscale=xscale, yscale=yscale, line_dim='ultra thick',
                                  xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

# Plot the axes
s += tikz.get_2d_axes(xmin, xmax, ymin, ymax,
                      tick_frac=tick_frac, ylabel_offset=ylabel_offset,
                      label_font='LARGE',
                      xscale=xscale, yscale=yscale,
                      xticks=xticks, yticks=yticks, tick_font='large',
                      xlabel=r'$x_{1}$', ylabel=r'$x_{2}$')

# Finalize the output string
s += tikz.get_end_tikz()

# Write the whole string to a file
fp = open('rosenbrock_contour.tex', 'w')
fp.write(s)
fp.close()
