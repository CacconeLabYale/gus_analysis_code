# ginland.py is part of the 'gus_analysis_code' package.
# It was written by Gus Dunn and was created on 8/10/15.
#
# Please see the license info in the root folder of this package.

"""
Purpose: provide logic to support the running of the `gINLAnd` R package.

=================================================
ginland.py
=================================================
"""
__author__ = 'Gus Dunn'

from collections import defaultdict

from misc import nested_defaultdict

import pandas as pd

import vcf

import pybioclim as pbc


def generate_ginland_inputs(vcf_path, bioclim_dir, bioclims, sample_locations, ginland_dir, site_members=None):
    """Generate the 4 input files needed for running the `gINLAnd` R package.

    For more information about the input file types see: http://www2.imm.dtu.dk/~gigu/gINLAnd/gINLAnd_doc.html

    Args:
        vcf_path (str): path to VCF file to convert.
        bioclim_dir (str): path directory where the bioclim data is stored.
        bioclims (list): list of names of bioclims to include.
        sample_locations (str): path to csv table file with 3 columns ["sample_loc_id","lat", "long"].
            GPS should be in degree-decimal notation.
        ginland_dir (str): path to directory to place generated input files.
        site_members (Optional[dict]): `dict` containing individuals' ID codes as `key` and group name as `value`.
            If value is `None`, attempts to figure out groups by VCF individuals' IDs.

    Returns:
        None
    """

    # OUT Paths
    allele_count_path = ginland_dir + "/allele_count"
    sample_sizes_path = ginland_dir + "/sample_sizes"
    site_coords_path = ginland_dir + "/site_coords"
    environmental_data_path = ginland_dir + "/environmental_data"

    # Generate allele_count and sample_sizes dataframes
    allele_count, sample_sizes = vcf_to_allele_count_and_sample_sizes(vcf_path=vcf_path, site_members=site_members)

    # Learn which sample geolocations are in the VCF
    geo_sites = allele_count.index.values
    geo_sites

    # Generate coords_and_bioclim dataframe
    pbc.DATA_DIR = bioclim_dir  # explicitly set the pbc.DATA_DIR (don't just use the data packaged in pbc)
    coords_and_bioclim = pd.DataFrame.from_csv(sample_locations)
    coords_and_bioclim = add_bioclims_to_df(df=coords_and_bioclim, clim_list=bioclims)

    # Generate site_coords and environmental_data dataframes
    site_coords, environmental_data = generate_site_coords_and_env_data(coords_and_bioclim=coords_and_bioclim,
                                                                        geo_sites=geo_sites)

    # write out generated input data to files in the `ginland_dir` directory as CSV.
    allele_count.to_csv(allele_count_path + ".csv")
    sample_sizes.to_csv(sample_sizes_path + ".csv")
    site_coords.to_csv(site_coords_path + ".csv")
    environmental_data.to_csv(environmental_data_path + ".csv")


def vcf_to_allele_count_and_sample_sizes(vcf_path, site_members=None):
    """Generate dataframes with per-locus allele_count and sample_sizes gINLAnd data.

    Args:
        vcf_path (str): Path to source VCF
        site_members (Optional[dict]): `dict` containing individuals' ID codes as `key` and group name as `value`.
            If value is `None`, attempts to figure out groups by VCF individuals' IDs.

    Returns:
        allele_count (pandas.DataFrame)
        sample_sizes (pandas.DataFrame)

    """
    allele_count_dict = nested_defaultdict()
    sample_sizes_dict = nested_defaultdict()
    if site_members is None:
        site_members = map_site_members_to_site_code_from_vcf(vcf_path=vcf_path)
    site_codes = tuple(set(site_members.values()))
    vcf_reader = vcf.Reader(open(vcf_path, 'r'))

    for snp_rec in vcf_reader:
        chrom_pos = init_nested_dicts_for_locus(allele_count_dict, sample_sizes_dict, snp_rec, site_codes)

        for sample in snp_rec.samples:
            sample_name = sample.sample
            sample_site = site_members[sample_name]

            try:
                allele_count_dict[chrom_pos][sample_site] += sum_hap_gt(sample=sample)
                sample_sizes_dict[chrom_pos][sample_site] += 2
            except TypeError:
                pass

    allele_count = pd.DataFrame(data=allele_count_dict).sort(axis=0).sort(axis=1)
    sample_sizes = pd.DataFrame(data=sample_sizes_dict).sort(axis=0).sort(axis=1)

    return allele_count, sample_sizes


def map_site_members_to_site_code_from_vcf(vcf_path):
    """maps site members to site codes.

    Args:
        vcf_path (str): Path to source VCF

    Returns:
        site_members (dict): `dict` containing individuals' ID codes as `key` and group name as `value`

    """

    vcf_reader = vcf.Reader(open(vcf_path, 'r'))

    site_members = defaultdict(str)

    for sample in vcf_reader.samples:
        site_members[sample] = sample[:2]

    return site_members


def init_nested_dicts_for_locus(allele_count_dict, sample_sizes_dict, snp_rec, site_codes):
    """One line summary.

    More information can be multi-lines

    Args:
        xxx (yyy): zzz.

    Returns:
        None
    """
    chrom_pos = "{chrom}:{pos}".format(chrom=snp_rec.CHROM, pos=snp_rec.POS)
    for site in site_codes:
        allele_count_dict[chrom_pos][site] = 0
        sample_sizes_dict[chrom_pos][site] = 0
    return chrom_pos


def sum_hap_gt(sample):
    """One line summary.

    More information can be multi-lines

    Args:
        xxx (yyy): zzz.

    Returns:
        None
    """
    gt = sample.data.GT
    assert '/' in gt

    hap_gts = [int(hap) for hap in gt.split('/')]
    assert set(hap_gts).issubset(set([0, 1]))

    return sum(hap_gts)


def generate_site_coords_and_env_data(coords_and_bioclim, geo_sites):
    """One line summary.

    More information can be multi-lines

    Args:
        xxx (yyy): zzz.

    Returns:
        None
    """

    # filter for sites we actually have
    geo_site_mask = coords_and_bioclim.code.apply(lambda row: row in geo_sites)
    coords_and_bioclim_filtered = coords_and_bioclim[geo_site_mask]

    site_coords = coords_and_bioclim_filtered[["lat", "long"]].set_index(coords_and_bioclim_filtered.code.values)
    environmental_data = coords_and_bioclim_filtered[
        [x for x in coords_and_bioclim_filtered.columns if x.startswith('bio')]].set_index(
        coords_and_bioclim_filtered.code.values)

    return site_coords.sort(axis=0), environmental_data.sort(axis=0).sort(axis=1)


def add_bioclims_to_df(df, clim_list):
    """Adds bioclims listed in `clim_list` to `df`.

    Args:
        df (pandas.DataFrame): zzz.
        clim_list (list): zzz.

    Returns:
        df (pandas.DataFrame)
    """
    for clim in clim_list:
        df[clim] = pbc.get_values(clim, df[['lat', 'long']].as_matrix())
    return df
