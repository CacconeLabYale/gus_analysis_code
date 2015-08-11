# configs.py is part of the 'gus_analysis_code' package.
# It was written by Gus Dunn and was created on 8/10/15.
#
# Please see the license info in the root folder of this package.

"""
Purpose: process different kinds of config files for this package.

=================================================
configs.py
=================================================
"""
__author__ = 'Gus Dunn'

import os

import yaml

import munch


def generate_ginland_inputs(config):
    """Prepare user's config file.

    Also handles validation.

    Args:
        config (str): path to config file.

    Returns:
        conf (dict): configuration values.
    """
    conf = munch.munchify(yaml.load(config))
    conf.meta_data = munch.Munch()
    conf.meta_data.path = os.path.abspath(config.name)

    # # Run all validations that we can do on conf
    # # Can add more later

    return conf
