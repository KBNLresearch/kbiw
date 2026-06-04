#! /usr/bin/env python3

"""Comnvert paletted image to regular image
"""

import pyvips

def convertPaletted (imageIn, imageOut):
    # Re-saves input image, which results in non-paletted output image
    try:
        im1 = pyvips.Image.new_from_file(imageIn, access="sequential")
        im1.write_to_file(imageOut)
        success = True
    except Exception:
        success = False

    return success

