# This file is used to configure the behavior of pytest when using the Astropy
# test infrastructure. It needs to live inside the package in order for it to
# get picked up when running the tests inside an interpreter using
# packagename.test

import warnings

import numpy as np
import pytest
from astropy import units as u
from astropy import coordinates as coord
from astropy.io import fits
from astropy.modeling import models
from astropy.nddata import CCDData, StdDevUncertainty
from astropy.wcs import WCS
from specutils import Spectrum1D, SpectrumCollection, SpectrumList
from gwcs import coordinate_frames as cf, wcs as gwcs_wcs

from jdaviz import __version__, Cubeviz, Imviz, Mosviz, Specviz, Specviz2d

SPECTRUM_SIZE = 10  # length of spectrum


@pytest.fixture
def cubeviz_helper():
    return Cubeviz()


@pytest.fixture
def imviz_helper():
    return Imviz()


@pytest.fixture
def mosviz_helper():
    return Mosviz()


@pytest.fixture
def specviz_helper():
    return Specviz()


@pytest.fixture
def specviz2d_helper():
    return Specviz2d()


@pytest.fixture
def image_2d_wcs():
    return WCS({'CTYPE1': 'RA---TAN', 'CUNIT1': 'deg', 'CDELT1': -0.0002777777778,
                'CRPIX1': 1, 'CRVAL1': 337.5202808,
                'CTYPE2': 'DEC--TAN', 'CUNIT2': 'deg', 'CDELT2': 0.0002777777778,
                'CRPIX2': 1, 'CRVAL2': -20.833333059999998})


@pytest.fixture
def spectral_cube_wcs():
    # A simple spectral cube WCS used by some tests
    wcs = WCS(naxis=3)
    wcs.wcs.ctype = 'FREQ', 'DEC--TAN', 'RA---TAN'
    wcs.wcs.set()
    return wcs


@pytest.fixture
def image_cube_hdu_obj():
    flux_hdu = fits.ImageHDU(np.ones((10, 10, 10)))
    flux_hdu.name = 'FLUX'

    mask_hdu = fits.ImageHDU(np.zeros((10, 10, 10)))
    mask_hdu.name = 'MASK'

    uncert_hdu = fits.ImageHDU(np.ones((10, 10, 10)))
    uncert_hdu.name = 'ERR'

    wcs = {
        'WCSAXES': 3, 'CRPIX1': 38.0, 'CRPIX2': 38.0, 'CRPIX3': 1.0,
        'PC1_1 ': -0.000138889, 'PC2_2 ': 0.000138889,
        'PC3_3 ': 8.33903304339E-11, 'CDELT1': 1.0, 'CDELT2': 1.0,
        'CDELT3': 1.0, 'CUNIT1': 'deg', 'CUNIT2': 'deg', 'CUNIT3': 'm',
        'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN', 'CTYPE3': 'WAVE-LOG',
        'CRVAL1': 205.4384, 'CRVAL2': 27.004754, 'CRVAL3': 3.62159598486E-07,
        'LONPOLE': 180.0, 'LATPOLE': 27.004754, 'MJDREFI': 0.0,
        'MJDREFF': 0.0, 'DATE-OBS': '2014-03-30',
        'RADESYS': 'FK5', 'EQUINOX': 2000.0
    }

    flux_hdu.header.update(wcs)
    flux_hdu.header['BUNIT'] = '1E-17 erg*s^-1*cm^-2*Angstrom^-1'

    uncert_hdu.header['BUNIT'] = '1E-17 erg*s^-1*cm^-2*Angstrom^-1'

    return fits.HDUList([fits.PrimaryHDU(), flux_hdu, uncert_hdu, mask_hdu])


