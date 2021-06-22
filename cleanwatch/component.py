import re
from typing import Dict, List

import ROOT as root

from .isotope import isotopes

# Currently, Tl210 values are multiplied by 0.002. Not sure why. Have included
# this in the new version for the moment to match up results but should check
# what the reason for this factor is.

EFF_RFILE = "results.root"

class Component():
    # Container for each area of the detector e.g. PMTs, tank. Handles
    # activity and efficiency calculations.

    def __init__(self, name: str, mass: float, region: str=None,
                 rate_format: str=None):
        self.name = name
        self.region = region
        self.rate_format = rate_format
        self.mass = mass
        self.isotopes = {}
        # Could have all these dicts
        self.activities = {} # Dict of {isotope_obj: activity}
        self.efficiencies = {} # Dict of {isotope_obj: {isotope_str: eff}}
        self.singles = {} # Dict of {isotope_obj: {isotope_str: (prompt, delayed)}}
        self.accidentals = {}
        #or
        #self.isodata = {} # Dict of {iso_name: {'act': act, 'eff': eff, 'rate': rate}}
        # and just write functions to easily access each property
        self.rates = {}

    def add_isotope(self, name: str, rate: float) -> None:
        iso_id = parse_isotope(name)
        isotope = isotopes[iso_id]
        self.isotopes[name] = isotope
        self.rates[name] = rate

    def remove_isotope(self, name: str) -> None:
        del self.isotopes[name]

    def set_rate(self, name: str, rate: float) -> None:
        self.rates[name] = rate

    def update(self, skip_activity=False) -> None:
        if not skip_activity:
            self.calculate_activity()
        self.get_efficiencies(8, 19)
        self.calculate_singles()
        self.calculate_accidentals()

    def calculate_activity(self) -> None:
        # Calculates activities for all isotopes registered with this
        # component. Assumes secular equilibrium for decay chains.
        activities = {}
        for iso, iso_obj in self.isotopes.items():
            rate = self.rates[iso]
            if self.rate_format == 'ppm':
                activity = (self.mass * rate * (1 / 10**6)
                            * iso_obj.activity * iso_obj.NA)
            elif self.rate_format == 'Bq/kg':
                activity = rate * self.mass
            else:
                raise AttributeError(f"Rate format not recognised for {iso} \
                    in {self.name}")
            activities[iso] = activity
        self.activities = activities

    def share(
            self,
            max_bg: float,
            tot_acc: float,
            scales: Dict[str, Dict[str, float]]=None
            ) -> Dict[str, Dict[str, float]]:
        # Update singles to new total background
        shares = {}
        for iso, iso_obj in self.isotopes.items():
            cshares = {}
            if scales is not None:
                scale = scales[self.name][iso]
            else:
                scale = 1
            for ciso, rate in self.singles[iso].items():
                isoshare = rate[0] + (max_bg - tot_acc) / tot_acc * rate[0] * scale
                cshares[ciso] = isoshare
            shares[iso] = cshares
        return shares # updated prompt rate for each isotope in Hz

    def revise_activity(
            self, upd_singles: Dict[str, Dict[str, float]], ratio: float
            ) -> Dict[str, Dict[str, float]]:
        # This function should calculate PPM from activity
        r_rates = {}
        for iso, iso_obj in self.isotopes.items():
            prompt_rates = {key:value[0] for (key, value) in self.singles[iso].items()}
            maxiso = max(prompt_rates, key=prompt_rates.get) #type: ignore
            try:
                if self.rate_format == 'ppm':
                    rev_rate = (upd_singles[iso][maxiso]
                                / self.efficiencies[iso][maxiso][0]
                                / (self.mass * 1e-6 * iso_obj.activity * iso_obj.NA)
                                / ratio**0.5)
                elif self.rate_format == 'Bq/kg':
                    rev_rate = (upd_singles[iso][maxiso]
                                / self.efficiencies[iso][maxiso][0]
                                / self.mass
                                / ratio**0.5)
                else:
                    raise AttributeError(f"Rate format not recognised for {iso} in {self.name}")
            except ZeroDivisionError:
                rev_rate = 0
            r_rates[iso] = rev_rate
            #max([i[0] for i in self.singles[iso].values()])
        return r_rates

    def get_efficiencies(
                        self,
                        prompt_cut: int,
                        delayed_cut: int,
                        fiducial_cut: float =1.9
                        ) -> None:
        efficiencies = {}
        rfile = root.TFile(EFF_RFILE, "READ")
        for iso, iso_obj in self.isotopes.items():
            ceffs = {}
            for ciso in iso_obj.contributors:
                if iso_obj.chain:
                    # Might be able to remove the if statement here, needs testing
                    histname = find_hist(self.name, ciso, parent=iso)
                else:
                    histname = find_hist(self.name, iso)
                if histname:
                    hist = rfile.Get(histname)
                    p_eff = hist.GetBinContent(hist.FindBin(fiducial_cut, prompt_cut))
                    d_eff = hist.GetBinContent(hist.FindBin(fiducial_cut, delayed_cut))
                    if ciso == "210Tl":
                        p_eff *= 0.002
                        d_eff *= 0.002
                    eff = (p_eff, d_eff)
                else:
                    eff = (0., 0.)
                    ceffs[ciso] = eff
                ceffs[ciso] = eff
            efficiencies[iso] = ceffs
        self.efficiencies = efficiencies

    def calculate_singles(self) -> None:
        singles = {}
        tot_singles = 0.
        del_singles = 0.
        for iso, iso_obj in self.isotopes.items():
            csingles = {}
            for ciso in iso_obj.contributors:
                p_rate = self.efficiencies[iso][ciso][0] * self.activities[iso]
                d_rate = self.efficiencies[iso][ciso][1] * self.activities[iso]
                rate = (p_rate, d_rate)
                tot_singles += rate[0]
                del_singles += rate[1]
                csingles[ciso] = rate
            singles[iso] = csingles
        self.total_singles = tot_singles
        self.del_singles = del_singles
        self.singles = singles

    def _singles_rate(self, act, eff):
        rates = {}
        for iso in self.isotopes:
            singles = act[iso] * eff[iso]
            rates[iso] = singles
        return rates

    def calculate_accidentals(
            self, time_cut: float=0.0001, space_cut: float=0.05
            ) -> None:
        accidentals = {}
        tot_acc = 0.
        for iso, iso_obj in self.isotopes.items():
            cacc = {}
            for ciso in iso_obj.contributors:
                acc = (self.singles[iso][ciso][0] * self.singles[iso][ciso][1]
                       * time_cut * space_cut)
                tot_acc += acc
                cacc[ciso] = acc
            accidentals[iso] = cacc
        self.total_accidentals = tot_acc
        self.accidentals = accidentals

    def bg_share(self, total_singles: float) -> float:
        share = self.total_singles / total_singles
        return share

    def revprint(self) -> None:
        """Formatted print revised activities for components"""
        text = "\n"
        text += f"{self.name}:"
        for iso, rate in self.rates.items():
            text += f"\n{iso}: {rate:.4e} {self.rate_format}"
        print(text)

    def output(self):
        text = ""
        text += f"\n********************\nDetails for {self.name}:\n"
        text += "********************\n"
        text += f"\nRegistered isotopes: {list(self.isotopes.keys())}\n"
        text += f"Total prompt singles rate: {self.total_singles:.4e} Hz\n"
        text += "\nBreakdown of isotopes: \n"
        for iso, iso_obj in self.isotopes.items():
            text += f"\n-----------{iso}{' chain' if iso_obj.chain else ''}----------\n"
            text += f"\nActivity of {iso}{' chain' if iso_obj.chain else ''}: {self.activities[iso]:.4e} Bq\n"
            text += f"\n    {'Chain details:' if iso_obj.chain else 'Details:'}\n    ---------\n"
            for ch_iso in self.efficiencies[iso]:
                text += f"    {ch_iso} prompt efficiency: {self.efficiencies[iso][ch_iso][0]:.4e}\n"
            text += "\n"
            for ch_iso in self.singles[iso]:
                text += f"    {ch_iso} prompt singles rate: {self.singles[iso][ch_iso][0]:.4e} Hz\n"
        text += "\n--------------------\n"
        return text

    def __repr__(self):
        return f"{self.name} Component"

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

