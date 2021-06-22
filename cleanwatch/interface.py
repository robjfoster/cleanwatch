import cmd

from .budget import * # Terrible practice but will fix later
from .component import get_defaults
from .plotting import cb_plot

# The command line interface for cleanwatch

components = get_defaults()

class Interface(cmd.Cmd):

    intro = "\nCleanwatch. Select an option to continue."
    prompt = "\nPlaceholder for options list.\nChoose option: "

    def __init__(self):
        cmd.Cmd.__init__(self)

    def do_greet(self, args):
        """Print hello"""
        print("Hello")

    def do_exit(self, args):
        return True

    def default(self, args):
        if args == 'q' or args =='x':
            return self.do_exit(args)
        else:
            return

    do_EOF = do_exit

    def emptyline(self):
        return

    def do_print(self, args):
        text = ""
        for comp in components:
            text += comp.output()
        print(text)

    def do_maxbg(self, args):
        while True:
            try:
                signal = float(input("Signal rate: ") or 0.485)
                t3sigma = float(input("Time to detection: ") or 156)
            except ValueError:
                print("Invalid input.\n")
                continue
            break
        mbg = maxbg(signal, t3sigma)
        print(mbg) if mbg > 0 else print("Not possible.")

    def do_budget(self, args):
        while True:
            try:
                signal = float(input("Signal rate per day: ") or 0.485)
                print(f"Signal set to {signal}")
                t3sigma = float(input("Days to detection: ") or 156)
                print(f"Time for 3 sigma set to {t3sigma}")
                method = str(input("Method to use (e/c): ") or "e")
                print(f"Method set to {method}")
            except ValueError:
                print("Invalid input.\n")
                continue
            break
        revcomponents = budget(components, signal, t3sigma, method=method)
        if revcomponents:
            print("\nRevised component activities:")
            for comp in revcomponents:
                comp.revprint()

    def do_bgr(self, args):
        print(total_bgr(components))

    def do_activity(self, args):
        while True:
            try:
                choice = input(f"Choose component to adjust. Choices {[comp.name for comp in components]}: ")
                if not choice: return
                user_comp = components[[comp.name.lower() for comp in components].index(choice.lower())]
            except ValueError:
                print("Invalid input. \n")
                continue
            break
        for iso in user_comp.isotopes.values():
            print(iso.name)
        return

    def do_plot(self, args):
        cb_plot(components, option='c')
