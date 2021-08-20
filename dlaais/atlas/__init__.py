#--------------------------------------------------------------------------------------------------------
# Project： dlaais.atlas
# Description:
#   atlas files for acute ischemic stroke
# File Name:
#   __init__.py
# Creation Date:
#   2021.08.18
# Modification Date:
#   2021.08.18
#--------------------------------------------------------------------------------------------------------

import os

atlas_root = os.path.dirname(__file__)

atlas_names = ['mni_icbm152_t1_tal_nlin_sym_09c', 
               'mni_icbm152_t2_tal_nlin_sym_09c',
               'mni_icbm152_pd_tal_nlin_sym_09c',
               'mni_icbm152_gm_tal_nlin_sym_09c',
               'mni_icbm152_wm_tal_nlin_sym_09c',
               'mni_icbm152_csf_tal_nlin_sym_09c']

#--------------------------------------------------------------------------------------------------------
#
def get_atlas_nii_file(atlas_name, mni_space='mni_nlin_sysm_09c_1mm'):
    """
    """
    atlas_file = os.path.join(atlas_root, mni_space, atlas_name + '.nii.gz')
    if os.path.exists(atlas_file): return atlas_file
    else: return None