# For getting names of histograms in results.root, can do:
# for tkey in file.GetListOfKeys(): key = tkey.GetName(); hist = file.Get(key)
def find_hist(location: str, isotope: str, parent=None) -> List[str]:
    file = root.TFile(EFF_RFILE, "READ")
    histkeys = []
    for tkey in file.GetListOfKeys():
        histkeys.append(tkey.GetName())
    matches = [key for key in histkeys if re.search(rf'_{location}_*', key)]
    # May need to remove trailing underscore for RN and FN
    matches = [key for key in matches if re.search(rf'_{isotope}_*', key)]
    if parent:
        matches = [key for key in matches if re.search(rf'_CHAIN_{parent}_NA', key)]
    if len(matches) != 1:
        #print(f"Could not find histogram for {isotope} ({parent}) in {location} in {EFF_RFILE}")
        return []
    else:
        return matches[0]

def parse_isotope(name: str) -> str:
    # Why not have all isotopes as U238 rather than 238U and use this method
    # whenever extracting the efficiency so that internally the naming system
    # is consistent even if it is not consistent with watchmakers.
    # Alternatively, use 238U format internally and only adjust the format
    # when output is presented to the user. This would be more confusing for
    # people adjusting the code though.
    iso_alpha = [char for char in name if char.isalpha()]
    iso_digits = [str(char) for char in name if char.isdigit()]
    iso_alpha = ''.join(iso_alpha)
    iso_digits = ''.join(iso_digits)
    iso_id = iso_alpha + iso_digits
    return iso_id
