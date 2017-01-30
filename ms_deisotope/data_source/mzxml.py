import numpy as np
from pyteomics import mzxml
from .common import (
    PrecursorInformation, ScanIterator, ScanDataSource, ChargeNotProvided,
    ScanBunch, ActivationInformation)
from weakref import WeakValueDictionary
from lxml.etree import XMLSyntaxError


def _yield_from_index(self, start=None):
    offset_provider = self._offset_index.offsets
    keys = offset_provider.keys()
    if start is not None:
        if isinstance(start, basestring):
            start = keys.index(start)
        elif isinstance(start, int):
            start = start
        else:
            raise TypeError("Cannot start from object %r" % start)
    else:
        start = 0
    for key in keys[start:]:
        scan = self.get_by_id(key, "num")
        yield scan


class MzXMLDataInterface(ScanDataSource):
    """Provides implementations of all of the methods needed to implement the
    :class:`ScanDataSource` for mzXML files. Not intended for direct instantiation.
    """
    def _scan_arrays(self, scan):
        try:
            return scan['m/z array'], scan["intensity array"]
        except KeyError:
            return np.array([]), np.array([])

    def _precursor_information(self, scan):
        pinfo_dict = scan['precursorMz'][0]
        precursor_scan_id = pinfo_dict['precursorScanNum']
        pinfo = PrecursorInformation(
            mz=float(pinfo_dict['precursorMz']),
            intensity=float(pinfo_dict.get('precursorIntensity', 0.0)),
            charge=int(pinfo_dict.get('precursorCharge')) if pinfo_dict.get('precursorCharge') else ChargeNotProvided,
            precursor_scan_id=precursor_scan_id,
            source=self,
            product_scan_id=self._scan_id(scan))
        return pinfo

    def _scan_title(self, scan):
        return self._scan_id(scan)

    def _scan_id(self, scan):
        return scan["num"]

    def _scan_index(self, scan):
        try:
            if self._scan_index_lookup is None:
                raise ValueError("Index Not Built")
            scan_index = self._scan_index_lookup[self._scan_id(scan)]
            return scan_index
        except KeyError:
            return -1
        except ValueError:
            return -1

    def _ms_level(self, scan):
        return int(scan['msLevel'])

    def _scan_time(self, scan):
        try:
            return scan['retentionTime']
        except KeyError:
            return None

    def _is_profile(self, scan):
        return not bool(int(scan['centroided']))

    def _polarity(self, scan):
        if scan['polarity'] == '+':
            return 1
        else:
            return -1

    def _activation(self, scan):
        try:
            return ActivationInformation(
                scan['precursorMz'][0]['activationMethod'], scan['collisionEnergy'])
        except KeyError:
            return None


