from __future__ import print_function

from collections import namedtuple


class Component(namedtuple("Component", ("name", "id", "category", "specialization"))):

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other or self.id == other
        else:
            return tuple(self) == tuple(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return super(Component, self).__repr__()

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)

    def is_a(self, term):
        return term == self.name or term in self.specialization


def __generate_list_code():
    '''Prints the code to generate these static lists
    '''
    from psims.controlled_vocabulary.controlled_vocabulary import load_psims

    cv_psims = load_psims()

    def type_path(term):
        path = []
        i = 0
        steps = [term.is_a.comment]
        while i < len(steps):
            step = steps[i]
            i += 1
            path.append(step)
            term = cv_psims[step]
            try:
                steps.append(term.is_a.comment)
            except AttributeError:
                steps.extend(t.comment for t in term.is_a)
            except KeyError:
                continue
        return path

    def render_list(seed, list_name=None):
        component_type_list = [seed]
        i = 0
        if list_name is None:
            list_name = seed.replace(" ", "_") + 's'
        print("%s = [" % (list_name,))
        while i < len(component_type_list):
            component_type = component_type_list[i]
            i += 1
            for term in cv_psims[component_type].children:
                print("    Component(%r, %r, %r, %r), " % (
                    term.name, term.id, component_type_list[0], type_path(term)))
                if term.children:
                    component_type_list.append(term.name)
        print("]")

    render_list('ionization type')
    render_list('detector type')
    render_list('mass analyzer type', 'analyzer_types')
    render_list('inlet type')


ionization_types = [
    Component('multiphoton ionization', 'MS:1000227',
              'ionization type', ['ionization type']),
    Component('fast ion bombardment', 'MS:1000446',
              'ionization type', ['ionization type']),
    Component('resonance enhanced multiphoton ionization',
              'MS:1000276', 'ionization type', ['ionization type']),
    Component('pyrolysis mass spectrometry', 'MS:1000274',
              'ionization type', ['ionization type']),
    Component('neutralization reionization mass spectrometry',
              'MS:1000272', 'ionization type', ['ionization type']),
    Component('photoionization', 'MS:1000273',
              'ionization type', ['ionization type']),
    Component('Negative Ion chemical ionization', 'MS:1000271',
              'ionization type', ['ionization type']),
    Component('chemical ionization', 'MS:1000071',
              'ionization type', ['ionization type']),
    Component('electrospray ionization', 'MS:1000073',
              'ionization type', ['ionization type']),
    Component('fast atom bombardment ionization', 'MS:1000074',
              'ionization type', ['ionization type']),
    Component('flowing afterglow', 'MS:1000255',
              'ionization type', ['ionization type']),
    Component('desorption ionization', 'MS:1000247',
              'ionization type', ['ionization type']),
    Component('atmospheric pressure ionization', 'MS:1000240',
              'ionization type', ['ionization type']),
    Component('spark ionization', 'MS:1000404',
              'ionization type', ['ionization type']),
    Component('thermal ionization', 'MS:1000407',
              'ionization type', ['ionization type']),
    Component('surface ionization', 'MS:1000406',
              'ionization type', ['ionization type']),
    Component('plasma desorption ionization', 'MS:1000400',
              'ionization type', ['ionization type']),
    Component('soft ionization', 'MS:1000403',
              'ionization type', ['ionization type']),
    Component('secondary ionization', 'MS:1000402',
              'ionization type', ['ionization type']),
    Component('vertical ionization', 'MS:1000408',
              'ionization type', ['ionization type']),
    Component('autodetachment', 'MS:1000383',
              'ionization type', ['ionization type']),
    Component('adiabatic ionization', 'MS:1000380',
              'ionization type', ['ionization type']),
    Component('associative ionization', 'MS:1000381',
              'ionization type', ['ionization type']),
    Component('chemi-ionization', 'MS:1000386',
              'ionization type', ['ionization type']),
    Component('autoionization', 'MS:1000384',
              'ionization type', ['ionization type']),
    Component('charge exchange ionization', 'MS:1000385',
              'ionization type', ['ionization type']),
    Component('dissociative ionization', 'MS:1000388',
              'ionization type', ['ionization type']),
    Component('electron ionization', 'MS:1000389',
              'ionization type', ['ionization type']),
    Component('field ionization', 'MS:1000258',
              'ionization type', ['ionization type']),
    Component('glow discharge ionization', 'MS:1000259',
              'ionization type', ['ionization type']),
    Component('liquid secondary ionization', 'MS:1000395',
              'ionization type', ['ionization type']),
    Component('penning ionization', 'MS:1000399',
              'ionization type', ['ionization type']),
    Component('microelectrospray', 'MS:1000397', 'ionization type', [
              'electrospray ionization', 'ionization type']),
    Component('nanoelectrospray', 'MS:1000398', 'ionization type',
              ['electrospray ionization', 'ionization type']),
    Component('matrix-assisted laser desorption ionization', 'MS:1000075',
              'ionization type', ['desorption ionization', 'ionization type']),
    Component('field desorption', 'MS:1000257', 'ionization type',
              ['desorption ionization', 'ionization type']),
    Component('surface-assisted laser desorption ionization', 'MS:1000405',
              'ionization type', ['desorption ionization', 'ionization type']),
    Component('desorption/ionization on silicon', 'MS:1000387',
              'ionization type', ['desorption ionization', 'ionization type']),
    Component('laser desorption ionization', 'MS:1000393', 'ionization type', [
              'desorption ionization', 'ionization type']),
    Component('atmospheric pressure matrix-assisted laser desorption ionization', 'MS:1000239',
              'ionization type', ['atmospheric pressure ionization', 'ionization type']),
    Component('atmospheric pressure chemical ionization', 'MS:1000070',
              'ionization type', ['atmospheric pressure ionization', 'ionization type']),
    Component('desorption electrospray ionization', 'MS:1002011', 'ionization type', [
              'atmospheric pressure ionization', 'ionization type']),
    Component('atmospheric pressure photoionization', 'MS:1000382', 'ionization type', [
              'atmospheric pressure ionization', 'ionization type']),
    Component('surface enhanced laser desorption ionization', 'MS:1000278',
              'ionization type', ['surface ionization', 'ionization type']),
    Component('surface enhanced neat desorption', 'MS:1000279',
              'ionization type', ['surface ionization', 'ionization type']),
]


