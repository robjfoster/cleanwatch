import math


class Isotope():
    # Class to describe radioactive isotopes and their decay chains (if
    # applicable).

    # Isotopes need consistent naming convention both internally and for display
    # also needs to be consistent for daughter isotopes in decay chains.

    def __init__(self, Z, half_life, NA, chain=None, name=None, branches=None):
        self.Z = Z
        self.half_life = half_life * 365.25 * 24. * 60. * 60.
        self.NA = NA
        self.lifetime = self.calculate_lifetime()
        self.lam = self.calculate_lambda()
        self.activity = self.calculate_activity()
        self.chain = chain
        self.branches = branches
        if not chain:
            self.contributors = [name]
        else:
            self.contributors = chain
        self.name = name

    def __repr__(self):
        return f"Iso ({self.name})"

    def calculate_lifetime(self) -> float:
        return self.half_life / math.log(2)

    def calculate_lambda(self) -> float:
        return math.log(2) / self.half_life

    def calculate_activity(self) -> float:
        return 6.022e23 * self.lam / (self.Z / 1000)


# No alphas
chains = {
    "U238": ['234Pa', '214Pb', '214Bi', '210Bi', '210Tl'],
    "Th232": ['228Ac', '212Pb', '212Bi', '208Tl'],
    "U235": ['231Th', '223Fr', '211Pb', '211Bi', '207Tl'],
    "Rn222": ['214Pb', '214Bi', '210Bi', '210Tl'],
}
# Source periodictable.com
branches = {
    "U238": {'234Pa': 1.0, '214Pb': 1.0, '214Bi': 1.0, '210Bi': 1.0, '210Tl': 0.0021},
    "Th232": {'228Ac': 1.0, '212Pb': 1.0, '212Bi': 0.6405, '208Tl': 0.3594},
    "U235": {'231Th': 1.0, '223Fr': 0.0138, '211Pb': 1.0, '211Bi': 0.00276, '207Tl': 1.34e-9},
    "Rn222": {'214Pb': 1.0, '214Bi': 1.0, '210Bi': 1.0, '210Tl': 0.0021}
}

isotopes = {
    "U238":  Isotope(238, 4.47e9, 0.9928, chain=chains['U238'], branches=branches["U238"], name="U238"),
    "U235":  Isotope(235, 7.04e8, 0.0072, chain=chains['U235'], branches=branches["U235"], name="U235"),
    "Th232": Isotope(232, 1.41e10, 0.9998, chain=chains['Th232'], branches=branches["Th232"], name="Th232"),
    "Rn222": Isotope(222, 3.82/365.25, 1, chain=chains['Rn222'], branches=branches["Rn222"], name="Rn222"),
    "K40":   Isotope(40, 1.28e9, 0.000117, name="K40"),
    "Gd152": Isotope(152, 1.08e14, 0.002, name="Gd152"),
    "Co60":  Isotope(60, 5.27, 1, name="Co60"),
    "Cs137": Isotope(137, 30.17, 1, name="Cs137"),
}
