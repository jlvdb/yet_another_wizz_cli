import filecmp
import subprocess

from numpy.random import default_rng
from yaw import UniformRandoms

from yaw_cli import commandline


class Args:
    verbose = True
    threads = None
    progress = False
    config_from = None
    cache_path = None

    def __init__(self, wdir, setup):
        self.wdir = wdir
        self.setup = setup


def test_dump_config():
    subprocess.check_call(["yaw_cli", "run", "--dump"])


def test_run_setup(tmp_path):
    run_path = tmp_path / "run"

    # create the random generators
    gen = UniformRandoms(-5, 5, -5, 5, seed=12345)
    gen_np = default_rng(12345)

    # generate redshifts
    z = gen_np.uniform(0.01, 1.0, size=20_000)
    # generate the catalog data and store them
    for i in (1, 2):
        path = str(tmp_path / f"data{i}.pqt")
        gen.generate(10_000, draw_from=dict(z=z)).to_parquet(path)
        path = str(tmp_path / f"rand{i}.pqt")
        gen.generate(10_000, draw_from=dict(z=z)).to_parquet(path)

    # build and run setup
    args = Args(str(run_path), str(tmp_path / "config.yaml"))
    write_conffile(args.setup, tmp_path)
    commandline.subcommands.CommandRun.run(args)

    # check the results and compare to previously recorded values
    check_path = tmp_path / "nz_cc_1.dat"
    write_expected_result(str(check_path))
    result_path = run_path / "estimate" / "kpc100t1000" / "tag" / "nz_cc_1.dat"
    assert filecmp.cmp(str(result_path), str(check_path))


# below are functions that generate files on the fly


def write_expected_result(write_to):
    content = """# n(z) estimate with symmetric 68% percentile confidence
# extra info: w_sp / sqrt(dz^2)
#    z_low     z_high         nz     nz_err
 0.0100000  0.0483921 -0.0714874  0.2412837
 0.0483921  0.0875150 -0.1702502  0.7736657
 0.0875150  0.1274242  0.4444239  1.0861802
 0.1274242  0.1681784  0.0179567  1.6201554
 0.1681784  0.2098402  1.4058437  1.4778325
 0.2098402  0.2524754 -1.7601214  1.8089520
 0.2524754  0.2961534  1.7782632  1.2683275
 0.2961534  0.3409489 -3.5581369  1.8869132
 0.3409489  0.3869399 -1.2043255  1.9049252
 0.3869399  0.4342099  1.2868055  3.0061225
 0.4342099  0.4828482 -3.5714507  2.5126651
 0.4828482  0.5329485 -1.2246467  2.1515636
 0.5329485  0.5846115  1.1374885  1.4373456
 0.5846115  0.6379443  4.0366565  3.1248831
 0.6379443  0.6930618  2.5069487  2.3406142
 0.6930618  0.7500851 -1.9557623  1.1136452
 0.7500851  0.8091461  1.6633500  2.8553834
 0.8091461  0.8703835  1.8858101  2.5538412
 0.8703835  0.9339479 -0.0073104  1.2230824
 0.9339479  1.0000001  0.2293991  1.3679943
"""
    with open(write_to, "w") as f:
        f.write(content)


