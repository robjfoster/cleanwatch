import cmd

from .budget import *  # Terrible practice but will fix later
from .plotting import cb_plot

# The command line interface for cleanwatch


class Interface(cmd.Cmd):

    intro = "\nCleanwatch. Select an option to continue."
    prompt = "\nPlaceholder for options list.\nChoose option: "

    def __init__(self, components, params):
        cmd.Cmd.__init__(self)
        self.components = components
        self.params = params
        for comp in self.components:
            comp.update(params=self.params)

    def do_greet(self, args):
        """Print hello"""
        print("Hello")

    def do_exit(self, args):
        return True

    def default(self, args):
        if args == 'q' or args == 'x':
            return self.do_exit(args)
        else:
            return

    do_EOF = do_exit

    def emptyline(self):
        return

    def do_print(self, args):
        text = ""
        for comp in self.components:
            text += comp.output()
        print(text)

    def do_maxbg(self, args):
        while True:
            try:
                signal = float(input("Signal rate: ") or self.params.signal)
                t3sigma = float(input("Time to detection: ")
                                or self.params.t3sigma)
            except ValueError:
                print("Invalid input.\n")
                continue
            break
        mbg = maxbg(signal,
                    t3sigma,
                    sigma=self.params.sigma,
                    Ronoff=self.params.Ronoff,
                    RN=self.params.radionuclides,
                    FN=self.params.fastneutrons)
        print(mbg) if mbg > 0 else print("Not possible.")

    def do_budget(self, args):
        while True:
            try:
                signal = float(input("Signal rate per day: ")
                               or self.params.signal)
                print(f"Signal set to {signal}")
                t3sigma = float(input("Days to detection: ")
                                or self.params.t3sigma)
                print(f"Time for 3 sigma set to {t3sigma}")
                method = str(input("Method to use (e/c): ") or "e")
                print(f"Method set to {method}")
            except ValueError:
                print("Invalid input.\n")
                continue
            break
        revcomponents = budget(self.components, signal,
                               t3sigma, self.params, method=method)
        if revcomponents:
            print("\nRevised component activities:")
            for comp in revcomponents:
                comp.revprint()

    def do_bgr(self, args):
        print(total_bgr(self.components))

    def do_activity(self, args):
        while True:
            try:
                choice = input(
                    f"Choose component to adjust. Choices {[comp.name for comp in self.components]}: ")
                if not choice:
                    return
                user_comp = self.components[[
                    comp.name.lower() for comp in self.components].index(choice.lower())]
            except ValueError:
                print("Invalid input. \n")
                continue
            break
        for iso in user_comp.activities:
            print(iso, user_comp.activities[iso], "Bq")
        while True:
            for iso in user_comp.activities:
                try:
                    new_act = float(input(f"Enter new activity for {iso}: "))
                except ValueError:
                    print("Invalid input")
                    continue
                user_comp.activities[iso] = new_act
            break
        return

    def do_plot(self, args):
        cb_plot(self.components, option='c')
