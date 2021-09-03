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

import os

import numpy as np
import nibabel as nib

#--------------------------------------------------------------------------------------------------------
#
def generate_brain_mask_from_CTP(ctp_nii_file, phase=0, label='mask', ext='.nii.gz'):
    """
    """
    # calculate mask nii filename
    file_root = os.path.dirname(ctp_nii_file)
    file_basename = os.path.basename(ctp_nii_file)
    if file_basename.endswith('.nii'): mask_filename = file_basename[:-4] + '_' + label + ext
    elif file_basename.endswith('.nii.gz'): mask_filename = file_basename[:-7] + '_' + label + ext
    else: mask_filename = file_basename + '_' + label + ext
    mask_nii_file = os.path.join(file_root, mask_filename)

    # 
    nib_ctp = nib.load(ctp_nii_file)
    np_ctp = nib_ctp.get_fdata()
    np_max = np.max(np_ctp, axis=-1)
    np_mean = np.mean(np_ctp, axis=-1)
    np_working = np_max - np_mean
    np_mask = np.zeros(np_working.shape, dtype=np.int8)
    np_mask[np_working>10] = 1
    nib_mask = nib.Nifti1Image(np_mask, affine=nib_ctp.affine)
    nib.save(nib_mask, )
#--------------------------------------------------------------------------------------------------------
#
def generate_phase_from_CTP(ctp_nii_file, ctp_phase=0, ext='.nii.gz'):
    """
    """
    # calculate ctp phase nii filename
    label = '{:04d}'.format(ctp_phase) 
    file_root = os.path.dirname(ctp_nii_file)
    file_basename = os.path.basename(ctp_nii_file)
    if file_basename.endswith('.nii'): ctp_phase_filename = file_basename[:-4] + '_' + label + ext
    elif file_basename.endswith('.nii.gz'): ctp_phase_filename = file_basename[:-7] + '_' + label + ext
    else: ctp_phase_filename = file_basename + '_' + label + ext
    ctp_phase_nii_file = os.path.join(file_root, ctp_phase_filename)

    # 
    nib_ctp = nib.load(ctp_nii_file)
    np_ctp = nib_ctp.get_fdata()
    np_phase = np_ctp[:,:,:,0]
    if ctp_phase < np_ctp.shape[3]: np_phase = np_ctp[:,:,:,ctp_phase]
    nib_phase = nib.Nifti1Image(np_phase, affine=nib_ctp.affine)
    nib.save(nib_phase, ctp_phase_nii_file)