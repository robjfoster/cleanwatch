import matplotlib.pyplot as plt

def cb_plot(components, option: str=None) -> None:
    if option == 'c':
        # Plot contribution breakdown
        names = [comp.name for comp in components]
        while True:
            choice = input(f"Select component to plot. Choices: {names}\nChoice: ")
            if choice.lower() in [name.lower() for name in names]:
                break
            elif choice in ['q', 'x', 'exit']:
                return
        for comp in components:
            if comp.name.lower() == choice.lower():
                user_comp = comp
                break
        data = []
        labels = []
        total = user_comp.total_accidentals * 60 * 60 * 24
        for iso in user_comp.isotopes:
            value = sum(user_comp.accidentals[iso].values()) * 60 * 60 * 24
            data.append(value)
            labels.append(f"{iso}, {value:.2e} per day, {value/total*100:.1f}%")
        plt.pie(data, normalize=True, labels=labels)
        plt.show()
        return