@pytest.fixture
def image_cube_hdu_obj_microns():
    flux_hdu = fits.ImageHDU(np.ones((8, 9, 10)).astype(np.float32))
    flux_hdu.name = 'FLUX'

    uncert_hdu = fits.ImageHDU(np.zeros((8, 9, 10)).astype(np.float32))
    uncert_hdu.name = 'ERR'

    mask_hdu = fits.ImageHDU(np.ones((8, 9, 10)).astype(np.uint16))
    mask_hdu.name = 'MASK'

    wcs = {
        'WCSAXES': 3, 'CRPIX1': 38.0, 'CRPIX2': 38.0, 'CRPIX3': 1.0,
        'CRVAL1': 205.4384, 'CRVAL2': 27.004754, 'CRVAL3': 4.890499866509344,
        'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN', 'CTYPE3': 'WAVE',
        'CUNIT1': 'deg', 'CUNIT2': 'deg', 'CUNIT3': 'um',
        'CDELT1': 3.61111097865634E-05, 'CDELT2': 3.61111097865634E-05, 'CDELT3': 0.001000000047497451,  # noqa
        'PC1_1 ': -1.0, 'PC1_2 ': 0.0, 'PC1_3 ': 0,
        'PC2_1 ': 0.0, 'PC2_2 ': 1.0, 'PC2_3 ': 0,
        'PC3_1 ': 0, 'PC3_2 ': 0, 'PC3_3 ': 1,
        'DISPAXIS': 2, 'VELOSYS': -2538.02,
        'SPECSYS': 'BARYCENT', 'RADESYS': 'ICRS', 'EQUINOX': 2000.0,
        'LONPOLE': 180.0, 'LATPOLE': 27.004754,
        'MJDREFI': 0.0, 'MJDREFF': 0.0, 'DATE-OBS': '2014-03-30'}

    flux_hdu.header.update(wcs)
    flux_hdu.header['BUNIT'] = '1E-17 erg*s^-1*cm^-2*Angstrom^-1'

    uncert_hdu.header['BUNIT'] = '1E-17 erg*s^-1*cm^-2*Angstrom^-1'

    return fits.HDUList([fits.PrimaryHDU(), flux_hdu, uncert_hdu, mask_hdu])


@pytest.fixture
def spectrum1d_cube_wcs():
    # A simple spectrum1D WCS used by some tests
    wcs = WCS(naxis=3)
    wcs.wcs.ctype = 'WAVE-LOG', 'DEC--TAN', 'RA---TAN'
    wcs.wcs.set()
    return wcs


@pytest.fixture
def spectrum1d():
    np.random.seed(42)

    spec_axis = np.linspace(6000, 8000, SPECTRUM_SIZE) * u.AA
    flux = (np.random.randn(len(spec_axis.value)) +
            10*np.exp(-0.001*(spec_axis.value-6563)**2) +
            spec_axis.value/500) * u.Jy
    uncertainty = StdDevUncertainty(np.abs(np.random.randn(len(spec_axis.value))) * u.Jy)

    meta = dict(header=dict(FILENAME="jdaviz-test-file.fits"))

    return Spectrum1D(spectral_axis=spec_axis, flux=flux, uncertainty=uncertainty, meta=meta)


@pytest.fixture
def spectrum_collection(spectrum1d):
    sc = [spectrum1d] * 5

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        result = SpectrumCollection.from_spectra(sc)
    return result


@pytest.fixture
def multi_order_spectrum_list(spectrum1d, spectral_orders=10):
    sc = []
    np.random.seed(42)

    for i in range(spectral_orders):

        spec_axis = (np.arange(SPECTRUM_SIZE) + 6000 + i * SPECTRUM_SIZE) * u.AA
        flux = (np.random.randn(len(spec_axis.value)) +
                10 * np.exp(-0.002 * (spec_axis.value - 6563) ** 2) +
                spec_axis.value / 500) * u.Jy
        uncertainty = StdDevUncertainty(np.abs(np.random.randn(len(spec_axis.value))) * u.Jy)
        meta = dict(header=dict(FILENAME="jdaviz-test-multi-order-file.fits"))
        spectrum1d = Spectrum1D(spectral_axis=spec_axis, flux=flux,
                                uncertainty=uncertainty, meta=meta)

        sc.append(spectrum1d)

    return SpectrumList(sc)


