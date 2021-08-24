#--------------------------------------------------------------------------------------------------------
# Project： dlaais.ctp
# Description:
#   processing functions for CTP processing
# File Name:
#   __init__.py
# Creation Date:
#   2021.08.23
# Modification Date:
#   2021.08.23
#--------------------------------------------------------------------------------------------------------

import numpy as np
import nibabel as nib

#--------------------------------------------------------------------------------------------------------
#
def generate_brain_mask(ctp_nii_file, mask_nii_file):
    """
    """
    nib_ctp = nib.load(ctp_nii_file)
    np_ctp = nib_ctp.get_fdata()
    np_max = np.max(np_ctp, axis=-1)
    np_mean = np.mean(np_ctp, axis=-1)
    np_working = np_max - np_mean
    np_mask = np.zeros(np_working.shape, dtype=np.int8)
    np_mask[np_working>10] = 1
    nib_mask = nib.Nifti1Image(np_mask, affine=nib_ctp.affine)
    nib.save(nib_mask, mask_nii_file)