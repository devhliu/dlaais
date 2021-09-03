#--------------------------------------------------------------------------------------------------------
# Project： dlaais.ants.nii2png
# Description:
#   nii2png view processing functions using ants
# File Name:
#   registration.py
# Creation Date:
#   2021.08.18
# Modification Date:
#   2021.08.18
#--------------------------------------------------------------------------------------------------------

import os
import ants
import shutil

import numpy as np
import nibabel as nib

#--------------------------------------------------------------------------------------------------------
#
def conv_4dnii2mosaicpng(nii_file, out_png_file, matrix_size=(64, 64), cols=4, rows=4):
    """
    """
    ants_img = ants.image_read(nii_file)
    
    return