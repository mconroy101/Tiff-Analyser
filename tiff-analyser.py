import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from PIL import Image
from PIL.TiffTags import TAGS

import cv2 as cv

SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)    # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

matplotlib.rcParams['mathtext.fontset'] = 'custom'
matplotlib.rcParams['mathtext.rm'] = 'DejaVu Sans'
matplotlib.rcParams['mathtext.it'] = 'DejaVu Sans:italic'
matplotlib.rcParams['mathtext.bf'] = 'DejaVu Sans:bold'

# Define path to image specified
image_name = f"flash 6.tif"

# Open 16 bit TIFF file in channel order BGR
# -1 flag prevents compression to 8 bit image
im = cv.imread(image_name, -1)
im_8 = (im/256).astype('uint8')


# Get image metadata
PIL_image = Image.open(image_name)
meta_dict = {TAGS[key] : PIL_image.tag[key] for key in PIL_image.tag_v2}
dpi_x = meta_dict['XResolution'][0][0]
image_width = meta_dict['ImageWidth'][0]
image_height = meta_dict['ImageLength'][0]


# Conversion factor from pixel number to mm
pix_mm = 25.4 / dpi_x

plt.imshow(im_8)
plt.title("Record x and y coordinate (pixel number) of centre of beam spot as well as width of beam")
plt.show()


# #############################################################################
#Enter Values Here:

# Location of beam parameters which code will default to if nothing entered below
c = (877,1460)      # Enter centre point in pixel number of beam
w = image_width     # Enter width of beam spot
h = image_height    # Enter height of beam spot


# #############################################################################


# Allows user to enter values of centre and width through terminal
try:
    cx = int(input('Enter x coordinate of centre of beam spot: '))
    cy = int(input('Enter y coordinate of centre of beam spot: '))
    c = cx,cy
    
except:
    #c = (image_width/2), (image_height/2)
    pass

try:
    w = int(input('Enter width of beam spot in pixels, or leave blank for full image width: '))
    
except:
    #w = image_width
    pass

try:
    h = int(input('Enter height of beam spot in pixels, or leave blank for full image width: '))
    
except:
    #h = image_height
    pass

# Select red channel (BGR format)
red = im[:,:,2]
print(np.shape(red))

# Dose conversion, ignore
'''
# Convert to dose profile 
# Enter zero dose OD offset
OD_0 = 0.212778715
# Convert to net optical density
scanner_max = 65335.0
net_OD_profile = np.log10(scanner_max/red) - OD_0   # Subtract zero point OD 
# Dose calibration paramters
popt = (3.99990045e+01, 1.28648613e+01, 3.91353102e+00, 2.66929284e-02)

def polynomial(x, a, b, c, d):
    
    y = a*x**3 + b*x**2 + c*x + d
    
    return y

# Convert to dose profile
dose_profile = polynomial(net_OD_profile, *popt)
'''

# If not correcting for dose, then use this line below and comment out above
dose_profile = red

#print(c, w, h)

# Define crop limits based on user inputs
x_min, x_max = c[0] - w/2, c[0] + w/2
y_min, y_max = c[1] - h/2, c[1] + h/2

#print(x_min, x_max)
#print(y_min, y_max)

# Ensure cropping does not go out of bounds of image
if x_min < 0:
    diff = 0 - x_min
    x_min = 0
    x_max -= diff
    print(f'x_min: {x_min}')
    
if x_max > image_width:
    diff = x_max - image_width
    x_max = image_width
    x_min += diff
    print(f'xmax: {x_max}')
    
if y_min < 0:
    diff = 0 - y_min
    y_min = 0
    y_max -= diff
    print(f'y_min: {y_min}')
    
if y_max > image_height:
    diff = y_max - image_height
    y_max = image_height
    y_min += diff
    print(f'y_max: {y_max}')

# Crop image based on values above to place beam spot at centre
dose_profile_cut = dose_profile[int(y_min):int(y_max),int(x_min):int(x_max)]

# Sum along y axis
y_sum = np.mean(dose_profile_cut, axis=0)
# Sum along x axis
x_sum = np.mean(dose_profile_cut, axis=1)

# Get central x and y axis location of plot to show
cy = int(np.shape(dose_profile_cut)[0]/2)
cx = int(np.shape(dose_profile_cut)[1]/2)

# Slice along x axis, averageraging over 5 pixel wide stip
x_slice = dose_profile_cut[:,cy-2:cy+2]
x_slice = np.mean(x_slice, axis=1)

# Slice along y axis, averageraging over 5 pixel wide stip
y_slice = dose_profile_cut[cx-2:cx+2,:]
y_slice = (np.mean(y_slice, axis=0))

# Define x and y axes indices for side profile plots (in pixel no.)
y_i = np.arange(0, np.shape(x_slice)[0], 1)
x_i = np.arange(0, np.shape(y_slice)[0], 1)

