#--------------------------------------------------------------------------------------------------------
# Project： dlaais.ants.segmentation
# Description:
#   segmentation processing functions using ants
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
def seg_brain_by_threshold(ncct_nii_file, low_thres=0, high_thres=255):
    """
    """
    ncct_brain_nii_file = ncct_nii_file.replace('.nii.gz', '_brain0.nii.gz')
    nib_ncct = nib.load(ncct_nii_file)
    np_ncct = nib_ncct.get_fdata()
    np_brain_ncct = np.zeros(np_ncct.shape, dtype=np.short)
    np_brain_ncct[np_ncct<=low_thres]=0
    np_brain_ncct[np_ncct>high_thres]=0
    nib_brain_ncct = nib.Nifti1Image(np_brain_ncct, affine=nib_ncct)
    nib.save(nib_brain_ncct, ncct_brain_nii_file)
    return
#--------------------------------------------------------------------------------------------------------
#
def seg_brain(ncct_nii_file, priors=None):
    """
    """
    return
#--------------------------------------------------------------------------------------------------------
#
def rigid_reg_3d_nifti_groups(series_root, ref_file, in_filenames, out_filenames):
    """
    :param series_root:
    :param ref_file:
    :param in_filenames:
    :param out_filenames:
    :return:
    """
    if not os.path.exists(ref_file): return False
    fi = ants.image_read(ref_file)
    for in_filename, out_filename in zip(in_filenames, out_filenames):
        print('working on %s - %s'%(series_root, in_filename))
        in_file = os.path.join(series_root, in_filename + '.nii.gz')
        out_file = os.path.join(series_root, out_filename)
        out_nii_file = out_file + '.nii.gz'
        if not os.path.exists(in_file): continue
        if os.path.exists(out_nii_file): continue
        mv = ants.image_read(in_file)
        mx = ants.registration(fixed=fi, moving=mv, type_of_transform='Rigid', 
                               reg_iterations=(10, 10, 0), aff_iterations=(400, 200, 200, 10))
        ants.image_write(mx['warpedmovout'], out_nii_file)
    return

#--------------------------------------------------------------------------------------------------------
#
def rigid_reg_4d_nifti(patient_niix_root, dyn_1min_4d_niifilename, ref_nii_file='First'):
    """
    :param patient_niix_root:
    :param dyn_1min_4d_niifile:
    :param ref_nii_file:        'First', 'Last', 'real file link'
    :return:
    """
    # decompose 4d nifti file
    dyn_4d_niifile = os.path.join(patient_niix_root, dyn_1min_4d_niifilename + '.nii.gz')
    dyn_4d_mc_niifile = os.path.join(patient_niix_root, dyn_1min_4d_niifilename + '_mc.nii.gz')
    if os.path.exists(dyn_4d_mc_niifile): return True
    dyn_4d_mc_nii_root = os.path.join(patient_niix_root, dyn_1min_4d_niifilename)
    if os.path.exists(dyn_4d_mc_nii_root): shutil.rmtree(dyn_4d_mc_nii_root)
    os.makedirs(dyn_4d_mc_nii_root, exist_ok=True)
    nib_4d_img = nib.load(dyn_4d_niifile)
    affine = nib_4d_img.affine
    np_4d_img = nib_4d_img.get_fdata()
    dtype = np_4d_img.dtype
    N = np_4d_img.shape[-1]
    in_filenames = []
    out_filenames = []
    for i in range(N):
        np_3d_img_1min = np_4d_img[:, :, :, i]
        nib_3d_img_1min = nib.Nifti1Image(np_3d_img_1min, affine=affine)
        nib.save(nib_3d_img_1min, os.path.join(dyn_4d_mc_nii_root, dyn_1min_4d_niifilename + '_{:04d}.nii.gz'.format(i)))
        in_filenames.append(dyn_1min_4d_niifilename + '_{:04d}'.format(i))
        out_filenames.append(dyn_1min_4d_niifilename + '_{:04d}_mc'.format(i))
    np_4d_img = None
    nib_4d_img = None

    # select the reference file
    if ref_nii_file == 'First':
        ref_file = os.path.join(dyn_4d_mc_nii_root, in_filenames[0] + '.nii.gz')
    elif ref_nii_file == 'Last':
        ref_file = os.path.join(dyn_4d_mc_nii_root, in_filenames[-1] + '.nii.gz')
    else:
        ref_file = ref_nii_file
    if not os.path.exists(ref_file): return False

    # make registration
    rigid_reg_3d_nifti_groups(dyn_4d_mc_nii_root, ref_file, in_filenames, out_filenames)

    # collect mc nii files
    nib_imgs = [nib.load(os.path.join(dyn_4d_mc_nii_root, out_filename + '.nii.gz')) for out_filename in out_filenames]
    nib_4d_img_mc = nib.concat_images(nib_imgs)
    np_4d_img_mc = nib_4d_img_mc.get_fdata()
    np_4d_img_mc_new = np_4d_img_mc.astype(dtype)
    nib_4d_img_mc_new = nib.Nifti1Image(np_4d_img_mc_new, affine=affine)
    nib.save(nib_4d_img_mc_new, dyn_4d_mc_niifile)

    # remove temp files
    if os.path.exists(dyn_4d_mc_nii_root): shutil.rmtree(dyn_4d_mc_nii_root)
    return True

#--------------------------------------------------------------------------------------------------------
#
