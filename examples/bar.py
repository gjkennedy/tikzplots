import tikzplots as tikz
import numpy as np

# Create the data
n = 10
b1 = 1.0/np.linspace(0.5, 1, n)
b2 = 1.0/np.linspace(0.5, 1, n)**2
b3 = np.linspace(0.1, 1, n)
b4 = np.linspace(0.1, 1, n)**2

bars = []
for i in range(n):
    bars.append([b1[i], b2[i], b3[i], b4[i]])

# Set the scale
xscale = 0.25
yscale = 0.5

# Set the view box in the data coordinates (scaling is applied after)
xmin = 0.75
xmax = 11.25
ymin = -0.1
ymax = 2.05

xticks = [1, 5, 10]
yticks = [0, 1, 2]

# Set relative dimensions of tick fraction
tick_frac = 0.01
xlabel_offset = 0.15
ylabel_offset = 0.08

# Create the SIMP version of the plot
s = tikz.get_header()
s += tikz.get_begin_tikz(xdim=1.75, ydim=2.75, xunit='in', yunit='in')

# Create the custom colors
color_list = []
colors = tikz.get_colors('default')
for i in range(4):
    # Set the color index
    s += r'\definecolor{cust%d}{RGB}{%d,%d,%d}'%(i,
        colors[i % len(colors)][0],
        colors[i % len(colors)][1],
        colors[i % len(colors)][2])
    color_list.append('cust%d'%(i))

# 40 bars
x_sep = 0.0
bar_offset = 0.05
bar_width = 0.2
s += tikz.get_bar_chart(bars, color_list=color_list, x_sep=x_sep,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        line_dim='thick', xscale=xscale, yscale=yscale,
                        bar_width=bar_width, bar_offset=bar_offset)

# Plot the axes
s += tikz.get_2d_axes(xmin, xmax, ymin, ymax,
                      tick_frac=tick_frac, ylabel_offset=ylabel_offset,
                      xscale=xscale, yscale=yscale,
                      xticks=xticks, yticks=yticks,
                      xlabel=None, ylabel=None)

s += tikz.get_end_tikz()

fp = open('bar_plot.tex', 'w')
fp.write(s)
fp.close()
