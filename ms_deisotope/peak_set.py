import operator
from collections import namedtuple

from .utils import Base, ppm_error
from brainpy import mass_charge_ratio


class _Index(object):
    """
    Stores the ordered index of an object under sort by `mz` and
    sort by `neutral_mass`

    Attributes
    ----------
    mz : int
        Index of this object (or its parent), ordered by mz
    neutral_mass : int
        Index of this object (or its parent), ordered by neutral mass
    """

    __slots__ = ["neutral_mass", "mz"]

    def __init__(self, neutral_mass=None, mz=None):
        self.neutral_mass = neutral_mass
        self.mz = mz

    def __reduce__(self):
        return self.__class__, (self.neutral_mass, self.mz)

    def __repr__(self):
        return "%d|%d" % (self.neutral_mass, self.mz)

    def clone(self):
        return self.__class__(self.neutral_mass, self.mz)


EnvelopePair = namedtuple("EnvelopePair", ("mz", "intensity"))


class Envelope(object):
    """
    Represents a sequence of (mz, intensity) pairs which store peak positions
    that were matched. Since these peaks may later be mutated by subtraction,
    this structure stores copies of the numbers

    Supports the Sequence protocol, and is read-only.

    Attributes
    ----------
    pairs : tuple of tuple of (float, float)
        list of (mz, intensity) pairs
    """
    __slots__ = ['pairs']

    def __init__(self, pairs):
        self.pairs = [EnvelopePair(*x) for x in pairs]

    def __reduce__(self):
        return self.__class__, (self.pairs,)

    def __getitem__(self, i):
        return self.pairs[i]

    def __iter__(self):
        return iter(self.pairs)

    def __repr__(self):
        return "[%s]" % (', '.join("(%0.4f, %0.2f)" % t for t in self),)

    def clone(self):
        return self.__class__(self)


class DeconvolutedPeak(Base):
    """
    Represent a single deconvoluted peak which represents an aggregated isotopic
    pattern collapsed to its monoisotopic peak, with a known charge state

    Attributes
    ----------
    a_to_a2_ratio : float
        Ratio of intensities of A peak to A+2 peak
    average_mass : float
        The averaged neutral mass of the composition, the weighted average
        of the envelope peaks.
    charge : int
        The signed charge state of the isotopic pattern
    envelope : Envelope
        The sequence of (mz, intensity) pairs which map to this peak
    full_width_at_half_max : float
        The averaged full width at half max of this isotopic pattern
    index : _Index
        The position of this peak in different orderings
    intensity : float
        The summed height of the peaks in the isotopic pattern this peak captures
    most_abundant_mass : float
        The neutral mass of the most abundant peak in the isotopic pattern this peak captures
    mz : float
        The mass-charge-ratio of the monoisotopic peak
    neutral_mass : float
        The neutral mass of the monoisotopic peak
    score : float
        An assigned value describing the quality of this peak's fit. The semantics of this score
        depends upon the scoring function
    signal_to_noise : float
        The average signal-to-noise ratio of the peaks in the isotopic pattern this peak captures
    """
    __slots__ = [
        "neutral_mass", "intensity", "signal_to_noise",
        "index", "full_width_at_half_max", "charge",
        "a_to_a2_ratio", "most_abundant_mass", "average_mass",
        "score", "envelope", "mz", "fit", "chosen_for_msms", 'area'
    ]

    def __init__(self, neutral_mass, intensity, charge, signal_to_noise, index, full_width_at_half_max,
                 a_to_a2_ratio=None, most_abundant_mass=None, average_mass=None, score=None,
                 envelope=None, mz=None, fit=None, chosen_for_msms=False, area=0):
        if index is None:
            index = _Index()
        self.neutral_mass = neutral_mass
        self.intensity = intensity
        self.signal_to_noise = signal_to_noise
        self.index = index
        self.full_width_at_half_max = full_width_at_half_max
        self.charge = charge
        self.a_to_a2_ratio = a_to_a2_ratio
        self.most_abundant_mass = most_abundant_mass
        self.average_mass = average_mass
        self.score = score
        self.envelope = Envelope(envelope)
        self.mz = mz or mass_charge_ratio(self.neutral_mass, self.charge)
        self.fit = fit
        self.chosen_for_msms = chosen_for_msms
        self.area = area

    def __eq__(self, other):
        return (abs(self.neutral_mass - other.neutral_mass) < 1e-5) and (
            abs(self.intensity - other.intensity) < 1e-5)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.mz, self.intensity, self.charge))

    def clone(self):
        return DeconvolutedPeak(self.neutral_mass, self.intensity, self.charge, self.signal_to_noise,
                                self.index, self.full_width_at_half_max, self.a_to_a2_ratio,
                                self.most_abundant_mass, self.average_mass, self.score,
                                self.envelope, self.mz, self.fit, self.chosen_for_msms,
                                self.area)

    def __reduce__(self):
        return DeconvolutedPeak, (self.neutral_mass, self.intensity, self.charge, self.signal_to_noise,
                                  self.index, self.full_width_at_half_max, self.a_to_a2_ratio,
                                  self.most_abundant_mass, self.average_mass, self.score,
                                  self.envelope, self.mz, self.fit, self.chosen_for_msms, self.area)


