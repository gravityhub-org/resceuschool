"""
Minimal two-image millilensing for bilby (effective-distance parameterization).

Standalone extract of Anna Liu's phenomenological millilensing model for a
fixed K=2 image system. Lens parameters:

  D1, D2   effective luminosity distances of images 1 and 2 [Mpc]
  t2       arrival time of image 2 relative to image 1 [s], with t2 > t1 ≡ 0
  n1, n2   Morse factors (0, 0.5, or 1)

The frequency-domain amplification follows Liu et al. (physics convention),
then is conjugated for bilby / LAL engineering Fourier conventions:

  F(f) = conj[ e^{-i n1 π} + (D1/D2) e^{2π i f t2 - i n2 π} ]
"""

from __future__ import annotations

import numpy as np
from bilby.core.prior import Prior
from bilby.gw.source import lal_binary_black_hole


class DiscreteUniformMorse(Prior):
    """Uniform prior over Morse factors {0, 0.5, 1} (types I, II, III)."""

    def __init__(self, name=None, latex_label=None, unit=None):
        super().__init__(
            name=name,
            latex_label=latex_label,
            unit=unit,
            minimum=0.0,
            maximum=2.0,
        )

    def rescale(self, val):
        return np.floor((self.maximum + 1) * val) / 2.0

    def prob(self, val):
        on_grid = (np.modf(2.0 * val)[0] == 0).astype(float)
        in_range = ((val >= 0.0) & (val <= self.maximum / 2.0)).astype(float)
        return in_range * on_grid / float(self.maximum + 1)

    def cdf(self, val):
        return (val <= self.maximum / 2.0) * (np.floor(2.0 * val) + 1) / float(
            self.maximum + 1
        ) + (val > self.maximum / 2.0)


def two_image_amplification(frequency_array, D1, D2, t2, n1, n2):
    """Complex millilensing amplification for two fixed images (t2 > t1 ≡ 0)."""
    frequency_array = np.asarray(frequency_array, dtype=float)
    w = 1j * 2.0 * np.pi * frequency_array # Convert to angular frequency
    f_geo = np.exp(-1j * n1 * np.pi) + (D1 / D2) * np.exp(
        w * t2 - 1j * n2 * np.pi
    )
    return np.conj(f_geo) # Physics convention to engineering convention for bilby / LAL


def binary_black_hole_two_image_millilensing(
    frequency_array,
    mass_1,
    mass_2,
    a_1,
    tilt_1,
    phi_12,
    a_2,
    tilt_2,
    phi_jl,
    theta_jn,
    phase,
    D1,
    D2,
    t2,
    n1,
    n2,
    **kwargs,
):
    """
    Frequency-domain BBH waveform with two millilensed images.

    The unlensed waveform is generated at effective distance ``D1``; image 2
    arrives at ``t2`` (relative to image 1 at ``t1 = 0``) with effective
    distance ``D2`` and Morse factors ``n1``, ``n2``.
    """
    # Bilby may also pass luminosity_distance for source-frame metadata; the
    # millilensing amplitude is set by D1, so drop any duplicate here.
    kwargs.pop("luminosity_distance", None)
    waveform = lal_binary_black_hole(
        frequency_array,
        mass_1=mass_1,
        mass_2=mass_2,
        luminosity_distance=D1,
        a_1=a_1,
        tilt_1=tilt_1,
        phi_12=phi_12,
        a_2=a_2,
        tilt_2=tilt_2,
        phi_jl=phi_jl,
        theta_jn=theta_jn,
        phase=phase,
        **kwargs,
    )
    if waveform is None:
        return None

    amplification = two_image_amplification(
        frequency_array, D1=D1, D2=D2, t2=t2, n1=n1, n2=n2
    )
    return {
        "plus": waveform["plus"] * amplification,
        "cross": waveform["cross"] * amplification,
    }


LENS_PARAMETERS = ("D1", "D2", "t2", "n1", "n2")
