import tikzplots as tikz
import numpy as np

# Create the basis function data
n = 300
xi = np.linspace(-1, 1, n)

# Plot Lagrange polynomials at the Gauss-Lobatto points
p = 5
knots = -np.cos(np.linspace(0, np.pi, p+1))
Nlist = []
for i in range(p+1):
    N = np.ones(n)
    for j in range(p+1):
        if i != j:
            N *= (xi - knots[j])/(knots[i] - knots[j])
    Nlist.append(N)

# Extract the colors for the lines. This creates a red-blue color scheme for an arbitrary number
# of curves.
colors = tikz.get_blue_red_colors(p+1)

# Create the header for the plot. Note that all the data is written to a string
# that is then printed out to the file
s = tikz.get_header()

# Add the string to the beginning of the figure. This sets the overall dimensions, and the
# units used to specify the dimensions
s += tikz.get_begin_tikz(xdim=2.75, ydim=2.25, xunit='in', yunit='in')

# Specify any tick locations
yticks = [-0.25, 0, 0.5, 1.0]

# You can optionally specify tick labels
xticks = knots
xtick_labels = []
for k in knots:
    xtick_labels.append('%.2g'%(k))

# Set the scale factor applied to the plotting data. This can also be used to
# indirectly control the thickness of all the lines. Smaller scaling factors 
# produce thicker lines
xscale = 0.75
yscale = 0.75

# Set the view box in the data coordinates (scaling is applied after)
xmin = -1.1
xmax = 1.1
ymin = -0.35
ymax = 1.05

# Set relative dimensions of tick fraction
tick_frac = 0.01
xlabel_offset = 0.15
ylabel_offset = 0.08

for icolor, N in enumerate(Nlist):
    # Set the color index
    s += r'\definecolor{customcolor}{RGB}{%d,%d,%d}'%(
        colors[icolor % len(colors)][0],
        colors[icolor % len(colors)][1],
        colors[icolor % len(colors)][2])
    
    # Plot the shape function values
    s += tikz.get_2d_plot(xi, N,
                          xscale=xscale, yscale=yscale,
                          color='customcolor', line_dim='ultra thick',
                          xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

# Plot the axes
s += tikz.get_2d_axes(xmin, xmax, ymin, ymax,
                      tick_frac=tick_frac, ylabel_offset=ylabel_offset,
                      label_font='LARGE',
                      xscale=xscale, yscale=yscale,
                      xticks=xticks, xtick_labels=xtick_labels,
                      yticks=yticks, tick_font='large',
                      xlabel=r'$\xi$',
                      ylabel=r'$N(\xi)$')

# Finalize the output string
s += tikz.get_end_tikz()

# Write the whole string to a file
fp = open('basis_functions.tex', 'w')
fp.write(s)
fp.close()