def _create_spectrum1d_cube_with_fluxunit(fluxunit=u.Jy, shape=(2, 2, 4)):

    flux = np.arange(np.prod(shape)).reshape(shape) * fluxunit
    wcs_dict = {"CTYPE1": "RA---TAN", "CTYPE2": "DEC--TAN", "CTYPE3": "WAVE-LOG",
                "CRVAL1": 205, "CRVAL2": 27, "CRVAL3": 4.622e-7,
                "CDELT1": -0.0001, "CDELT2": 0.0001, "CDELT3": 8e-11,
                "CRPIX1": 0, "CRPIX2": 0, "CRPIX3": 0}
    w = WCS(wcs_dict)

    return Spectrum1D(flux=flux, wcs=w)


@pytest.fixture
def spectrum1d_cube():
    return _create_spectrum1d_cube_with_fluxunit(fluxunit=u.Jy)


@pytest.fixture
def spectrum1d_cube_larger():
    return _create_spectrum1d_cube_with_fluxunit(fluxunit=u.Jy, shape=(SPECTRUM_SIZE, 2, 4))


@pytest.fixture
def spectrum1d_cube_custom_fluxunit():
    return _create_spectrum1d_cube_with_fluxunit


@pytest.fixture
def mos_spectrum1d():
    '''
    A specially defined Spectrum1d that matches the corresponding spectrum2d below.

    TODO: this fixture should be replaced by the global spectrum1d fixture defined in
    jdaviz/conftest.py AFTER reforming the spectrum2d fixture below to match the
    global spectrum1d fixture.

    Unless linking the two is required, try to use the global spectrum1d fixture.
    '''
    spec_axis = np.linspace(6000, 8000, 1024) * u.AA
    np.random.seed(42)
    flux = (np.random.randn(len(spec_axis.value)) +
            10*np.exp(-0.001*(spec_axis.value-6563)**2) +
            spec_axis.value/500) * u.Jy

    return Spectrum1D(spectral_axis=spec_axis, flux=flux)


@pytest.fixture
def spectrum2d():
    '''
    A simple 2D Spectrum1D with a center "trace" array rising from 0 to 10
    with two "zero array" buffers above and below
    '''
    data = np.zeros((5, 10))
    data[3] = np.arange(10)

    return Spectrum1D(flux=data*u.MJy, spectral_axis=data[3]*u.um)


@pytest.fixture
def mos_spectrum2d():
    '''
    A specially defined 2D (spatial) Spectrum1D whose wavelength range matches the
    mos-specific 1D spectrum.

    TODO: This should be reformed to match the global Spectrum1D defined above so that we may
    deprecate the mos-specific spectrum1d.
    '''
    header = {
        'WCSAXES': 2,
        'CRPIX1': 0.0, 'CRPIX2': 1024.5,
        'CDELT1': 1E-06, 'CDELT2': 2.9256727777778E-05,
        'CUNIT1': 'm', 'CUNIT2': 'deg',
        'CTYPE1': 'WAVE', 'CTYPE2': 'OFFSET',
        'CRVAL1': 0.0, 'CRVAL2': 5.0,
        'RADESYS': 'ICRS', 'SPECSYS': 'BARYCENT'}
    wcs = WCS(header)
    np.random.seed(42)
    data = np.random.sample((1024, 15)) * u.one
    return Spectrum1D(data, wcs=wcs, meta=header)


@pytest.fixture
def mos_image():
    header = {
        'WCSAXES': 2,
        'CRPIX1': 937.0, 'CRPIX2': 696.0,
        'CDELT1': -1.5182221158397e-05, 'CDELT2': 1.5182221158397e-05,
        'CUNIT1': 'deg', 'CUNIT2': 'deg',
        'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN',
        'CRVAL1': 5.0155198140981, 'CRVAL2': 5.002450989248,
        'LONPOLE': 180.0, 'LATPOLE': 5.002450989248,
        'DATEREF': '1858-11-17', 'MJDREFI': 0.0, 'MJDREFF': 0.0,
        'RADESYS': 'ICRS'}
    wcs = WCS(header)
    np.random.seed(42)
    data = np.random.sample((55, 55))
    return CCDData(data, wcs=wcs, unit='Jy', meta=header)


