import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple
import math
import matplotlib.ticker as ticker

class PlotManager:
    """
    A class to manage and create plots using matplotlib.
    """

    def __init__(self, num_subplots: int = 1, title: str = '', xlabel: str = 'X Axis', 
                 ylabels: Optional[List[str]] = None, **kwargs):
        """
        Initialize the PlotManager.

        :param num_subplots: Number of subplots to create.
        :param title: Main title for the figure.
        :param xlabel: Label for x-axis (common for all subplots).
        :param ylabels: List of labels for y-axis of each subplot.
        :param kwargs: Additional keyword arguments for plot customization.
        """
        self.num_subplots = num_subplots
        self.fig, self.axs = plt.subplots(num_subplots, 1, sharex=True)
        self.fig.suptitle(title)
        self._setup_axes(xlabel, ylabels, **kwargs)
        self.plots = [[] for _ in range(num_subplots)]

    def _setup_axes(self, xlabel: str, ylabels: Optional[List[str]], **kwargs):
        """Set up the axes with proper labels and scales."""
        x_scale = kwargs.get('x_scale', 'linear')
        y_scale = kwargs.get('y_scale', 'linear')

        if self.num_subplots == 1:
            self.axs = [self.axs]

        ylabels = ylabels or ['Y Axis'] * self.num_subplots
        if len(ylabels) != self.num_subplots:
            raise ValueError("The length of ylabels must match num_subplots")

        for ax, ylabel in zip(self.axs, ylabels):
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.grid(True)
            ax.set_xscale(x_scale)
            ax.set_yscale(y_scale)

    @staticmethod
    def format_value(val: float) -> str:
        """
        Format a numerical value with appropriate SI prefixes.

        :param val: The value to format.
        :return: Formatted string representation of the value.
        """
        if np.isnan(val):
            print('NAN')
            return "NaN"
        abs_val = abs(val)
        for exp, suffix in [(1e12, 'T'), (1e9, 'G'), (1e6, 'M'), (1e3, 'k'),
                            (1, ''), (1e-3, 'm'), (1e-6, 'μ'), (1e-9, 'n'),
                            (1e-12, 'p'), (1e-15, 'f')]:
            if abs_val >= exp:
                return f"{val/exp:.2f}{suffix}"
        return f"{val*1e18:.2f}a"

    def plot(self, xaxis: np.ndarray, yaxis: np.ndarray, label: str, 
             subplot_index: int = 0, linestyle: str = '-'):
        """
        Add a plot to a specific subplot.

        :param xaxis: X-axis data.
        :param yaxis: Y-axis data.
        :param label: Label for the plot.
        :param subplot_index: Index of the subplot to add the plot to.
        :param linestyle: Style of the line to plot.
        """
        if 0 <= subplot_index < self.num_subplots:
            self.axs[subplot_index].plot(xaxis, yaxis, label=label, linestyle=linestyle)
            self.axs[subplot_index].legend()
            self.plots[subplot_index].append((xaxis, yaxis, label))
        else:
            raise IndexError("subplot_index out of range")

    def add_line(self, line_orientation: str, line_value: float, line_label: str = '', 
                 line_color: str = 'red', subplot_index: int = 0):
        """
        Add a horizontal or vertical line to a subplot.

        :param line_orientation: 'horizontal' or 'vertical'.
        :param line_value: Value at which to draw the line.
        :param line_label: Label for the line.
        :param line_color: Color of the line.
        :param subplot_index: Index of the subplot to add the line to.
        """
        if 0 <= subplot_index < self.num_subplots:
            ax = self.axs[subplot_index]
            line_func = ax.axhline if line_orientation == 'horizontal' else ax.axvline
            formatted_value = self.format_value(line_value)
            line_func(line_value, color=line_color, linestyle='--', 
                      label=f'{line_label}={formatted_value}')
            ax.legend()
        else:
            raise IndexError("subplot_index out of range")

    def add_annotation(self, lookup_value: float, lookup_array: np.ndarray, 
                       lookup_return_array: np.ndarray, subplot_index: int = 0, 
                       annotation_text: Optional[str] = None, 
                       annotation_color: str = 'red', cursor: str = 'v'):
        """
        Add an annotation to a subplot.

        :param lookup_value: Value to look up.
        :param lookup_array: Array to search in.
        :param lookup_return_array: Array to return values from.
        :param subplot_index: Index of the subplot to add the annotation to.
        :param annotation_text: Text for the annotation.
        :param annotation_color: Color of the annotation.
        :param cursor: 'v' for vertical or 'h' for horizontal cursor.
        """
        if not (0 <= subplot_index < self.num_subplots):
            raise IndexError("subplot_index out of range")

        lookup_result = self._lookup(lookup_array, lookup_value, lookup_return_array)

        if annotation_text is None:
            x_val, y_val = (lookup_value, lookup_result) if cursor == 'v' else (lookup_result, lookup_value)
            annotation_text = f'Intersection: (X={self.format_value(x_val)}, Y={self.format_value(y_val)})'

        x, y = (lookup_value, lookup_result) if cursor == 'v' else (lookup_result, lookup_value)

        self.axs[subplot_index].annotate(annotation_text, xy=(x, y), xycoords='data',
                                         xytext=(-40, 30), textcoords='offset points',
                                         arrowprops=dict(arrowstyle="->", color=annotation_color))

    @staticmethod
    def _lookup(array: np.ndarray, value: float, return_array: np.ndarray) -> float:
        """Find the closest value in an array and return the corresponding value from another array."""
        idx = (np.abs(array - value)).argmin()
        return return_array[idx]

    def show(self):
        """Display the plot."""
        plt.show(block=False)

    def save(self, filename: str, format: str = 'png', width: int = 8, height: int = 8):
        """Save the plot to a file."""
        self.fig.set_size_inches(width, height)
        self.fig.savefig(filename, format=format, bbox_inches='tight')

    

    def _setup_log_paper_background(self, ax):
        """Set up logarithmic paper background for an axis."""
        ax.grid(which="major", color="#666666", linestyle="-", linewidth=1, alpha=0.8)
        ax.grid(which="minor", color="#999999", linestyle=":", linewidth=0.5, alpha=0.5)
        ax.set_facecolor("#f0f0f0")  # Light gray background

        # Customize x-axis (frequency)
        ax.set_xscale('log')
        ax.xaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
        ax.xaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))

        # Customize y-axis
        ax.yaxis.set_major_locator(ticker.AutoLocator())
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    def bode_plot(self, frequency: np.ndarray, gain: np.ndarray, phase: np.ndarray, 
                  bw_3dB: float, title: str = 'Bode Plot'):
        """
        Create a Bode plot with gain and phase diagrams on logarithmic paper background.

        :param frequency: Frequency data in Hz.
        :param gain: Gain data in linear scale.
        :param phase: Phase data in radians.
        :param bw_3dB: 3dB bandwidth frequency in Hz.
        :param title: Title for the Bode plot.
        """
        if self.num_subplots != 2:
            raise ValueError("Number of subplots must be 2 for Bode plot")

        self.fig.suptitle(title, fontsize=20)  # Adjust the fontsize value as needed


        # Gain plot
        self._bode_diagram_gain(0, frequency, gain, bw_3dB)

        # Phase plot
        self._bode_diagram_phase(1, frequency, phase, bw_3dB)

        plt.tight_layout()

    def _bode_diagram_gain(self, subplot_index: int, frequency: np.ndarray, gain: np.ndarray, bw_3dB: float):
        """Helper method to create gain diagram for Bode plot with logarithmic paper background."""
        ax = self.axs[subplot_index]
        ax.semilogx(frequency, (gain), color='blue', linewidth=2)
        self._setup_log_paper_background(ax)
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Magnitude [dB]")
        ax.set_title("Magnitude Response")

        # Set y-axis ticks to be multiples of 20 dB
        y_min, y_max = ax.get_ylim()
        y_ticks = np.arange(math.floor(y_min / 20) * 20, math.ceil(y_max / 20) * 20 + 1, 20)
        ax.set_yticks(y_ticks)

        # Add vertical 3dB bandwidth line
        ax.axvline(x=bw_3dB, color='red', linestyle='--', linewidth=1.5)
        ax.annotate(f'{self.format_value(bw_3dB)}Hz', xy=(bw_3dB, ax.get_ylim()[0]), 
                    xytext=(5, 10), textcoords='offset points', 
                    arrowprops=dict(arrowstyle='->', color='red'))

    def _bode_diagram_phase(self, subplot_index: int, frequency: np.ndarray, phase: np.ndarray, bw_3dB: float):
        """Helper method to create phase diagram for Bode plot with logarithmic paper background."""
        ax = self.axs[subplot_index]
        phase_deg = np.degrees(phase)
        ax.semilogx(frequency, phase_deg, color='green', linewidth=2)
        self._setup_log_paper_background(ax)
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Phase [degrees]")
        ax.set_title("Phase Response")

        # Set y-axis ticks to be multiples of 45 degrees
        y_min, y_max = ax.get_ylim()
        y_ticks = np.arange(math.floor(y_min / 45) * 45, math.ceil(y_max / 45) * 45 + 1, 45)
        ax.set_yticks(y_ticks)

        # Add vertical 3dB bandwidth line
        ax.axvline(x=bw_3dB, color='red', linestyle='--', linewidth=1.5)
        
        # Find the phase at the 3dB frequency
        phase_at_3db = np.interp(bw_3dB, frequency, phase_deg)
        
        # Add horizontal cursor at the intersection
        ax.axhline(y=phase_at_3db, color='purple', linestyle=':', linewidth=1.5)
        
        # Add annotation for the intersection point
        ax.plot(bw_3dB, phase_at_3db, 'ro')  # Red dot at intersection
        ax.annotate(f'({self.format_value(bw_3dB)}Hz, {phase_at_3db:.2f}°)', 
                    xy=(bw_3dB, phase_at_3db), xytext=(10, -10),
                    textcoords='offset points', color='purple',
                    arrowprops=dict(arrowstyle='->', color='purple'))

# Example usage:
# if __name__ == "__main__":
#     freq = np.logspace(1, 4, num=400)
#     gain = 20 * np.log10(1/np.sqrt(1 + (freq/1000)**2))
#     phase = -np.arctan(freq/1000)
#     bw_3dB = 1000
#
#     pm = PlotManager(num_subplots=2, title="Bode Plot Example", xlabel="Frequency (Hz)", 
#                      ylabels=["Gain (dB)", "Phase (rads)"], x_scale='log', y_scale='linear')
#     pm.bode_plot(frequency=freq, gain=gain, phase=phase, bw_3dB=bw_3dB)
#     pm.show()