detector_types = [
    Component('channeltron', 'MS:1000107',
              'detector type', ['detector type']),
    Component('photomultiplier', 'MS:1000116',
              'detector type', ['detector type']),
    Component('multi-collector', 'MS:1000115',
              'detector type', ['detector type']),
    Component('faraday cup', 'MS:1000112',
              'detector type', ['detector type']),
    Component('daly detector', 'MS:1000110',
              'detector type', ['detector type']),
    Component('electron multiplier', 'MS:1000253',
              'detector type', ['detector type']),
    Component('fluorescence detector', 'MS:1002308',
              'detector type', ['detector type']),
    Component('conversion dynode', 'MS:1000346',
              'detector type', ['detector type']),
    Component('dynode', 'MS:1000347', 'detector type', ['detector type']),
    Component('array detector', 'MS:1000345',
              'detector type', ['detector type']),
    Component('focal plane collector', 'MS:1000348',
              'detector type', ['detector type']),
    Component('ion-to-photon detector', 'MS:1000349',
              'detector type', ['detector type']),
    Component('postacceleration detector', 'MS:1000351',
              'detector type', ['detector type']),
    Component('point collector', 'MS:1000350',
              'detector type', ['detector type']),
    Component('inductive detector', 'MS:1000624',
              'detector type', ['detector type']),
    Component('electron multiplier tube', 'MS:1000111',
              'detector type', ['electron multiplier', 'detector type']),
    Component('Acquity UPLC FLR', 'MS:1000819',
              'detector type', 'fluorescence detector'),
    Component('conversion dynode electron multiplier', 'MS:1000108',
              'detector type', ['conversion dynode', 'detector type']),
    Component('conversion dynode photomultiplier', 'MS:1000109',
              'detector type', ['conversion dynode', 'detector type']),
    Component('microchannel plate detector', 'MS:1000114',
              'detector type', ['array detector', 'detector type']),
    Component('photodiode array detector', 'MS:1000621',
              'detector type', ['array detector', 'detector type']),
    Component('focal plane array', 'MS:1000113', 'detector type',
              ['focal plane collector', 'detector type']),
    Component('Acquity UPLC PDA', 'MS:1000818',
              'detector type', 'photodiode array detector'),
]


