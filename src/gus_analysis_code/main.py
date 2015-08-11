# main.py is part of the 'gus_analysis_code' package.
# It was written by Gus Dunn and was created on 8/10/15.
#
# Please see the license info in the root folder of this package.

"""
Purpose: provide main entry point to this package's scripts.

=================================================
main.py
=================================================
"""
__author__ = 'Gus Dunn'
import os

import click
from click import echo

import munch

import configs
import ginland


@click.group()
@click.pass_context
def cli(ctx):
    """Command line interface to `gus_analysis_code`.

    For command specific help text, call the specific
    command followed by the --help option.
    """

    ctx.obj = munch.Munch()


@cli.command()
@click.option('--config',
              help="Path to optional config.yaml. Providing additional options will override config values.",
              type=click.File(),
              show_default=True)
@click.option('--vcf-path',
              help="Path to VCF file to convert.",
              type=click.File())
@click.option('--bioclim-dir',
              help="Path directory where the bioclim data is stored.",
              type=click.Path(exists=True))
@click.option('--bioclims',
              help="List of names of bioclims to include: comma-separated string. ",
              show_default=True,
              type=str)
@click.option('--sample-locations',
              help="Path to csv table file with 3 columns ['sample_loc_id','lat','long'].",
              type=click.File())
@click.option('--ginland-dir',
              help="Path to directory to place generated input files, will be created if it does not exist.",
              type=click.Path(exists=False))
@click.option('--site-members',
              help="Path to csv file containing individuals' ID codes as  column named `key` and group/geo-location "
                   "name as column named`value`. If value is not provided, I will attempt to figure out groups by VCF "
                   "individuals' IDs.",
              type=click.Path(),
              show_default=True)
@click.pass_context
def generate_ginland_inputs(ctx, config, vcf_path, bioclim_dir, bioclims, sample_locations, ginland_dir,
                            site_members):
    """Generates the 4 input files needed for running the `gINLAnd` R package.

    For more information about the input file types see: http://www2.imm.dtu.dk/~gigu/gINLAnd/gINLAnd_doc.html

    """

    opts = munch.Munch(dict(vcf_path=vcf_path,
                            bioclim_dir=bioclim_dir,
                            bioclims=bioclims,
                            sample_locations=sample_locations,
                            ginland_dir=ginland_dir,
                            site_members=site_members)
                       )

    if config:
        ctx.obj.CONFIG = configs.generate_ginland_inputs(config=config)

        # override CONFIG value if provided at the commandline.
        for opt, val in opts.items():
            if val is not None:
                ctx.obj.CONFIG[opt] = val
    else:
        ctx.obj.CONFIG = opts

    c = ctx.obj.CONFIG

    if not os.path.exists(c.ginland_dir):
        echo("generate_ginland_inputs: Creating directory: {out}.".format(out=c.ginland_dir))
        os.makedirs(c.ginland_dir)

    ginland.generate_ginland_inputs(vcf_path=c.vcf_path,
                                    bioclim_dir=c.bioclim_dir,
                                    bioclims=c.bioclims,
                                    sample_locations=c.sample_locations,
                                    ginland_dir=c.ginland_dir,
                                    site_members=c.site_members)


if __name__ == '__main__':
    cli(obj={})
