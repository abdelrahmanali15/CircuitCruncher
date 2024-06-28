import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib import pyplot

class PlotManager:
    def __init__(self, num_subplots: int = 1, title: str = '', xlabel: str = 'X Axis', ylabel: str = 'Y Axis'):
        self.num_subplots = num_subplots
        self.fig, self.axs = plt.subplots(num_subplots, 1, sharex=True)
        self.fig.suptitle(title)
        
        if num_subplots == 1:
            self.axs = [self.axs]  # Ensure self.axs is always a list
        
        for ax in self.axs:
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.grid()
        
        self.plots = [[] for _ in range(num_subplots)]

    def plot(self, xaxis: np.ndarray, yaxis: np.ndarray, label: str, subplot_index: int = 0, linestyle: str = '-'):
        if 0 <= subplot_index < self.num_subplots:
            self.axs[subplot_index].semilogx(xaxis, yaxis, label=label, linestyle=linestyle)
            self.axs[subplot_index].legend()
            self.plots[subplot_index].append((xaxis, yaxis, label))
        else:
            raise IndexError("subplot_index out of range")

    def add_line(self, line_orientation: str = 'horizontal', line_value: float = None, line_label: str = '', line_color: str = 'red', subplot_index: int = 0):
        if 0 <= subplot_index < self.num_subplots:
            ax = self.axs[subplot_index]
            if line_value is not None:
                if line_orientation == 'horizontal':
                    ax.axhline(y=line_value, color=line_color, linestyle='--', label=f'{line_label}={"{:e}".format(abs(line_value))}')
                elif line_orientation == 'vertical':
                    ax.axvline(x=line_value, color=line_color, linestyle='--', label=f'{line_label}={"{:e}".format(abs(line_value))}')
                ax.legend()
        else:
            raise IndexError("subplot_index out of range")

    def add_annotation(self, lookup_value: float, lookup_array: np.ndarray, lookup_return_array: np.ndarray,
                       subplot_index: int = 0, annotation_text: str = None, annotation_color: str = 'red', cursor: str = 'v'):
        if not (0 <= subplot_index < self.num_subplots):
            raise IndexError("subplot_index out of range")

        if lookup_value is None or lookup_array is None or lookup_return_array is None:
            print('None')
            return

        lookup_result = self.lookup(lookup_array, lookup_value, lookup_return_array)

        if annotation_text is None:
            if cursor == 'v':
                annotation_text = f'Intersection: (X={lookup_value}, Y={lookup_result:.2e})'
            elif cursor == 'h':
                annotation_text = f'Intersection: (X={lookup_result:.2e}, Y={lookup_value})'

        if cursor not in ['v', 'h']:
            raise ValueError('Please provide whether the cursor is horizontal "h" or vertical "v"')

        x, y = (lookup_value, lookup_result) if cursor == 'v' else (lookup_result, lookup_value)

        self.axs[subplot_index].annotate(annotation_text, xy=(x, y), xycoords='data',
                                         xytext=(-40, 30), textcoords='offset points',
                                         arrowprops=dict(arrowstyle="->", color=annotation_color))

    @staticmethod
    def lookup(array: np.ndarray, value: float, return_array: np.ndarray) -> float:
        idx = (np.abs(array - value)).argmin()
        return return_array[idx]

    def show(self):
        plt.show()
    
    def save(self, filename: str, format: str = 'png', width: int = 8, height: int = 8):
        self.fig.set_size_inches(width, height)
        self.fig.savefig(filename, format=format, bbox_inches='tight')






        """This module provides helpers to plot Bode diagrams using Matplolib.

Frequency is in Hz, gain in dB, phase in radians between -π and π.
"""

####################################################################################################



####################################################################################################
def bode_diagram_gain(axe, frequency, gain, **kwargs):
    axe.set_xscale('log')
    axe.plot(frequency, gain, **kwargs)
    axe.grid(True)
    axe.grid(True, which='minor')
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Gain [dB]")

####################################################################################################

def bode_diagram_phase(axe, frequency, phase, **kwargs):
    axe.set_xscale('log')
    axe.plot(frequency, phase, **kwargs)
    axe.set_ylim(-math.pi, math.pi)
    axe.grid(True)
    axe.grid(True, which='minor')
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Phase [rads]")
    # axe.set_yticks # Fixme:
    plt.yticks((-math.pi, -math.pi/2,0, math.pi/2, math.pi),
               (r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"))

####################################################################################################

def bode_diagram(axes, frequency, gain, phase, **kwargs):
    bode_diagram_gain(axes[0], frequency, gain, **kwargs)
    bode_diagram_phase(axes[1], frequency, phase, **kwargs)

def plot_bode(frequency, gain_db, phase, bw_3dB,title = 'Bode Plot'):
    def format_value(val):
        if np.isnan(val):
            return "NaN"
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"{val/1e12:.2f}T"
        elif abs_val >= 1e9:
            return f"{val/1e9:.2f}G"
        elif abs_val >= 1e6:
            return f"{val/1e6:.2f}M"
        elif abs_val >= 1e3:
            return f"{val/1e3:.2f}k"
        elif abs_val >= 1:
            return f"{val:.2f}"
        elif abs_val >= 1e-3:
            return f"{val*1e3:.2f}m"
        elif abs_val >= 1e-6:
            return f"{val*1e6:.2f}μ"
        elif abs_val >= 1e-9:
            return f"{val*1e9:.2f}n"
        elif abs_val >= 1e-12:
            return f"{val*1e12:.2f}p"
        elif abs_val >= 1e-15:
            return f"{val*1e15:.2f}f"
        else:
            return f"{val*1e18:.2f}a"
        

    figure, axes = plt.subplots(2, figsize=(10, 10))
    figure.suptitle(title)
    bode_diagram(axes=axes,
                 frequency=frequency,
                 gain=gain_db,
                 phase=phase,
                 marker='.',
                 color='blue',
                 linestyle='-',
    )
    for ax in axes:
        ax.axvline(x=bw_3dB, color='red')
        ax.annotate(f'{format_value(bw_3dB)}Hz', xy=(bw_3dB, 0), xytext=(5, 10),
                    textcoords='offset points', arrowprops=dict(arrowstyle='->', color='red'))

    plt.tight_layout
    plt.show()
