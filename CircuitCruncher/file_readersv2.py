
import numpy as np
from typing import Tuple, List, Dict, Any, BinaryIO, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)


class NgRawReadError(Exception):
    pass


@dataclass
class Dataset:
    """
    Represents a single dataset with its data and metadata.
    
    Attributes:
        data: NumPy structured array containing the actual data
        metadata: Dictionary containing all metadata from the file
        variable_names: List of variable names in order
        variable_units: List of corresponding units
        title: Dataset title (if available)
        num_variables: Number of variables
        num_points: Number of data points
        is_complex: Whether the data contains complex numbers
    """
    data: np.ndarray
    metadata: Dict[str, Any]
    variable_names: List[str]
    variable_units: List[str]
    title: Optional[str] = None
    num_variables: int = 0
    num_points: int = 0
    is_complex: bool = False
    
    def __post_init__(self):
        """Extract common properties from metadata after initialization."""
        self.num_variables = len(self.variable_names)
        self.num_points = len(self.data) if self.data is not None else 0
        self.title = self.metadata.get(b'title')
        flags = self.metadata.get(b'flags', b'')
        self.is_complex = b'complex' in flags if isinstance(flags, bytes) else 'complex' in str(flags)
    
    def get_variable_data(self, variable_name: str) -> np.ndarray:
        """Get data for a specific variable by name."""
        if variable_name not in self.data.dtype.names:
            raise ValueError(f"Variable '{variable_name}' not found. Available: {list(self.data.dtype.names)}")
        return self.data[variable_name]
    
    def get_statistics(self, variable_name: str) -> Dict[str, float]:
        """Get statistics for a variable."""
        data_col = self.get_variable_data(variable_name)
        
        if np.isrealobj(data_col):
            return {
                'min': float(np.min(data_col)),
                'max': float(np.max(data_col)),
                'mean': float(np.mean(data_col)),
                'std': float(np.std(data_col))
            }
        else:
            return {
                'real_min': float(np.min(data_col.real)),
                'real_max': float(np.max(data_col.real)),
                'imag_min': float(np.min(data_col.imag)),
                'imag_max': float(np.max(data_col.imag))
            }