analyzer_types = [
    Component('cyclotron', 'MS:1000288',
              'mass analyzer type', ['mass analyzer type']),
    Component('orbitrap', 'MS:1000484',
              'mass analyzer type', ['mass analyzer type']),
    Component('ion trap', 'MS:1000264',
              'mass analyzer type', ['mass analyzer type']),
    Component('fourier transform ion cyclotron resonance mass spectrometer',
              'MS:1000079', 'mass analyzer type', ['mass analyzer type']),
    Component('electrostatic energy analyzer', 'MS:1000254',
              'mass analyzer type', ['mass analyzer type']),
    Component('quadrupole', 'MS:1000081',
              'mass analyzer type', ['mass analyzer type']),
    Component('magnetic sector', 'MS:1000080',
              'mass analyzer type', ['mass analyzer type']),
    Component('time-of-flight', 'MS:1000084',
              'mass analyzer type', ['mass analyzer type']),
    Component('stored waveform inverse fourier transform',
              'MS:1000284', 'mass analyzer type', ['mass analyzer type']),
    Component('quadrupole ion trap', 'MS:1000082',
              'mass analyzer type', ['ion trap', 'mass analyzer type']),
    Component('linear ion trap', 'MS:1000291', 'mass analyzer type', [
              'ion trap', 'mass analyzer type']),
    Component('axial ejection linear ion trap', 'MS:1000078', 'mass analyzer type', [
              'linear ion trap', 'ion trap', 'mass analyzer type']),
    Component('radial ejection linear ion trap', 'MS:1000083', 'mass analyzer type', [
              'linear ion trap', 'ion trap', 'mass analyzer type']),
]


inlet_types = [
    Component(u'flow injection analysis', u'MS:1000058',
              u'inlet type', [u'inlet type']),
    Component(u'inductively coupled plasma', u'MS:1000059',
              u'inlet type', [u'inlet type']),
    Component(u'direct inlet', u'MS:1000056', u'inlet type', [u'inlet type']),
    Component(u'electrospray inlet', u'MS:1000057',
              u'inlet type', [u'inlet type']),
    Component(u'continuous flow fast atom bombardment',
              u'MS:1000055', u'inlet type', [u'inlet type']),
    Component(u'reservoir', u'MS:1000067', u'inlet type', [u'inlet type']),
    Component(u'particle beam', u'MS:1000066', u'inlet type', [u'inlet type']),
    Component(u'open split', u'MS:1000065', u'inlet type', [u'inlet type']),
    Component(u'moving wire', u'MS:1000064', u'inlet type', [u'inlet type']),
    Component(u'moving belt', u'MS:1000063', u'inlet type', [u'inlet type']),
    Component(u'membrane separator', u'MS:1000062',
              u'inlet type', [u'inlet type']),
    Component(u'jet separator', u'MS:1000061', u'inlet type', [u'inlet type']),
    Component(u'infusion', u'MS:1000060', u'inlet type', [u'inlet type']),
    Component(u'thermospray inlet', u'MS:1000069',
              u'inlet type', [u'inlet type']),
    Component(u'septum', u'MS:1000068', u'inlet type', [u'inlet type']),
    Component(u'direct liquid introduction', u'MS:1000249',
              u'inlet type', [u'inlet type']),
    Component(u'direct insertion probe', u'MS:1000248',
              u'inlet type', [u'inlet type']),
    Component(u'membrane inlet', u'MS:1000396',
              u'inlet type', [u'inlet type']),
    Component(u'nanospray inlet', u'MS:1000485', u'inlet type',
              [u'electrospray inlet', u'inlet type']),
]


all_components = ionization_types + detector_types + analyzer_types + inlet_types

all_components_by_name = {c.name: c for c in all_components}


def component(name):
    try:
        return all_components_by_name[name]
    except KeyError:
        return Component(name, name, name, [name])
