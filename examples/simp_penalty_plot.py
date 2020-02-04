'''
The following code creates a figure for the linearization of the
SIMP/RAMP penalization. This illustrates that the linearization always
falls below the actual penalty value.
'''

import numpy as np
import tikzplots as tikz

# Create the range of design variable values
x = np.linspace(0, 1, 150)

xmin = -0.05
xmax = 1.0
ymin = 0.0
ymax = 1.0

# Set the penalty parameter values
p = 3.0
q = 5.0

# Set the value of the base point
x0 = 0.5

# Set the full penalty values
SIMP = x**p
RAMP = x/(1.0 + q*(1.0 - x))

# Set the linearizations
xSIMP = np.linspace(1.0/p*x0, 1.0, 100)
ySIMP = x0**p + (p*x0**(p-1.0))*(xSIMP - x0)

xscale = 1.0
yscale = 1.0
tick_frac = 0.02

xticks = [0, 0.25, 0.5, 0.75, 1]
yticks = [0, 0.25, 0.5, 0.75, 1]

xlabel_offset = 0.15
ylabel_offset = 0.15

# Set the colours to use
colors = ['Red', 'NavyBlue', 'black', 'ForestGreen', 'Gray']

# Create the SIMP version of the plot
s = tikz.get_header()
s += tikz.get_begin_tikz(xdim=2.75, ydim=2.75, xunit='in', yunit='in')

s += tikz.get_2d_plot([x0, x0], [-0.01, 0.025], 
                      xscale=xscale, yscale=yscale,
                      color='black', line_dim='ultra thick',
                      xmin=xmin, xmax=xmax, ymin=-ymax, ymax=ymax)

s += tikz.get_2d_plot([(1.0 - 1.0/p)*x0, (1.0 - 1.0/p)*x0], [-0.01, 0.025], 
                      xscale=xscale, yscale=yscale,
                      color='black', line_dim='ultra thick',
                      xmin=xmin, xmax=xmax, ymin=-ymax, ymax=ymax)

s += tikz.get_2d_plot(x, SIMP, xscale=xscale, yscale=yscale,
                      color='Gray', line_dim='ultra thick',
                      xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                      symbol=None)
s += tikz.get_2d_plot(xSIMP, ySIMP, xscale=xscale, yscale=yscale,
                      color=colors[1], line_dim='ultra thick',
                      xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                      symbol=None)

s += tikz.get_2d_plot([x0], [x0**p], xscale=xscale, yscale=yscale,
                      color='black', line_dim='ultra thick',
                      xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                      symbol='circle', symbol_size=0.02)

s += r'\draw[font=\normalsize] (%f, %f) node[fill=white] {%s} -- (%f, %f);'%(
    0.4*xscale, 0.6*yscale, 
    r'$x_{0}^{p} + p x_{0}^{p-1}(x - x_{0})$', xSIMP[65], ySIMP[65])

s += r'\draw[font=\normalsize] (%f, %f) node[fill=white] {%s} -- (%f, %f);'%(
    0.55*xscale, 0.075*yscale, '$x_{0}$', 0.5*xscale, 0*yscale)

s += r'\draw[font=\normalsize] (%f, %f) node[fill=white] {%s} -- (%f, %f);'%(
    0.1*xscale, 0.2*yscale, r'$(1 - p^{-1})x_{0}$',
    (1.0 - 1.0/p)*x0*xscale, 0*yscale)

# Plot the axes
s += tikz.get_2d_axes(xmin, xmax, ymin, ymax,
                      tick_frac=tick_frac, ylabel_offset=ylabel_offset,
                      xscale=xscale, yscale=yscale,
                      xticks=xticks, yticks=yticks,
                      xlabel='$x$', ylabel='$w(x)$')

s += tikz.get_end_tikz()

fp = open('simp_penalty_linearized.tex', 'w')
fp.write(s)
fp.close()