def create_example_gwcs(shape):
    # Example adapted from photutils:
    #   https://github.com/astropy/photutils/blob/
    #   2825356f1d876cacefb3a03d104a4c563065375f/photutils/datasets/make.py#L821
    rho = np.pi / 3.0
    # Roman plate scale:
    scale = (0.11 * u.arcsec / u.pixel).to_value(u.deg / u.pixel)

    shift_by_crpix = (models.Shift((-shape[1] / 2) + 1)
                      & models.Shift((-shape[0] / 2) + 1))

    cd_matrix = np.array([[-scale * np.cos(rho), scale * np.sin(rho)],
                          [scale * np.sin(rho), scale * np.cos(rho)]])

    rotation = models.AffineTransformation2D(cd_matrix, translation=[0, 0])
    rotation.inverse = models.AffineTransformation2D(
        np.linalg.inv(cd_matrix), translation=[0, 0])

    tan = models.Pix2Sky_TAN()
    celestial_rotation = models.RotateNative2Celestial(197.8925, -1.36555556,
                                                       180.0)

    det2sky = shift_by_crpix | rotation | tan | celestial_rotation
    det2sky.name = 'linear_transform'

    detector_frame = cf.Frame2D(name='detector', axes_names=('x', 'y'),
                                unit=(u.pix, u.pix))

    sky_frame = cf.CelestialFrame(reference_frame=coord.ICRS(),
                                  name='icrs', unit=(u.deg, u.deg))

    pipeline = [(detector_frame, det2sky), (sky_frame, None)]

    return gwcs_wcs.WCS(pipeline)


# this filtered warning can be removed after resolution of PR:
# https://github.com/spacetelescope/roman_datamodels/pull/138
@pytest.mark.filterwarnings(
    'ignore:erfa.core.ErfaWarning: ERFA function "d2dtf" yielded 1 of "dubious year (Note 5)"'
)
def create_wfi_image_model(image_shape, **kwargs):
    """
    Create a dummy Roman WFI Image datamodel instance with valid values
    for attributes required by the schema.

    Requires roman_datamodels >= 0.14.2.dev

    Adapted from:
        https://github.com/spacetelescope/roman_datamodels/blob/
        932afed416e02bf0e684973f03548eeefe973b9e/src/roman_datamodels/testing/factories.py#L1224

    Parameters
    ----------
    image_shape : tuple
        Shape of the synthetic image to produce

    **kwargs
        Additional or overridden attributes.
    Returns
    -------
    roman_datamodels.datamodel.ImageModel
    """
    from roman_datamodels import datamodels as rdd, stnode
    from roman_datamodels.random_utils import (
        generate_array_float32, generate_array_uint32, generate_array_uint16
    )
    from roman_datamodels.testing.factories import (
        create_meta, create_cal_logs, create_photometry
    )
    count_rate_lims = dict(min=0, max=1e4)
    raw = {
        "data": generate_array_float32(
            image_shape, units=u.electron / u.s, **count_rate_lims
        ),
        "dq": generate_array_uint32(image_shape),
        "err": generate_array_float32(
            image_shape, units=u.electron / u.s, **count_rate_lims
        ),
        "meta": create_meta(),
        "var_flat": generate_array_float32(
            image_shape, units=u.electron**2 / u.s**2, **count_rate_lims
        ),
        "var_poisson": generate_array_float32(
            image_shape, units=u.electron**2 / u.s**2, **count_rate_lims
        ),
        "var_rnoise": generate_array_float32(
            image_shape, units=u.electron**2 / u.s**2, **count_rate_lims
        ),
        "amp33": generate_array_uint16((2, image_shape[0] + 8, 128), units=u.DN),
        "border_ref_pix_right": generate_array_float32(
            (2, image_shape[0] + 8, 4), units=u.DN, **count_rate_lims
        ),
        "border_ref_pix_left": generate_array_float32(
            (2, image_shape[0] + 8, 4), units=u.DN, **count_rate_lims
        ),
        "border_ref_pix_top": generate_array_float32(
            (2, 4, image_shape[1] + 8), units=u.DN, **count_rate_lims
        ),
        "border_ref_pix_bottom": generate_array_float32(
            (2, 4, image_shape[1] + 8), units=u.DN, **count_rate_lims
        ),
        "dq_border_ref_pix_right": generate_array_uint32((image_shape[0] + 8, 4)),
        "dq_border_ref_pix_left": generate_array_uint32((image_shape[0] + 8, 4)),
        "dq_border_ref_pix_top": generate_array_uint32((4, image_shape[1] + 8)),
        "dq_border_ref_pix_bottom": generate_array_uint32((4, image_shape[1] + 8)),
        "cal_logs": create_cal_logs(),
    }
    raw.update(kwargs)
    raw["meta"]["photometry"] = create_photometry()
    raw["meta"]["wcs"] = create_example_gwcs(image_shape)
    return rdd.ImageModel(stnode.WfiImage(raw))


