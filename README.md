# Tiff-Analyser

-	Change the file name to read in on line 27
-	The code first shows a full image which you should use to determine the pixel values of the centre of the beam profile and the approximate width (plus a little bit either side). If you record these values when the code shows this image, when you close the image you can type them into the terminal. Or if you prefer you can hard code them into the code on line 55-57
-	If you leave the height and width blank it will use the whole image, unless you change that specifically
-	The code did have dose calculations based on the film I was analysing but I removed this so the colour mapping might be a bit weird
-	I have the size of the final plots specifically designed so that the side plots line up nicely with the main plot, if you want to make the image bigger for saving then change the max height variable on line 179, I’ve left it at 6 for now because otherwise it doesn’t fit on a laptop screen, but if you uncomment the save image lines at the bottom of both plotting sections (lines 234 and 284) it will save at the size you define
