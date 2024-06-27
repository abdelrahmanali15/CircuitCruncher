import numpy as np
import matplotlib.pyplot as plt

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
