import numpy as np
import matplotlib.pyplot as plt
import math


class PlotManager:
    def __init__(self, num_subplots: int = 1, title: str = '', xlabel: str = 'X Axis', ylabels: list = None, **kwargs):
        self.num_subplots = num_subplots
        self.fig, self.axs = plt.subplots(num_subplots, 1, sharex=True)
        self.fig.suptitle(title)
        self.x_scale = kwargs.get('x_scale', 'linear')
        self.y_scale = kwargs.get('y_scale', 'linear')

        if num_subplots == 1:
            self.axs = [self.axs]

        if ylabels is None:
            ylabels = ['Y Axis'] * num_subplots
        elif len(ylabels) != num_subplots:
            raise ValueError("The length of ylabels must match num_subplots")

        for ax, ylabel in zip(self.axs, ylabels):
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.grid()
            ax.set_xscale(self.x_scale)
            ax.set_yscale(self.y_scale)
        
        self.plots = [[] for _ in range(num_subplots)]

    @staticmethod
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

    def plot(self, xaxis: np.ndarray, yaxis: np.ndarray, label: str, subplot_index: int = 0, linestyle: str = '-'):
        if 0 <= subplot_index < self.num_subplots:
            self.axs[subplot_index].plot(xaxis, yaxis, label=label, linestyle=linestyle)
            self.axs[subplot_index].legend()
            self.plots[subplot_index].append((xaxis, yaxis, label))
        else:
            raise IndexError("subplot_index out of range")

    def add_line(self, line_orientation: str = 'horizontal', line_value: float = None, line_label: str = '', line_color: str = 'red', subplot_index: int = 0):
        if 0 <= subplot_index < self.num_subplots:
            ax = self.axs[subplot_index]
            if line_value is not None:
                if line_orientation == 'horizontal':
                    ax.axhline(y=line_value, color=line_color, linestyle='--', label=f'{line_label}={self.format_value(line_value)}')
                elif line_orientation == 'vertical':
                    ax.axvline(x=line_value, color=line_color, linestyle='--', label=f'{line_label}={self.format_value(line_value)}')
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
                annotation_text = f'Intersection: (X={self.format_value(lookup_value)}, Y={self.format_value(lookup_result)})'
            elif cursor == 'h':
                annotation_text = f'Intersection: (X={self.format_value(lookup_result)}, Y={self.format_value(lookup_value)})'

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
        plt.show(block=False)

    def save(self, filename: str, format: str = 'png', width: int = 8, height: int = 8):
        self.fig.set_size_inches(width, height)
        self.fig.savefig(filename, format=format, bbox_inches='tight')

    def bode_diagram_gain(self, subplot_index: int, frequency: np.ndarray, gain: np.ndarray, **kwargs):
        if 0 <= subplot_index < self.num_subplots:
            ax = self.axs[subplot_index]
            ax.set_xscale('log')
            ax.plot(frequency, gain, **kwargs)
            ax.grid(True)
            ax.grid(True, which='minor')
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Gain [dB]")
        else:
            raise IndexError("subplot_index out of range")

    def bode_diagram_phase(self, subplot_index: int, frequency: np.ndarray, phase: np.ndarray, **kwargs):
        if 0 <= subplot_index < self.num_subplots:
            ax = self.axs[subplot_index]
            ax.set_xscale('log')
            ax.plot(frequency, phase, **kwargs)
            ax.set_ylim(-math.pi, math.pi)
            ax.grid(True)
            ax.grid(True, which='minor')
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Phase [rads]")
            plt.yticks((-math.pi, -math.pi/2, 0, math.pi/2, math.pi),
                       (r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"))
        else:
            raise IndexError("subplot_index out of range")

    def bode_plot(self, frequency: np.ndarray, gain: np.ndarray, phase: np.ndarray, bw_3dB: float, title: str = 'Bode Plot'):
        if self.num_subplots != 2:
            raise ValueError("Number of subplots must be 2 for Bode plot")

        self.fig.suptitle(title)
        self.bode_diagram_gain(0, frequency, gain, marker='.', color='blue', linestyle='-')
        self.bode_diagram_phase(1, frequency, phase, marker='.', color='blue', linestyle='-')

        for ax in self.axs:
            ax.axvline(x=bw_3dB, color='red')
            ax.annotate(f'{self.format_value(bw_3dB)}Hz', xy=(bw_3dB, 0), xytext=(5, 10),
                        textcoords='offset points', arrowprops=dict(arrowstyle='->', color='red'))

# Example usage:
# freq = np.logspace(1, 4, num=400)
# gain = 20 * np.log10(1/np.sqrt(1 + (freq/1000)**2))
# phase = -np.arctan(freq/1000)
# bw_3dB = 1000

# pm = PlotManager(num_subplots=2, title="Bode Plot Example", xlabel="Frequency (Hz)", ylabels=["Gain (dB)", "Phase (rads)"], x_scale='log', y_scale='linear')
# pm.bode_plot(frequency=freq, gain=gain, phase=phase, bw_3dB=bw_3dB)
# pm.show()
