#--------------------------------------------------------------------------------------------------------
# Project： dlaais.ants.registration
# Description:
#   registration processing functions using ants
# File Name:
#   registration.py
# Creation Date:
#   2021.08.18
# Modification Date:
#   2021.08.18
#--------------------------------------------------------------------------------------------------------

import os
import shutil
import subprocess

import nibabel as nib

from glob import glob

#--------------------------------------------------------------------------------------------------------
#
def reg_3d_nifti_groups(series_root, ref_file, in_filenames, out_filenames):
    """
    :param series_root:
    :param ref_file:
    :param in_filenames:
    :param out_filenames:
    :return:
    """
    for in_filename, out_filename in zip(in_filenames, out_filenames):
        print('working on %s - %s'%(series_root, in_filename))
        in_file = os.path.join(series_root, in_filename + '.nii.gz')
        out_file = os.path.join(series_root, out_filename)
        out_nii_file = out_file + '.nii.gz'
        if not os.path.exists(in_file): continue
        if os.path.exists(out_nii_file): continue
        subprocess.call(['antsRegistrationSyNQuick.sh',
                         '-d', '3', '-r', '64', '-p', 'f', '-j', '1', '-n', '16',
                         '-f', ref_file, '-m', in_file, '-o', out_file])
        shutil.copy(os.path.join(series_root, out_filename + 'Warped.nii.gz'),
                    os.path.join(series_root, out_filename + '.nii.gz'))
        rm_files = glob(os.path.join(series_root, out_filename + '*.nii.gz'))
        rm_files += glob(os.path.join(series_root, '*.mat'))
        for rm_file in rm_files:
            if rm_file == out_nii_file: continue
            os.remove(rm_file)
        os.remove(in_file)
    return
#--------------------------------------------------------------------------------------------------------
#
def reg_4d_nifti(patient_niix_root, dyn_1min_4d_niifilename, ref_nii_file='First'):
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
    N = np_4d_img.shape[-1]
    in_filenames = []
    out_filenames = []
    for i in range(N):
        np_3d_img_1min = np_4d_img[:, :, :, i]
        nib_3d_img_1min = nib.Nifti1Image(np_3d_img_1min, affine=affine)
        nib.save(nib_3d_img_1min, os.path.join(dyn_4d_mc_nii_root, dyn_1min_4d_niifilename + '_{:04d}.nii.gz'.format(i)))
        in_filenames.append(dyn_1min_4d_niifilename + '_{:04d}'.format(i))
        out_filenames.append(dyn_1min_4d_niifilename + '_{:04d}_mc'.format(i))
    
    # select the reference file
    if ref_nii_file == 'First':
        ref_file = os.path.join(dyn_4d_mc_nii_root, in_filenames[0] + '.nii.gz')
    elif ref_nii_file == 'Last':
        ref_file = os.path.join(dyn_4d_mc_nii_root, in_filenames[-1] + '.nii.gz')
    else:
        ref_file = ref_nii_file
    if os.path.exists(ref_file): return False

    # make registration
    reg_3d_nifti_groups(dyn_4d_mc_nii_root, ref_file, in_filenames, out_filenames)

    # collect mc nii files
    nib_imgs = [nib.load(os.path.join(dyn_4d_mc_nii_root, out_filename + '.nii.gz')) for out_filename in out_filenames]
    nib_4d_img = nib.concat_images(nib_imgs)
    nib.save(nib_4d_img, dyn_4d_mc_niifile)

    # remove temp files
    if os.path.exists(dyn_4d_mc_nii_root): shutil.rmtree(dyn_4d_mc_nii_root)
    return True