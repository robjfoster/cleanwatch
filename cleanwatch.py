from typing import List

from cleanwatch.component import Component
from cleanwatch.interface import Interface

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
    return [water, gd, pmt, veto, tank]


components = get_defaults()

interface = Interface(components)
interface.cmdloop()
print("Done")
