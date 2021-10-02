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
import ants
import shutil

import nibabel as nib


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
    fi_mask = ants.get_mask(fi, low_thresh=None, high_thresh=None)
    fi = ants.mask_image(fi, fi_mask)
    for in_filename, out_filename in zip(in_filenames, out_filenames):
        print('working on %s - %s'%(series_root, in_filename))
        in_file = os.path.join(series_root, in_filename + '.nii.gz')
        out_file = os.path.join(series_root, out_filename)
        out_nii_file = out_file + '.nii.gz'
        if not os.path.exists(in_file): continue
        mv = ants.image_read(in_file)
        mv_mask = ants.get_mask(mv, low_thresh=None, high_thresh=None)
        mv = ants.mask_image(mv, mv_mask)
        mx = ants.registration(fixed=fi, moving=mv, type_of_transform='QuickRigid', mask=fi_mask,
                               reg_iterations=(5, 5, 0), aff_iterations=(20, 10, 10, 10))
        mv_rigid = mx['warpedmovout']
        ants.image_write(mv_rigid, out_nii_file)
    return

#--------------------------------------------------------------------------------------------------------
#
def rigid_reg_4d_nifti(series_root, dyn4d_nii_filename, ref_nii_file='First', ext='_mc'):
    """
    :param series_root:
    :param dyn4d_nii_filename:
    :param ref_nii_file:        'First', 'Last', 'real file link'
    :param ext:                 '_mc'
    :return:
    """
    # decompose 4d nifti file for quick rigid registration
    dyn_4d_niifile = os.path.join(series_root, dyn4d_nii_filename + '.nii.gz')
    dyn_4d_mc_niifile = os.path.join(series_root, dyn4d_nii_filename + ext + '.nii.gz')
    if os.path.exists(dyn_4d_mc_niifile): return True
    dyn_4d_mc_nii_root = os.path.join(series_root, dyn4d_nii_filename)
    if os.path.exists(dyn_4d_mc_nii_root): shutil.rmtree(dyn_4d_mc_nii_root)
    if not os.path.exists(dyn_4d_mc_nii_root):
        os.makedirs(dyn_4d_mc_nii_root, exist_ok=True)
        nib_4d_img = nib.load(dyn_4d_niifile)
        affine = nib_4d_img.affine
        np_4d_img = nib_4d_img.get_fdata()
        dtype = np_4d_img.dtype
        
        if len(np_4d_img.shape) != 4: return False

        N = np_4d_img.shape[-1]
        in_filenames = []
        out_filenames = []
        for i in range(N):
            np_3d_img_1min = np_4d_img[:, :, :, i]
            nib_3d_img_1min = nib.Nifti1Image(np_3d_img_1min, affine=affine)
            nib.save(nib_3d_img_1min, os.path.join(dyn_4d_mc_nii_root, dyn4d_nii_filename + '_{:04d}.nii.gz'.format(i)))
            in_filenames.append(dyn4d_nii_filename + '_{:04d}'.format(i))
            out_filenames.append(dyn4d_nii_filename + '_{:04d}'.format(i)+ext)
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
def apply_mni_tx_4d_mc_nifti(series_root, dyn4d_nii_filename, mni_txlist, ref_img, ext='_mni_nlin_sysm_09c_1mm'):
    """
    """
    # decompose 4d nifti file
    dyn_4d_niifile = os.path.join(series_root, dyn4d_nii_filename + '.nii.gz')
    dyn_4d_mni_niifile = os.path.join(series_root, dyn4d_nii_filename + ext + '.nii.gz')
    if os.path.exists(dyn_4d_mni_niifile): return True
    dyn_4d_mni_nii_root = os.path.join(series_root, dyn4d_nii_filename)
    if os.path.exists(dyn_4d_mni_nii_root): shutil.rmtree(dyn_4d_mni_nii_root)
    if not os.path.exists(dyn_4d_mni_nii_root):
        os.makedirs(dyn_4d_mni_nii_root, exist_ok=True)
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
            nib.save(nib_3d_img_1min, os.path.join(dyn_4d_mni_nii_root, dyn4d_nii_filename + '_{:04d}.nii.gz'.format(i)))
            in_filenames.append(dyn4d_nii_filename + '_{:04d}'.format(i))
            out_filenames.append(dyn4d_nii_filename + '_{:04d}'.format(i) + ext)
        np_4d_img = None
        nib_4d_img = None

    # apply transform
    for in_filename, out_filename in zip(in_filenames, out_filenames):
        moving = ants.image_read(os.path.join(dyn_4d_mni_nii_root, in_filename + '.nii.gz'))
        warpedimage = ants.apply_transforms(fixed=ref_img, moving=moving, transformlist=mni_txlist)
        ants.image_write(warpedimage, os.path.join(os.path.join(dyn_4d_mni_nii_root, out_filename + '.nii.gz')))

    # collect mc nii files
    nib_imgs = [nib.load(os.path.join(dyn_4d_mni_nii_root, out_filename + '.nii.gz')) for out_filename in out_filenames]
    nib_4d_img_mc = nib.concat_images(nib_imgs)
    np_4d_img_mc = nib_4d_img_mc.get_fdata()
    np_4d_img_mc_new = np_4d_img_mc.astype(dtype)
    nib_4d_img_mc_new = nib.Nifti1Image(np_4d_img_mc_new, affine=nib_4d_img_mc.affine)
    nib.save(nib_4d_img_mc_new, dyn_4d_mni_niifile)

    # remove temp files
    if os.path.exists(dyn_4d_mni_nii_root): shutil.rmtree(dyn_4d_mni_nii_root)
    return True

#--------------------------------------------------------------------------------------------------------
#
def deform_reg_3d_nifti_groups(series_root, ref_file, in_filenames, out_filenames):
    """
    :param series_root:
    :param ref_file:
    :param in_filenames:
    :param out_filenames:
    :return:
    """
    if not os.path.exists(ref_file): return False
    fi = ants.image_read(ref_file)
    fi_mask = ants.get_mask(fi, low_thresh=None, high_thresh=None)
    fi = ants.mask_image(fi, fi_mask)
    for in_filename, out_filename in zip(in_filenames, out_filenames):
        print('working on %s - %s'%(series_root, in_filename))
        in_file = os.path.join(series_root, in_filename + '.nii.gz')
        out_file = os.path.join(series_root, out_filename)
        out_nii_file = out_file + '.nii.gz'
        if not os.path.exists(in_file): continue
        mv = ants.image_read(in_file)
        mx = ants.registration(fixed=fi, moving=mv, type_of_transform='QuickSyN')
        mv_rigid = mx['warpedmovout']
        ants.image_write(mv_rigid, out_nii_file)
    return