# Convert pixel numbers to mm for main image display
ext = [0, np.max(x_i)*pix_mm, np.max(y_i)*pix_mm, 0] # Note: Fails here!

# Image sizing for proper display
###############################################################################
# Enter maximum height of image (depends on monitor for viewing, or enter 12 for saving)
max_height = 6  # 12
###############################################################################

image_h_w_ratio = np.shape(dose_profile_cut)[0] / np.shape(dose_profile_cut)[1]
im_h = 2*(max_height - 0.25)/3
im_w = im_h / image_h_w_ratio
max_width = 14*im_w/8 + 0.75

# PLOT 1
# Create plot with image in centre and summed profiles either side
fig, ax = plt.subplots(2,4, figsize=(max_width,max_height), gridspec_kw={'height_ratios': [1, 2], 'width_ratios': [1,1,8,4]})
fig.suptitle(f'Film 6 summed dose profile')

# Top profile plot
ax[0,2].plot(x_i*pix_mm, y_sum)
ax[0,2].set_ylabel('Dose (Gy)')
ax[0,2].sharex(ax[1,2])
ax[0,2].set_title('x axis dose profile')

# Side profile plot
ax[1,3].plot(x_sum, (y_i)*pix_mm)
ax[1,3].set_title('y axis dose profile')
ax[1,3].set_xlabel('Dose (Gy)')
ax[1,3].sharey(ax[1,2])

# Main image
mp = ax[1,2].imshow(dose_profile_cut, extent=ext)
ax[1,2].set_xlabel('Pixel x Position (mm)')
ax[1,2].set_ylabel('Pixel y Position (mm)')

ax[1,2].axhline(cy*pix_mm, color='r')
ax[1,2].axvline(cx*pix_mm, color='r')

# Hide unused axis
ax[0,0].axis('off')
ax[0,1].axis('off')
ax[0,3].axis('off')
ax[1,1].axis('off')

# Colourbar setup
ax[1,0].spines['top'].set_visible(False)
ax[1,0].spines['left'].set_visible(False)
ax[1,0].spines['right'].set_visible(False)
ax[1,0].spines['bottom'].set_visible(False)
ax[1,0].get_xaxis().set_ticks([])
ax[1,0].get_yaxis().set_ticks([])
ax[1,0].set_ylabel('Dose (Gy)')

cbar_loc = ax[1,0].inset_axes([1,0, 0.2, 1])
cb = fig.colorbar(mp, ax=ax[1,0], cax=cbar_loc)
cb.ax.yaxis.set_ticks_position('left')


# Final whitespace adjustment and save image
plt.subplots_adjust(wspace=0.25, hspace=0.25)
#plt.savefig(f'27 April 23 Cyclotron Run/Film {film_no} summed dose profile_code4tony.png')
plt.show()


# PLOT 2
# Create plot with image in centre and sliced profiles either side
fig, ax = plt.subplots(2,4, figsize=(max_width,max_height), gridspec_kw={'height_ratios': [1, 2], 'width_ratios': [1,1,8,4]})
fig.suptitle(f'Film 6 sliced dose profile')

# Top profile plot
ax[0,2].plot(x_i*pix_mm, y_slice)
ax[0,2].set_title('x axis dose profile')
ax[0,2].set_ylabel('Dose (Gy)')
ax[0,2].sharex(ax[1,1])

# Side profile plot
ax[1,3].plot(x_slice, (y_i)*pix_mm)
ax[1,3].set_title('y axis dose profile')
ax[1,3].set_xlabel('Dose (Gy)')
ax[1,3].sharey(ax[1,1])

# Main image
mp = ax[1,2].imshow(dose_profile_cut, extent=ext)
ax[1,2].set_xlabel('Pixel x Position (mm)')
ax[1,2].set_ylabel('Pixel y Position (mm)')

ax[1,2].axhline(cy*pix_mm, color='r')
ax[1,2].axvline(cx*pix_mm, color='r')

# Hide unused axis
ax[0,0].axis('off')
ax[0,1].axis('off')
ax[0,3].axis('off')
ax[1,1].axis('off')

# Setup colourbar
ax[1,0].spines['top'].set_visible(False)
ax[1,0].spines['left'].set_visible(False)
ax[1,0].spines['right'].set_visible(False)
ax[1,0].spines['bottom'].set_visible(False)
ax[1,0].get_xaxis().set_ticks([])
ax[1,0].get_yaxis().set_ticks([])
ax[1,0].set_ylabel('Dose (Gy)')

cbar_loc = ax[1,0].inset_axes([1,0, 0.2, 1])
cb = fig.colorbar(mp, ax=ax[1,0], cax=cbar_loc)
cb.ax.yaxis.set_ticks_position('left')

# Final whitespace adjustment and save image
plt.subplots_adjust(wspace=0.25, hspace=0.25)
#plt.savefig(f'27 April 23 Cyclotron Run/Film {film_no} dose profile slice {days}_code4tony.png')
plt.show()