class DeconvolutedPeakSolution(DeconvolutedPeak):
    """
    Extends :class:`DeconvolutedPeak` to also include a reference to
    the :class:`IsotopicFitRecord` instance it is derived from, and optionally an
    object which the fit derives from.

    Attributes
    ----------
    fit : IsotpicFitRecord
        The isotopic pattern fit used to construct this peak
    solution : object
        Representation of the "source" of the isotopic fit
    """
    __slots__ = [
        "solution", "fit",
        "neutral_mass", "intensity", "signal_to_noise",
        "index", "full_width_at_half_max", "charge",
        "a_to_a2_ratio", "most_abundant_mass", "average_mass",
        "score", "envelope", "mz", "chosen_for_msms", 'area'
    ]

    def __init__(self, solution, fit, *args, **kwargs):
        self.solution = solution
        self.fit = fit
        super(DeconvolutedPeakSolution, self).__init__(*args, **kwargs)

    def clone(self):
        return DeconvolutedPeakSolution(
            self.solution, self.fit, self.neutral_mass, self.intensity, self.charge, self.signal_to_noise,
            self.index, self.full_width_at_half_max, self.a_to_a2_ratio,
            self.most_abundant_mass, self.average_mass, self.score,
            self.envelope, self.mz, self.chosen_for_msms, self.area)

    def __reduce__(self):
        return DeconvolutedPeakSolution, (
            self.solution, self.fit, self.neutral_mass, self.intensity, self.charge, self.signal_to_noise,
            self.index, self.full_width_at_half_max, self.a_to_a2_ratio,
            self.most_abundant_mass, self.average_mass, self.score,
            self.envelope, self.mz, self.chosen_for_msms, self.area)

    def __iter__(self):
        yield self.solution
        yield self
        yield self.fit


class DeconvolutedPeakSet(Base):
    """
    Represents a collection of :class:`DeconvolutedPeak` instances under multiple orderings.

    Attributes
    ----------
    peaks : tuple of DeconvolutedPeak
        Collection of peaks ordered by `neutral_mass`
    _mz_ordered: tuple of DeconvolutedPeak
        Collection of peaks ordered by `mz`
    """
    def __init__(self, peaks):
        self.peaks = peaks
        self._mz_ordered = None

    def reindex(self):
        """
        Updates the :attr:`index` of each peak in `self` and updates the
        sorted order.

        Returns
        -------
        self: DeconvolutedPeakSet
        """
        self._reindex()

    def _reindex(self):
        """
        Updates the :attr:`index` of each peak in `self` and updates the
        sorted order.

        Returns
        -------
        self: DeconvolutedPeakSet
        """
        self.peaks = tuple(sorted(self.peaks, key=operator.attrgetter("neutral_mass")))
        self._mz_ordered = tuple(sorted(self.peaks, key=operator.attrgetter("mz")))
        for i, peak in enumerate(self.peaks):
            peak.index = _Index()
            peak.index.neutral_mass = i
        for i, peak in enumerate(self._mz_ordered):
            peak.index.mz = i
        return self

    def __len__(self):
        return len(self.peaks)

    def get_nearest_peak(self, neutral_mass, use_mz=False):
        if use_mz:
            return _get_nearest_peak(self._mz_ordered, neutral_mass, use_mz=use_mz)
        else:
            return _get_nearest_peak(self.peaks, neutral_mass, use_mz=use_mz)

    def has_peak(self, neutral_mass, tolerance=1e-5, use_mz=False):
        if use_mz:
            return binary_search(self._mz_ordered, neutral_mass, tolerance, mz_getter)
        return binary_search(self.peaks, neutral_mass, tolerance, neutral_mass_getter)

    def all_peaks_for(self, neutral_mass, tolerance=1e-5):
        lo = neutral_mass - neutral_mass * tolerance
        hi = neutral_mass + neutral_mass * tolerance
        lo_peak, lo_err = self.get_nearest_peak(lo)
        hi_peak, hi_err = self.get_nearest_peak(hi)
        lo_ix = lo_peak.index.neutral_mass
        if abs(ppm_error(lo_peak.neutral_mass, neutral_mass)) > tolerance:
            lo_ix += 1
        hi_ix = hi_peak.index.neutral_mass + 1
        if abs(ppm_error(hi_peak.neutral_mass, neutral_mass)) > tolerance:
            hi_ix -= 1
        return self[lo_ix:hi_ix]

    def __repr__(self):
        return "<DeconvolutedPeakSet %d Peaks>" % (len(self))

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(tuple(p.clone() for p in self.peaks[item]))
        return self.peaks[item]

    def __iter__(self):
        return iter(self.peaks)

    def clone(self):
        return self.__class__(tuple(p.clone() for p in self))

    def between(self, m1, m2, tolerance=1e-5, use_mz=False):
        acc = []
        collecting = False
        if not use_mz:
            getter = operator.attrgetter("neutral_mass")
            iterator = self.peaks
        else:
            getter = operator.attrgetter("mz")
            iterator = self._mz_ordered
        for peak in iterator:
            if not collecting and getter(peak) >= m1:
                collecting = True
            elif collecting and getter(peak) > m2:
                break

            if collecting:
                acc.append(peak.clone())

        return self.__class__(acc)._reindex()