def write_conffile(write_to: str, dir: str):
    content = """
# yet_another_wizz setup configuration

# NOTE: (opt) in commment indicates entries that may be omitted.

# This section configures the correlation measurements and redshift
# binning of the clustering redshift estimates.
configuration:
    backend:                # (opt) backend specific parameters
        thread_num: 1           # (opt) default number of threads to use
        crosspatch: true        # (opt) whether to count pairs across patch boundaries (scipy
                                # backend only)
        rbin_slop: 0.01         # (opt) TreeCorr 'rbin_slop' parameter
    binning:                # specify the redshift binning for the clustering redshifts
        method: comoving        # (opt) redshift binning method, 'logspace' means equal size in
                                # log(1+z) (comoving, linear, logspace)
        zmin: 0.01              # lower redshift limit
        zmax: 1.00              # upper redshift limit
        zbin_num: 20            # (opt) number of redshift bins
        zbins: null             # list of custom redshift bin edges, if provided, other binning
                                # parameters are omitted, method is set to 'manual'
    scales:                 # specify the correlation measurement scales
        rmin: 100               # (list of) lower scale limit in kpc (pyhsical)
        rmax: 1000              # (list of) upper scale limit in kpc (pyhsical)
        rweight: null           # (opt) weight galaxy pairs by their separation to power 'rweight'
        rbin_num: 50            # (opt) number of bins in log r used (i.e. resolution) to compute
                                # distance weights
    cosmology: Planck15     # (opt) cosmological model used for distance calculations (Planck13,
                            # Planck15, Planck18, WMAP1, WMAP3, WMAP5, WMAP7, WMAP9)

# This section defines the input data products and their meta data.
# These can be FITS, PARQUET, CSV or FEATHER files.
data:
    backend: scipy          # (opt) name of the data catalog backend (scipy, treecorr)
    cachepath: null         # (opt) cache directory path, e.g. on fast storage device (recommended
                            # for 'backend=scipy', default is within project directory)
    n_patches: 8            # (opt) number of automatic spatial patches to use for input catalogs
                            # below, provide only if no 'data/rand.patches' provided
    reference:              # (opt) reference data sample with know redshifts
        data:                   # data catalog file and column names
            filepath: {dir:}/data1.pqt     # input file path
            ra: ra                  # right ascension in degrees
            dec: dec                # declination in degrees
            redshift: z             # redshift of objects (required)
            patches: null           # (opt) integer index for patch assignment, couting from 0...N-1
            weight: null            # (opt) object weight
            cache: false            # (opt) whether to cache the file in the cache directory
        rand:                   # random catalog for data sample, omit or repeat arguments from
                                # 'data' above
            filepath: {dir:}/rand1.pqt     # input file path
            ra: ra                  # right ascension in degrees
            dec: dec                # declination in degrees
            redshift: z             # redshift of objects (required)
            patches: null           # (opt) integer index for patch assignment, couting from 0...N-1
            weight: null            # (opt) object weight
            cache: false            # (opt) whether to cache the file in the cache directory
    unknown:                # (opt) unknown data sample for which clustering redshifts are
                            # estimated, typically in tomographic redshift bins, see below
        data:                   # data catalog file and column names
            filepath:               # either a single file path (no tomographic bins) or a mapping
                                    # of integer bin index to file path (as shown below)
                1: {dir:}/data2.pqt            # bin 1
            ra: ra                  # right ascension in degrees
            dec: dec                # declination in degrees
            redshift: z             # (opt) redshift of objects, if provided, enables computing the
                                    # autocorrelation of the unknown sample
            patches: null           # (opt) integer index for patch assignment, couting from 0...N-1
            weight: null            # (opt) object weight
            cache: false            # (opt) whether to cache the file in the cache directory
        rand:                   # random catalog for data sample, omit or repeat arguments from
                                # 'data' above ('filepath' format must must match 'data' above)
            filepath:               # either a single file path (no tomographic bins) or a mapping
                                    # of integer bin index to file path (as shown below)
                1: {dir:}/rand2.pqt            # bin 1
            ra: ra                  # right ascension in degrees
            dec: dec                # declination in degrees
            redshift: z             # (opt) redshift of objects, if provided, enables computing the
                                    # autocorrelation of the unknown sample
            patches: null           # (opt) integer index for patch assignment, couting from 0...N-1
            weight: null            # (opt) object weight
            cache: false            # (opt) whether to cache the file in the cache directory

# The section below is entirely optional and used to specify tasks to
# execute when using the 'yaw_cli run' command. The list is generated
# and updated automatically when running 'yaw_cli' subcommands. Tasks
# can be provided as single list entry, e.g.
#   - cross
#   - zcc
# to get a basic cluster redshift estimate or with the optional
# parameters listed below (all values optional, defaults listed).
tasks:
  - cross:                  # compute the crosscorrelation
        rr: True                # compute random-random pair counts if both randoms are available
  - auto_ref:               # compute the reference sample autocorrelation for bias mitigation
        rr: true                # do not compute random-random pair counts
  - auto_unk:               # compute the unknown sample autocorrelation for bias mitigation
        rr: true                # do not compute random-random pair counts
  - ztrue                   # compute true redshift distributions for unknown data (requires point
                            # estimate)
  - drop_cache              # delete temporary data in cache directory, has no arguments
  - zcc:                    # compute clustering redshift estimates for the unknown data, task can
                            # be added repeatedly if different a 'tag' is used
        tag: tag                # unique identifier for different configurations
        bias_ref: false         # whether to mitigate the reference sample bias using its
                                # autocorrelation function (if available)
        bias_unk: false         # whether to mitigate the unknown sample bias using its
                                # autocorrelation functions (if available)
        est_cross: HM           # correlation estimator for crosscorrelations (PH, DP, HM, LS)
        est_auto: null          # correlation estimator for autocorrelations (PH, DP, HM, LS)
        method: jackknife       # resampling method for covariance estimates (jackknife, bootstrap)
        crosspatch: true        # whether to include cross-patch pair counts when resampling
        n_boot: 500             # number of bootstrap samples
        global_norm: false      # normalise pair counts globally instead of patch-wise
        seed: 12345             # random seed for bootstrap sample generation
""".format(
        dir=dir
    )
    with open(write_to, "w") as f:
        f.write(content)