# this filtered warning can be removed after resolution of PR:
# https://github.com/spacetelescope/roman_datamodels/pull/138
@pytest.mark.filterwarnings(
    'ignore:erfa.core.ErfaWarning: ERFA function "d2dtf" yielded 1 of "dubious year (Note 5)"'
)
@pytest.fixture
def roman_wfi_image(image_shape=(20, 20)):
    # Combining synthetic WFI data generators from roman_datamodels
    # with the syntax for constructing a ImageModel:
    #    https://github.com/spacetelescope/romancal/blob/
    #    1908ae5c3f11704246d8aea1f71f637be44fc46b/docs/roman/datamodels/models.rst?plain=1#L48
    image_model = create_wfi_image_model(image_shape)
    return image_model


try:
    from pytest_astropy_header.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS
except ImportError:
    PYTEST_HEADER_MODULES = {}
    TESTED_VERSIONS = {}


def pytest_configure(config):
    PYTEST_HEADER_MODULES['astropy'] = 'astropy'
    PYTEST_HEADER_MODULES['pyyaml'] = 'yaml'
    PYTEST_HEADER_MODULES['scikit-image'] = 'skimage'
    PYTEST_HEADER_MODULES['specutils'] = 'specutils'
    PYTEST_HEADER_MODULES['specreduce'] = 'specreduce'
    PYTEST_HEADER_MODULES['asteval'] = 'asteval'
    PYTEST_HEADER_MODULES['echo'] = 'echo'
    PYTEST_HEADER_MODULES['idna'] = 'idna'
    PYTEST_HEADER_MODULES['traitlets'] = 'traitlets'
    PYTEST_HEADER_MODULES['bqplot'] = 'bqplot'
    PYTEST_HEADER_MODULES['bqplot-image-gl'] = 'bqplot_image_gl'
    PYTEST_HEADER_MODULES['glue-core'] = 'glue'
    PYTEST_HEADER_MODULES['glue-jupyter'] = 'glue_jupyter'
    PYTEST_HEADER_MODULES['glue-astronomy'] = 'glue_astronomy'
    PYTEST_HEADER_MODULES['ipyvue'] = 'ipyvue'
    PYTEST_HEADER_MODULES['ipyvuetify'] = 'ipyvuetify'
    PYTEST_HEADER_MODULES['ipysplitpanes'] = 'ipysplitpanes'
    PYTEST_HEADER_MODULES['ipygoldenlayout'] = 'ipygoldenlayout'
    PYTEST_HEADER_MODULES['voila'] = 'voila'
    PYTEST_HEADER_MODULES['vispy'] = 'vispy'
    PYTEST_HEADER_MODULES['gwcs'] = 'gwcs'
    PYTEST_HEADER_MODULES['asdf'] = 'asdf'
    PYTEST_HEADER_MODULES['stdatamodels'] = 'stdatamodels'
    PYTEST_HEADER_MODULES['roman_datamodels'] = 'roman_datamodels'

    TESTED_VERSIONS['jdaviz'] = __version__