mz_getter = operator.attrgetter('mz')
neutral_mass_getter = operator.attrgetter("neutral_mass")


def _get_nearest_peak(peaklist, neutral_mass, use_mz=False):
    lo = 0
    hi = len(peaklist)

    tol = 1

    getter = operator.attrgetter("mz") if use_mz else operator.attrgetter("neutral_mass")

    def sweep(lo, hi):
        best_error = float('inf')
        best_index = None
        for i in range(hi - lo):
            i += lo
            v = getter(peaklist[i])
            err = abs(v - neutral_mass)
            if err < best_error:
                best_error = err
                best_index = i
        return peaklist[best_index], best_error

    def binsearch(lo, hi):
        if (hi - lo) < 5:
            return sweep(lo, hi)
        else:
            mid = (hi + lo) // 2
            v = getter(peaklist[mid])
            if abs(v - neutral_mass) < tol:
                return sweep(lo, hi)
            elif v > neutral_mass:
                return binsearch(lo, mid)
            else:
                return binsearch(mid, hi)
    return binsearch(lo, hi)


def _sweep_solution(array, value, mid, tolerance, getter=operator.attrgetter('neutral_mass')):

    best_index = mid
    best_error = float('inf')
    n = len(array)

    i = 0
    while mid - i >= 0 and i <= mid:
        target = array[mid - i]
        abs_error = abs(ppm_error(value, getter(target)))
        if abs_error < tolerance:
            if abs_error < best_error:
                best_index = mid - i
                best_error = abs_error
        else:
            break
        i += 1
    i = 1
    while (mid + i) < (n - 1):
        target = array[mid + i]
        abs_error = abs(ppm_error(value, getter(target)))
        if abs_error < tolerance:
            if abs_error < best_error:
                best_index = mid + i
                best_error = abs_error
        else:
            break
        i += 1
    if best_error == float('inf'):
        return None
    else:
        return array[best_index]


def binary_search(peak_set, neutral_mass, tolerance, getter=operator.attrgetter('neutral_mass')):

    lo = 0
    hi = len(peak_set)

    while hi != lo:
        mid = (hi + lo) // 2
        found_peak = peak_set[mid]
        found_mass = getter(found_peak)

        if abs(ppm_error(found_mass, neutral_mass)) < tolerance:
            found_peak = _sweep_solution(peak_set, neutral_mass, mid, tolerance)
            return found_peak
        elif hi - lo == 1:
            return None
        elif found_mass > neutral_mass:
            hi = mid
        else:
            lo = mid


try:
    has_c = True
    _Envelope = Envelope
    __Index = _Index
    _DeconvolutedPeak = DeconvolutedPeak
    _DeconvolutedPeakSolution = DeconvolutedPeakSolution
    _DeconvolutedPeakSet = DeconvolutedPeakSet

    from ms_deisotope._c.peak_set import (
        Envelope, _Index, DeconvolutedPeak, DeconvolutedPeakSolution,
        DeconvolutedPeakSetIndexed as DeconvolutedPeakSet
        # DeconvolutedPeakSet
    )

except ImportError:
    has_c = False
