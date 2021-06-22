from cleanwatch.interface import Interface, components

for comp in components:
    comp.update()
Interface().cmdloop()
print("Done")