class MzXMLLoader(MzXMLDataInterface, ScanIterator):
    """Reads scans from mzXML files. Provides both iterative and
    random access.

    Attributes
    ----------
    source_file: str
        Path to file to read from.
    source: pyteomics.mzxml.MzXML
        Underlying scan data source
    """
    __data_interface__ = MzXMLDataInterface

    def __init__(self, source_file, use_index=True):
        self.source_file = source_file
        self._source = mzxml.MzXML(source_file, read_schema=True, iterative=True, use_index=use_index)
        self._producer = self._scan_group_iterator()
        self._scan_cache = WeakValueDictionary()
        self._use_index = use_index
        self._scan_index_lookup = None
        if self._use_index:
            self._build_scan_index_lookup()

    def __reduce__(self):
        return MzXMLLoader, (self.source_file, self._use_index)

    def _build_scan_index_lookup(self):
        if not self._use_index:
            raise ValueError("Must index the entire file before sequential indices may computed.")
        index = dict()
        i = 0
        for scan, offset in self.index.items():
            index[scan] = i
            i += 1
        self._scan_index_lookup = index

    @property
    def index(self):
        return self._source._offset_index

    @property
    def source(self):
        return self._source

    def close(self):
        self._source.close()

    def reset(self):
        self._make_iterator(None)
        self._scan_cache = WeakValueDictionary()
        self._source.reset()

    def _make_iterator(self, iterator=None):
        self._producer = self._scan_group_iterator(iterator)

    def _validate(self, scan):
        return "m/z array" in scan._data

    def _scan_group_iterator(self, iterator=None):
        if iterator is None:
            iterator = iter(self._source)
        precursor_scan = None
        product_scans = []

        current_level = 1

        _make_scan = self._make_scan

        for scan in iterator:
            packed = _make_scan(scan)
            if not self._validate(packed):
                continue
            self._scan_cache[packed.id] = packed
            if packed.ms_level == 2:
                if current_level < 2:
                    current_level = 2
                product_scans.append(packed)
            elif packed.ms_level == 1:
                if current_level > 1:
                    precursor_scan.product_scans = list(product_scans)
                    yield ScanBunch(precursor_scan, product_scans)
                else:
                    if precursor_scan is not None:
                        precursor_scan.product_scans = list(product_scans)
                        yield ScanBunch(precursor_scan, product_scans)
                precursor_scan = packed
                product_scans = []
            else:
                raise Exception("This object is not able to handle MS levels higher than 2")
        if precursor_scan is not None:
            yield ScanBunch(precursor_scan, product_scans)

    def next(self):
        try:
            return self._producer.next()
        except XMLSyntaxError:
            raise StopIteration(
                "This iterator may need to be reset by calling `reset` to continue using it after"
                " using a random-access function like `get_by_id`")

    def __next__(self):
        return self.next()

    def get_scan_by_id(self, scan_id):
        """Retrieve the scan object for the specified scan id. If the
        scan object is still bound and in memory somewhere, a reference
        to that same object will be returned. Otherwise, a new object will
        be created.

        Parameters
        ----------
        scan_id : str
            The unique scan id value to be retrieved

        Returns
        -------
        Scan
        """
        try:
            return self._scan_cache[scan_id]
        except KeyError:
            packed = self._make_scan(self._source.get_by_id(scan_id, id_key='num'))
            self._scan_cache[packed.id] = packed
            return packed

    def get_scan_by_time(self, time):
        scan_ids = tuple(self.index)
        lo = 0
        hi = len(scan_ids)
        while hi != lo:
            mid = (hi + lo) / 2
            sid = scan_ids[mid]
            scan = self.get_scan_by_id(sid)
            if not self._validate(scan):
                sid = scan_ids[mid - 1]
                scan = self.get_scan_by_id(sid)

            scan_time = scan.scan_time
            if scan_time == time:
                return scan
            elif (hi - lo) == 1:
                return scan
            elif scan_time > time:
                hi = mid
            else:
                lo = mid
        if hi == 0 and not self._use_index:
            raise TypeError("This method requires the index. Please pass `use_index=True` during initialization")

    def get_scan_by_index(self, index):
        if not self._use_index:
            raise TypeError("This method requires the index. Please pass `use_index=True` during initialization")
        return self.get_scan_by_id(tuple(self.index)[index])

    def _locate_ms1_scan(self, scan):
        while scan.ms_level != 1:
            if scan.index <= 0:
                raise IndexError("Cannot search backwards with a scan index <= 0 (%r)" % scan.index)
            scan = self.get_scan_by_index(scan.index - 1)
        return scan

    def start_from_scan(self, scan_id=None, rt=None, index=None, require_ms1=True):
        if scan_id is None:
            if rt is not None:
                scan = self.get_scan_by_time(rt)
            elif index is not None:
                scan = self.get_scan_by_index(index)
            else:
                raise ValueError("Must provide a scan locator, one of (scan_id, rt, index)")

            scan_id = scan.id
        else:
            scan = self.get_scan_by_id(scan_id)

        # We must start at an MS1 scan, so backtrack until we reach one
        if require_ms1:
            scan = self._locate_ms1_scan(scan)
            scan_id = scan.id

        iterator = _yield_from_index(self._source, scan_id)
        self._make_iterator(iterator)
        return self