class NgRawReader:
    """
    A parser for ngspice raw binary files containing numerical data with metadata.
    
    This class can handle files with multiple datasets, where each dataset contains:
    - Metadata lines in the format 'key: value'
    - Variable specifications (after 'variables' key)
    - Binary data arrays (after 'binary' key)
    
    Example usage:
        reader = NgRawReader()
        datasets = reader.read_file("data.raw")
        
        # Access first dataset
        first_dataset = datasets[0]
        print(f"Title: {first_dataset.title}")
        print(f"Variables: {first_dataset.variable_names}")
        
        # Get specific variable data
        voltage_data = first_dataset.get_variable_data('voltage')
    """
    
    # Class constants
    DEFAULT_BUFFER_SIZE = 1024
    REQUIRED_METADATA_KEYS = [b'no. variables', b'no. points']
    
    def __init__(self, buffer_size: int = DEFAULT_BUFFER_SIZE):
        """
        Initialize the reader.
        
        Args:
            buffer_size: Buffer size for reading lines from file
        """
        self.buffer_size = buffer_size
        
    def read_file(self, file_path: Union[str, Path]) -> 'Datasets':
        """
        Read and parse a binary file containing numerical data with metadata.
        
        Args:
            file_path: Path to the input file
            
        Returns:
            Datasets object containing all datasets from the file
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            NgRawReadError: If the file format is invalid or parsing fails
            IOError: If there are file reading issues
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with self._open_file(file_path) as fp:
                dataset_list = self._parse_file(fp)
                return Datasets(datasets=dataset_list)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise NgRawReadError(f"Failed to parse file {file_path}: {e}") from e
    
    @contextmanager
    def _open_file(self, file_path: Path):
        """Context manager for file operations."""
        try:
            with open(file_path, 'rb') as fp:
                yield fp
        except IOError as e:
            raise NgRawReadError(f"Cannot open file {file_path}: {e}") from e
    
    def _parse_file(self, fp: BinaryIO) -> List[Dataset]:
        """Parse the opened file and extract datasets."""
        datasets = []
        
        while True:
            dataset = self._parse_single_dataset(fp)
            if dataset is None:
                break
            datasets.append(dataset)
        
        if not datasets:
            raise NgRawReadError("No valid datasets found in file")
            
        return datasets
    
    
    def _parse_single_dataset(self, fp: BinaryIO) -> Optional[Dataset]:
        """Parse a single dataset from the file."""
        metadata = {}
        
        # Read metadata section
        while True:
            line_data = self._read_metadata_line(fp)
            if line_data is None:
                return None  # End of file
                
            key, value = line_data
            metadata[key] = value
            
            if key == b'variables':
                var_info = self._parse_variables(fp, metadata)
                metadata.update(var_info)
                self._ensure_unique_variable_names_within_dataset(metadata)
                
            elif key == b'binary':
                data_array = self._parse_binary_data(fp, metadata)
                return self._create_dataset(data_array, metadata)
    
    def _read_metadata_line(self, fp: BinaryIO) -> Optional[Tuple[bytes, bytes]]:
        """Read and parse a single metadata line."""
        try:
            line = fp.readline(self.buffer_size)
            if not line:
                return None
                
            if b':' not in line:
                return None
                
            parts = line.split(b':', maxsplit=1)
            if len(parts) != 2:
                return None
                
            key = parts[0].lower().strip()
            value = parts[1].strip()
            return key, value
            
        except Exception as e:
            raise NgRawReadError(f"Error reading metadata line: {e}") from e
    
    def _parse_variables(self, fp: BinaryIO, metadata: dict) -> dict:
        """Parse variable specifications from the file."""
        # Validate required metadata
        missing_keys = [key for key in self.REQUIRED_METADATA_KEYS if key not in metadata]
        if missing_keys:
            missing_str = ', '.join(k.decode('ascii') for k in missing_keys)
            raise NgRawReadError(f"Missing required metadata: {missing_str}")
        
        # Extract and validate dimensions
        try:
            num_vars = int(metadata[b'no. variables'])
            num_points = int(metadata[b'no. points'])
        except (ValueError, KeyError) as e:
            raise NgRawReadError(f"Invalid numeric values in metadata: {e}") from e
        
        if num_vars <= 0 or num_points <= 0:
            raise NgRawReadError(f"Invalid dimensions: variables={num_vars}, points={num_points}")
        
        # Parse variable specifications
        var_names = []
        var_units = []
        
        for var_index in range(num_vars):
            var_line = self._read_variable_line(fp, var_index)
            var_parts = var_line.split()
            
            if len(var_parts) < 3:
                raise NgRawReadError(f"Invalid variable specification: {var_line}")
            
            # Validate variable index
            try:
                actual_index = int(var_parts[0])
            except ValueError:
                raise NgRawReadError(f"Invalid variable index: {var_parts[0]}") from None
                
            if actual_index != var_index:
                raise NgRawReadError(f"Variable index mismatch: expected {var_index}, got {actual_index}")
            
            var_names.append(var_parts[1])
            var_units.append(var_parts[2])
        
        return {
            'varnames': var_names,
            'varunits': var_units,
            'num_vars': num_vars,
            'num_points': num_points
        }
    
    def _read_variable_line(self, fp: BinaryIO, var_index: int) -> str:
        """Read and decode a variable specification line."""
        var_line = fp.readline(self.buffer_size).strip().decode('ascii')
        if not var_line:
            raise NgRawReadError(f"Unexpected end of file while reading variable {var_index}")
        return var_line
    
    def _ensure_unique_variable_names_within_dataset(self, metadata: dict) -> None:
        """Ensure all variable names are unique within a single dataset by adding suffixes if needed."""
        updated_names = []
        used_names = set()
        name_suffix = 0
        
        for var_name in metadata['varnames']:
            original_name = var_name
            while var_name in used_names:
                var_name = f"{original_name}_{name_suffix}"
                name_suffix += 1
            
            used_names.add(var_name)
            updated_names.append(var_name)
        
        metadata['varnames'] = updated_names
    
    def _parse_binary_data(self, fp: BinaryIO, metadata: dict) -> np.ndarray:
        """Parse binary data section of the file."""
        if b'flags' not in metadata:
            raise NgRawReadError("Missing 'flags' in metadata before 'binary' section")
        
        num_vars = metadata['num_vars']
        num_points = metadata['num_points']
        
        # determine data type based on flags
        is_complex = b'complex' in metadata[b'flags']
        base_dtype = np.complex128 if is_complex else np.float64
        dtype_formats = [base_dtype] * num_vars
        
        #  structured array dtype
        try:
            row_dtype = np.dtype({
                'names': metadata['varnames'], 
                'formats': dtype_formats
            })
        except Exception as e:
            raise NgRawReadError(f"Failed to create numpy dtype: {e}") from e
        
        # read binary data
        try:
            array = np.fromfile(fp, dtype=row_dtype, count=num_points)
            if len(array) != num_points:
                logger.warning(f"Expected {num_points} points, got {len(array)}")
                
            
            fp.readline() # skip end-of-line character after binary data
            
            return array
            
        except Exception as e:
            raise NgRawReadError(f"Failed to read binary data: {e}") from e
    
    def _create_dataset(self, data_array: np.ndarray, metadata: dict) -> Dataset:
        """Create a Dataset object from parsed data and metadata."""
        return Dataset(
            data=data_array,
            metadata=metadata,
            variable_names=metadata.get('varnames', []),
            variable_units=metadata.get('varunits', [])
        )


@dataclass
class Datasets:
    """
    Container class for managing multiple datasets with cross-dataset operations.
    
    Attributes:
        datasets: List of Dataset objects
        dataset_names: List of dataset names/titles for identification
    """
    datasets: List[Dataset]
    dataset_names: List[str] = None
    
    def __post_init__(self):
        """Initialize dataset names if not provided."""
        if self.dataset_names is None:
            self.dataset_names = []
            for i, dataset in enumerate(self.datasets):
                name = dataset.title or f"Dataset_{i+1}"
                if isinstance(name, bytes):
                    name = name.decode('ascii', errors='ignore')
                self.dataset_names.append(str(name))
    
    def __len__(self) -> int:
        """Return number of datasets."""
        return len(self.datasets)
    
    def __getitem__(self, index: int) -> Dataset:
        """Get dataset by index."""
        return self.datasets[index]
    
    def __iter__(self):
        """Iterate over datasets."""
        return iter(self.datasets)
    
    def get_dataset_by_name(self, name: str) -> Optional[Dataset]:
        """Get dataset by name/title."""
        for i, dataset_name in enumerate(self.dataset_names):
            if dataset_name == name:
                return self.datasets[i]
        return None
    
    def get_all_variable_names(self) -> List[str]:
        """Get all unique variable names across all datasets."""
        all_vars = set()
        for dataset in self.datasets:
            all_vars.update(dataset.variable_names)
        return sorted(list(all_vars))
    
    def get_datasets_with_variable(self, variable_name: str) -> List[Tuple[int, Dataset]]:
        """
        Get all datasets that contain a specific variable.
        
        Returns:
            List of tuples (dataset_index, dataset) containing the variable
        """
        matching_datasets = []
        for i, dataset in enumerate(self.datasets):
            if variable_name in dataset.variable_names:
                matching_datasets.append((i, dataset))
        return matching_datasets
    
    def get_variable_across_datasets(self, variable_name: str) -> Dict[str, np.ndarray]:
        """
        Get variable data from all datasets that contain it.
        
        Returns:
            Dictionary mapping dataset names to variable data arrays
        """
        result = {}
        for i, dataset in enumerate(self.datasets):
            if variable_name in dataset.variable_names:
                dataset_name = self.dataset_names[i]
                result[dataset_name] = dataset.get_variable_data(variable_name)
        return result
    
    def get_common_variables(self) -> List[str]:
        """Get variables that exist in all datasets."""
        if not self.datasets:
            return []
        
        common_vars = set(self.datasets[0].variable_names)
        for dataset in self.datasets[1:]:
            common_vars &= set(dataset.variable_names)
        return sorted(list(common_vars))
    
    def get_variable_summary(self, variable_name: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of a variable across all datasets.
        
        Returns:
            Dictionary with dataset names, statistics, and metadata
        """
        summary = {
            'variable_name': variable_name,
            'datasets_containing': [],
            'total_datasets': len(self.datasets),
            'data_by_dataset': {},
            'statistics_by_dataset': {},
            'units_by_dataset': {}
        }
        
        for i, dataset in enumerate(self.datasets):
            if variable_name in dataset.variable_names:
                dataset_name = self.dataset_names[i]
                summary['datasets_containing'].append(dataset_name)
                
                var_data = dataset.get_variable_data(variable_name)
                summary['data_by_dataset'][dataset_name] = var_data
                summary['statistics_by_dataset'][dataset_name] = dataset.get_statistics(variable_name)

                var_index = dataset.variable_names.index(variable_name)
                if var_index < len(dataset.variable_units):
                    summary['units_by_dataset'][dataset_name] = dataset.variable_units[var_index]
        
        summary['found_in_datasets'] = len(summary['datasets_containing'])
        return summary
    
    def combine_variable_data(self, variable_name: str, 
                            independent_var: str = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Combine variable data from multiple datasets into single arrays.
        
        Args:
            variable_name: Name of the variable to combine
            independent_var: Name of independent variable (e.g., time, frequency)
                           If None, uses indices
        
        Returns:
            Tuple of (independent_values, dependent_values) arrays
        """
        all_independent = []
        all_dependent = []
        
        for dataset in self.datasets:
            if variable_name in dataset.variable_names:
                dependent_data = dataset.get_variable_data(variable_name)
                
                if independent_var and independent_var in dataset.variable_names:
                    independent_data = dataset.get_variable_data(independent_var)
                else:
                    independent_data = np.arange(len(dependent_data))
                
                all_independent.extend(independent_data)
                all_dependent.extend(dependent_data)
        
        return np.array(all_independent), np.array(all_dependent)
    
    def filter_datasets_by_metadata(self, metadata_key: str, 
                                  metadata_value: Any = None) -> 'Datasets':
        """
        Filter datasets based on metadata criteria.
        
        Args:
            metadata_key: Key to filter by
            metadata_value: Value to match (if None, just checks for key existence)
        
        Returns:
            New Datasets object with filtered datasets
        """
        filtered_datasets = []
        filtered_names = []
        
        for i, dataset in enumerate(self.datasets):
            key_bytes = metadata_key.encode('ascii') if isinstance(metadata_key, str) else metadata_key
            
            if key_bytes in dataset.metadata:
                if metadata_value is None:
                    # just check for key existence
                    filtered_datasets.append(dataset)
                    filtered_names.append(self.dataset_names[i])
                else:
                    # ccheck for specific value
                    actual_value = dataset.metadata[key_bytes]
                    if isinstance(actual_value, bytes):
                        actual_value = actual_value.decode('ascii', errors='ignore')
                    
                    if actual_value == metadata_value:
                        filtered_datasets.append(dataset)
                        filtered_names.append(self.dataset_names[i])
        
        return Datasets(datasets=filtered_datasets, dataset_names=filtered_names)
    
    def get_datasets_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all datasets."""
        return {
            'total_datasets': len(self.datasets),
            'dataset_names': self.dataset_names,
            'total_variables': len(self.get_all_variable_names()),
            'common_variables': self.get_common_variables(),
            'all_variables': self.get_all_variable_names(),
            'datasets_info': [
                {
                    'name': name,
                    'num_variables': dataset.num_variables,
                    'num_points': dataset.num_points,
                    'is_complex': dataset.is_complex,
                    'variables': dataset.variable_names
                }
                for name, dataset in zip(self.dataset_names, self.datasets)
            ]
        }


class NgRawAnalyzer:
    """
    dumb utility class for analyzing and debugging NgRaw datasets.
    """
    
    @staticmethod
    def print_datasets_summary(datasets: 'Datasets') -> None:
        """Print a summary of all datasets in a Datasets container."""
        print(f"Successfully read {len(datasets)} dataset(s)\n")
        
        # Print overall summary
        summary = datasets.get_datasets_summary()
        print("=" * 60)
        print("DATASETS OVERVIEW")
        print("=" * 60)
        print(f"Total datasets: {summary['total_datasets']}")
        print(f"Dataset names: {summary['dataset_names']}")
        print(f"Total unique variables: {summary['total_variables']}")
        print(f"Common variables: {summary['common_variables']}")
        print(f"All variables: {summary['all_variables']}")
        print()
        
        # Print individual dataset details
        for i, dataset in enumerate(datasets):
            NgRawAnalyzer.print_single_dataset(dataset, i + 1)
    
    @staticmethod
    def print_dataset_summary(datasets: List[Dataset]) -> None:
        """Print a summary of datasets from a list (legacy method)."""
        print(f"Successfully read {len(datasets)} dataset(s)\n")
        
        for i, dataset in enumerate(datasets):
            NgRawAnalyzer.print_single_dataset(dataset, i + 1)
    
    @staticmethod
    def print_variable_across_datasets(datasets: 'Datasets', variable_name: str) -> None:
        """Print information about a variable across all datasets."""
        print("=" * 60)
        print(f"VARIABLE ANALYSIS: {variable_name}")
        print("=" * 60)
        
        summary = datasets.get_variable_summary(variable_name)
        
        print(f"Variable '{variable_name}' found in {summary['found_in_datasets']}/{summary['total_datasets']} datasets")
        print(f"Datasets containing this variable: {summary['datasets_containing']}")
        print()
        
        for dataset_name in summary['datasets_containing']:
            print(f"Dataset: {dataset_name}")
            stats = summary['statistics_by_dataset'][dataset_name]
            units = summary['units_by_dataset'].get(dataset_name, 'unknown')
            data = summary['data_by_dataset'][dataset_name]
            
            print(f"  Units: {units}")
            print(f"  Data points: {len(data)}")
            print(f"  Statistics:")
            for stat_name, stat_value in stats.items():
                print(f"    {stat_name.replace('_', ' ').title()}: {stat_value:.3e}")
            print()
    
    @staticmethod
    def print_common_variables_analysis(datasets: 'Datasets') -> None:
        """Print analysis of variables common to all datasets."""
        common_vars = datasets.get_common_variables()
        
        print("=" * 60)
        print("COMMON VARIABLES ANALYSIS")
        print("=" * 60)
        
        if not common_vars:
            print("No variables are common to all datasets.")
            return
        
        print(f"Variables common to all {len(datasets)} datasets: {common_vars}")
        print()
        
        for var_name in common_vars:
            print(f"Variable: {var_name}")
            var_data_dict = datasets.get_variable_across_datasets(var_name)
            
            for dataset_name, data in var_data_dict.items():
                print(f"  {dataset_name}: {len(data)} points")
            print()
    
    @staticmethod
    def print_single_dataset(dataset: Dataset, index: int = 1) -> None:
        """Print detailed information about a single dataset."""
        print("=" * 60)
        print(f"DATASET {index}")
        print("=" * 60)
        
        print("METADATA:")
        NgRawAnalyzer._print_metadata(dataset.metadata)
        
        print(f"\nARRAY INFO:")
        print(f"  Shape: {dataset.data.shape}")
        print(f"  Dtype: {dataset.data.dtype}")
        print(f"  Variables: {dataset.variable_names}")
        print(f"  Units: {dataset.variable_units}")
        print(f"  Complex data: {dataset.is_complex}")
        
        NgRawAnalyzer._print_sample_data(dataset)

        NgRawAnalyzer._print_statistics(dataset)
        print()
    
    @staticmethod
    def _print_metadata(metadata: Dict[str, Any]) -> None:
        """Print metadata in a formatted way."""
        for key, value in metadata.items():
            if isinstance(value, bytes):
                value = value.decode('ascii', errors='ignore')
            elif isinstance(value, list) and len(value) > 0:
                if len(value) <= 10:
                    value = f"[{', '.join(map(str, value))}]"
                else:
                    value = f"[{', '.join(map(str, value[:5]))}, ... +{len(value)-5} more]"
            print(f"  {key}: {value}")
    
    @staticmethod
    def _print_sample_data(dataset: Dataset) -> None:
        """Print sample data from the dataset."""
        print(f"\nSAMPLE DATA:")
        if len(dataset.data) == 0:
            print("  No data points found")
            return
            
        num_rows_to_show = min(5, len(dataset.data))
        print(f"  First {num_rows_to_show} rows:")
        
        for row_idx in range(num_rows_to_show):
            row_data = {}
            for var_name in dataset.data.dtype.names:
                val = dataset.data[var_name][row_idx]
                if np.iscomplexobj(val):
                    row_data[var_name] = f"{val:.3e}"
                else:
                    row_data[var_name] = f"{val:.3e}"
            print(f"    Row {row_idx}: {row_data}")
    
    @staticmethod
    def _print_statistics(dataset: Dataset) -> None:
        if len(dataset.data) <= 1:
            return
            
        print(f"\n  STATISTICS:")
        for var_name in dataset.variable_names:
            try:
                stats = dataset.get_statistics(var_name)
                print(f"    {var_name}:")
                for stat_name, stat_value in stats.items():
                    print(f"      {stat_name.replace('_', ' ').title()}: {stat_value:.3e}")
            except Exception as e:
                print(f"    {var_name}: Error calculating statistics - {e}")


def main():
    try:
        reader = NgRawReader()
        
        # datasets = reader.read_file("test_sweep_mos_w.raw")
        datasets = reader.read_file("ota-5t_tb2_ac.raw")
        
        analyzer = NgRawAnalyzer()
        analyzer.print_datasets_summary(datasets)
        
        print("\n" + "="*60)
        print("CROSS-DATASET ANALYSIS EXAMPLES")
        print("="*60)
        
        # Get all variables across datasets
        all_vars = datasets.get_all_variable_names()
        print(f"All variables across datasets: {all_vars}")
        
        # Get common variables
        common_vars = datasets.get_common_variables()
        print(f"Variables common to all datasets: {common_vars}")
        
        if all_vars:
            example_var = all_vars[0]
            print(f"\nAnalyzing variable '{example_var}' across datasets:")
            analyzer.print_variable_across_datasets(datasets, example_var)
            
            # Get variable data from all datasets
            var_data_dict = datasets.get_variable_across_datasets(example_var)
            print(f"Variable '{example_var}' data summary:")
            print(f"Variable '{var_data_dict}' data :")
            for dataset_name, data in var_data_dict.items():
                print(f"  {dataset_name}: {len(data)} points, "
                      f"range: {np.min(data):.3e} to {np.max(data):.3e}")
        
        # Show common variables analysis
        if common_vars:
            analyzer.print_common_variables_analysis(datasets)
        
        # Example of accessing individual datasets
        if len(datasets) > 0:
            first_dataset = datasets[0]
            print(f"\nFirst dataset title: {first_dataset.title}")
            print(f"First dataset variables: {first_dataset.variable_names}")

            dataset_by_name = datasets.get_dataset_by_name(datasets.dataset_names[0])
            if dataset_by_name:
                print(f"Retrieved dataset by name: {datasets.dataset_names[0]}")
        
        # Example of filtering datasets
        filtered = datasets.filter_datasets_by_metadata('flags')
        print(f"\nDatasets with 'flags' metadata: {len(filtered)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
