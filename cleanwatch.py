from collections import namedtuple
from typing import List

from cleanwatch.component import Component
from cleanwatch.interface import Interface

Params = namedtuple(
    "Params", ("rfile, prompt_cut, delayed_cut, fiducial_cut, IBDtimecut,"
               "IBDspacecut, signal, t3sigma, Ronoff, radionuclides, fastneutrons,"
               "sigma"))

# Edit this to change the default detector components and activity values
# The component name should match with watchmakers


def get_defaults() -> List[Component]:
    water = Component("WaterVolume", mass=6300000, rate_format='Bq/kg')
    water.add_isotope("222Rn", 1e-6)
    #water.add_isotope("238U", 1e-6)
    #water.add_isotope("235U", 4.66e-8)
    #water.add_isotope("232Th", 1e-7)
    #water.add_isotope("40K", 4e-6)
    gd = Component("GD", mass=12600, rate_format='Bq/kg')
    #gd.add_isotope("152Gd", 0.841)
    gd.add_isotope("238U", 4.96e-5)
    gd.add_isotope("235U", 2.31e-6)
    gd.add_isotope("232Th", 2.48e-5)
    #gd.add_isotope("40K", 2e-3)
    pmt = Component("PMT", mass=4580.8, rate_format='ppm')
    pmt.add_isotope("238U", 0.064)
    pmt.add_isotope("232Th", 0.172)
    pmt.add_isotope("40K", 36)
    veto = Component("VETO", mass=458.08, rate_format='ppm')
    veto.add_isotope("238U", 0.341)
    veto.add_isotope("232Th", 1.33)
    veto.add_isotope("40K", 260)
    tank = Component("TANK", mass=257706, rate_format='ppm')
    tank.add_isotope("238U", 9.49e-3)
    #tank.add_isotope("235U", 8.38e-5)
    tank.add_isotope("232Th", 4.19e-3)
    tank.add_isotope("40K", 1.75)
    tank.add_isotope("137Cs", 2.47e-11)
    tank.add_isotope("60Co", 1.79e-12)
    rock = Component("ROCK", mass=0, rate_format='ppm')
    print("Default component activities loaded.")
    params = Params(rfile="results.root",
                    prompt_cut=8,
                    delayed_cut=19,
                    fiducial_cut=1.9,
                    IBDtimecut=0.0001,
                    IBDspacecut=0.05,
                    signal=0.485,
                    t3sigma=156,
                    Ronoff=1.5,
                    radionuclides=0.034,
                    fastneutrons=0.023,
                    sigma=4.65)
    return [water, gd, pmt, veto, tank], params


def get_16m_defaults() -> List[Component]:
    rfile = "results_Watchman_16m_water.root"
    # 16m tank, 5.7m rPMT. From cleanliness log
    water = Component("LIQUID", mass=3209257.833, rate_format='Bq/kg',
                      rfile=rfile)
    water.add_isotope("238U", 1.0e-6)
    water.add_isotope("232Th", 1.0e-7)
    water.add_isotope("40K", 4e-6)
    gd = Component("GD", 6418.52, rate_format='Bq/kg', rfile=rfile)
    gd.add_isotope("238U", 4.96e-5)
    gd.add_isotope("232Th", 2.48e-5)
    gd.add_isotope("235U", 2.31e-6)
    pmt = Component("PMT", mass=2553.6, rate_format='ppm', rfile=rfile)
    pmt.add_isotope("238U", 0.064)
    pmt.add_isotope("232Th", 0.172)
    pmt.add_isotope("40K", 85.5)
    psup = Component("PSUP", mass=33241.06, rate_format='ppm', rfile=rfile)
    psup.add_isotope("238U", 9.49e-3)
    psup.add_isotope("232Th", 4.19e-3)
    psup.add_isotope("40K", 1.75)
    psup.add_isotope("235U", 8.38e-5)
    psup.add_isotope("137Cs", 2.47e-11)
    psup.add_isotope("60Co", 1.79e-12)
    tank = Component("TANK", mass=481322.0, rate_format='ppm', rfile=rfile)
    tank.add_isotope("238U", 9.49e-3)
    tank.add_isotope("232Th", 4.19e-3)
    tank.add_isotope("40K", 1.75)
    tank.add_isotope("235U", 8.38e-5)
    tank.add_isotope("137Cs", 2.47e-11)
    tank.add_isotope("60Co", 1.79e-12)
    ibeam = Component("IBEAM", mass=320652.73, rate_format='ppm', rfile=rfile)
    ibeam.add_isotope("238U", 9.49e-3)
    ibeam.add_isotope("232Th", 4.19e-3)
    ibeam.add_isotope("40K", 1.75)
    ibeam.add_isotope("235U", 8.38e-5)
    ibeam.add_isotope("137Cs", 2.47e-11)
    ibeam.add_isotope("60Co", 1.79e-12)
    print("16m water tank component activities loaded.")
    # These aren't the latest numbers
    params = Params(rfile="results_Watchman_16m_water.root",
                    prompt_cut=8,
                    delayed_cut=19,
                    fiducial_cut=1.9,
                    IBDtimecut=0.0001,
                    IBDspacecut=0.05,
                    signal=0.485,
                    t3sigma=156,
                    Ronoff=1.5,
                    radionuclides=0.034,
                    fastneutrons=0.023,
                    sigma=4.65)
    return [water, gd, pmt, psup, tank, ibeam], params


# Change this function call to change detector design
components, params = get_16m_defaults()

interface = Interface(components, params)
interface.cmdloop()
print("Done")
