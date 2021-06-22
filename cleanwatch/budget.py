import copy
from typing import Dict, List, Tuple

from .component import Component


def get_total_singles_rate(components: List[Component]) -> float:
    total = 0.
    for comp in components:
        total += comp.total_singles
    return total

def total_accidentals(
        components: List[Component], ds=0.05, dt=0.0001
        ) -> float:
    prompt = 0.
    delayed = 0.
    for comp in components:
        prompt += comp.total_singles
        delayed += comp.del_singles
    total = prompt * delayed * ds * dt
    return total * 60 * 60 * 24

def total_bgr(
        components: List[Component], RN=0.034, FN=0.023, signal=0.485, WRratio=1.15
        ) -> float:
    acc = total_accidentals(components)
    bgr = acc + (WRratio * signal) + FN + RN
    return bgr

def t3sigma(
        signal: float,
        bg: float,
        sigma: float=4.65,
        Ronoff: float=1.5,
        RN: float=0.034,
        FN: float=0.023,
        WRratio: float=1.15
        ) -> float:
    S = signal * 0.9
    WR = WRratio * S
    B = bg + RN + FN + WR
    offtime = sigma**2 * ((B + (B + S) / Ronoff)) * (1 / S**2)
    obstime = offtime * (1 + Ronoff)
    return offtime

def maxbg(
        signal: float,
        t3sigma: float,
        sigma: float=4.65,
        Ronoff: float=1.5,
        RN: float=0.034,
        FN: float=0.023,
        WRratio: float=1.15
        ) -> float:
    # Rearrange t3sigma to solve for max B
    S = signal * 0.9
    WR = WRratio * S
    B = (((t3sigma * S**2) / sigma**2) - (S / Ronoff)) / (1 + (1. / Ronoff))
    maxB = B - FN - RN - WR
    if maxB < 0:
        raise ValueError(f"Cannot detect within {t3sigma} days at signal rate \
                         of {signal} per day. Returning.")
    return maxB

def bg_ratio(
        components: List[Component],
        signal: float,
        t3sigma: float,
        sigma: float=4.65,
        Ronoff: float=1.5,
        RN: float=0.034,
        FN: float=0.023,
        WRratio: float=1.15
        ) -> float:
    mb = maxbg(signal, t3sigma, sigma=sigma, Ronoff=Ronoff, RN=RN, FN=FN, WRratio=WRratio)
    bg = total_bgr(components)
    return bg / mb

def inv_gradients(
        components: List[Component],
        signal: float,
        t3sigma: float
        ) -> Tuple[Dict[str, Dict[str, float]], float]:
    # Need to copy components, adjust activity for a given isotope, calculate 
    # and then return components to original state
    # Do not work on comp or components, only comps_copy
    gradients = {}
    norm = 0
    for idx, comp in enumerate(components):
        comps_copy = copy.deepcopy(components)
        grad = {}
        for iso, iso_obj in comp.isotopes.items():
            comps_copy[idx].activities[iso] = comp.activities[iso] * 0.5
            comps_copy[idx].update(skip_activity=True)
            y1 = bg_ratio(comps_copy, signal, t3sigma)
            comps_copy[idx].activities[iso] = comp.activities[iso] * 1.5
            comps_copy[idx].update(skip_activity=True)
            y2 = bg_ratio(comps_copy, signal, t3sigma)
            if (y2 - y1) == 0:
                grad[iso] = 0
                norm += 0
            else:
                grad[iso] = 1. / (y2 - y1)
                norm += 1. / (y2 - y1)
            comps_copy[idx].activities[iso] = comp.activities[iso]
        gradients[comp.name] = grad
    return gradients, norm

# X = component, a = fractional contribution to total
# AtXt = (a1X1 + a2X2 + a3X3)
# X't = A'Xt = (a'1X1 + a'2X2 + a'3X3)
# A4 = f(a1) + f(a2) + f(a3)
# a'1 = a1(1 - a1)^0.5 A4 / (sum(an(1 - an)^0.5))

def inverse_scale(
    components: List[Component],
    scale_factor: float):
    comp_contribs = {}
    total = total_accidentals(components)
    sum = 0
    sum_scaled = 0
    for idx, comp in enumerate(components):
        comps_copy = copy.deepcopy(components)
        iso_contribs = {}
        for iso, iso_obj in comp.isotopes.items():
            comps_copy[idx].activities[iso] = comp.activities[iso] * 0
            comps_copy[idx].update(skip_activity=True)
            y1 = total_accidentals(comps_copy)
            comps_copy[idx].activities[iso] = comp.activities[iso] * 1
            comps_copy[idx].update(skip_activity=True)
            y2 = total_accidentals(comps_copy)
            iso_contrib = (y2 - y1) / total
            sum += iso_contrib
            iso_contribs[iso] = iso_contrib
            comps_copy[idx].activities[iso] = comp.activities[iso]
        comp_contribs[comp.name] = iso_contribs
    denom = 0.
    for comp in comp_contribs:
        for iso in comp_contribs[comp]:
            orig_contrib = comp_contribs[comp][iso]
            denom += orig_contrib * (1 - orig_contrib)**0.5
            if type(denom) == complex: raise ValueError("inverse_scale: denom is complex")
    comp_scaled_contribs = {}
    for comp in comp_contribs:
        iso_scaled_contribs = {}
        for iso in comp_contribs[comp]:
            orig_contrib = comp_contribs[comp][iso]
            scaled_contrib = (orig_contrib * (1 - orig_contrib)**0.5 * scale_factor) / denom
            sum_scaled += scaled_contrib
            iso_scaled_contribs[iso] = scaled_contrib
        comp_scaled_contribs[comp] = iso_scaled_contribs
    breakpoint()

def budget(
        components: List[Component],
        signal: float,
        t3sigma: float,
        totacc: float=0,
        mbg: float=0,
        method='e',
        update: bool=False
        ) -> List[Component]:
    revcomponents = []
    if not totacc:
        totacc = total_accidentals(components)
    if not mbg:
        try:
            mbg = maxbg(signal, t3sigma)
        except ValueError as e:
            print(e)
            return revcomponents
    if method == 'c':
        grads, norm = inv_gradients(components, signal, t3sigma)
        scales = {compname: {iso: grad/norm for iso, grad in isodict.items()} for compname, isodict in grads.items()}
        for comp in components:
            bg_share = comp.share(mbg, totacc, scales=scales)
            revact = comp.revise_activity(bg_share, mbg/totacc)
            revcomp = Component(comp.name, comp.mass, rate_format=comp.rate_format)
            for iso, act in revact.items():
                revcomp.add_isotope(iso, act) # type: ignore [why does this trigger issue with type hints?]
            revcomp.update()
            revcomponents.append(revcomp)
        return revcomponents
    for comp in components:
        bg_share = comp.share(mbg, totacc)
        revact = comp.revise_activity(bg_share, mbg/totacc)
        revcomp = Component(comp.name, comp.mass, rate_format=comp.rate_format)
        for iso, act in revact.items():
            revcomp.add_isotope(iso, act) # type: ignore why does this trigger issue with type hints?
        revcomp.update()
        revcomponents.append(revcomp)
    return revcomponents
