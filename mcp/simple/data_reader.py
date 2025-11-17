"""
Data Reader MCP Domain

Provides MCPBase-compliant operations for data loading and analysis:
- Reading CSV, JSON, Parquet, Excel files
- Querying dataframes
- Schema introspection
- Data type detection

All operations are read-only and cached for performance.
"""

from pathlib import Path
import json
from typing import Dict, Any, List, Optional, Union
import pandas as pd

from ..core.base import MCPBase, MCPResponse, MCPStatus
from ..core.decorators import read_only, cached


class DataReader(MCPBase):
    """
    Data loading and analysis domain for MCP.

    Provides core functionality for:
    - Reading CSV files (@read_only @cached)
    - Reading JSON files (@read_only @cached)
    - Reading Parquet files (@read_only @cached)
    - Reading Excel files (@read_only @cached)
    - Querying dataframes (@read_only)
    - Schema introspection (@read_only @cached)

    All methods return MCPResponse for standardized interaction.
    Caching is applied for expensive I/O operations (TTL: 300s).
    """

    def __init__(self, logger=None, context: Dict[str, Any] = None):
        """
        Initialize the data reader domain.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        super().__init__(logger=logger, context=context)

    # ===== Path Validation =====

    def _validate_file(self, path: str, extensions: List[str] = None) -> tuple[bool, Optional[Path], Optional[str]]:
        """
        Validate a file path for data reading.

        Args:
            path: File path to validate
            extensions: Optional list of allowed extensions (e.g., ['.csv', '.json'])

        Returns:
            Tuple of (is_valid, Path object, error_message)
        """
        try:
            file_path = Path(path).resolve()

            # Check existence
            if not file_path.exists():
                return False, None, f"File not found: {path}"

            # Check if it's a file
            if not file_path.is_file():
                return False, None, f"Not a file: {path}"

            # Check extension if specified
            if extensions and file_path.suffix.lower() not in extensions:
                return False, None, f"Invalid file type. Expected: {extensions}, got: {file_path.suffix}"

            return True, file_path, None

        except Exception as e:
            return False, None, f"Path validation error: {str(e)}"

    # ===== CSV Operations =====

    @read_only
    @cached(ttl=300)
    def read_csv(
        self,
        path: str,
        delimiter: str = ",",
        header: Union[int, str] = 0,
        encoding: str = "utf-8",
        max_rows: Optional[int] = None
    ) -> MCPResponse:
        """
        Read a CSV file into a pandas DataFrame.

        Args:
            path: Path to CSV file
            delimiter: Column delimiter (default: ',')
            header: Row number to use as header or 'infer' (default: 0)
            encoding: File encoding (default: 'utf-8')
            max_rows: Maximum number of rows to read (default: None = all)

        Returns:
            MCPResponse with data containing:
            - path: File path
            - shape: (rows, columns)
            - columns: List of column names
            - dtypes: Data types per column
            - preview: First 5 rows as dict
            - data: Full dataframe as dict (if max_rows specified)
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Reading CSV file: {path}')

        try:
            # Validate file
            is_valid, file_path, error = self._validate_file(path, ['.csv', '.txt', '.tsv'])
            if not is_valid:
                response.set_error(error)
                return response

            # Read CSV
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                header=header if header != 'infer' else 'infer',
                encoding=encoding,
                nrows=max_rows
            )

            response.data = {
                'path': str(file_path),
                'shape': df.shape,
                'rows': df.shape[0],
                'columns': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'preview': df.head().to_dict(orient='records'),
                'has_data': True
            }

            # Include full data if small enough
            if df.shape[0] <= 1000:
                response.data['data'] = df.to_dict(orient='records')

            response.add_trace(f'CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns')
            return response

        except pd.errors.EmptyDataError:
            response.set_error(f"CSV file is empty: {path}")
            return response
        except pd.errors.ParserError as e:
            response.set_error(f"Failed to parse CSV: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Failed to read CSV: {str(e)}")
            return response

    # ===== JSON Operations =====

    @read_only
    @cached(ttl=300)
    def read_json(self, path: str, orient: str = "records") -> MCPResponse:
        """
        Read a JSON file.

        Args:
            path: Path to JSON file
            orient: JSON orientation ('records', 'index', 'columns', 'values', 'split')

        Returns:
            MCPResponse with data containing:
            - path: File path
            - data: JSON data (parsed)
            - size: Number of records (if list/dict)
            - type: Data type (list, dict, etc.)
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Reading JSON file: {path}')

        try:
            # Validate file
            is_valid, file_path, error = self._validate_file(path, ['.json'])
            if not is_valid:
                response.set_error(error)
                return response

            # Read JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Determine size
            size = None
            if isinstance(data, list):
                size = len(data)
            elif isinstance(data, dict):
                size = len(data)

            response.data = {
                'path': str(file_path),
                'data': data,
                'type': type(data).__name__,
                'size': size
            }
            response.add_trace(f'JSON loaded: {type(data).__name__}')
            return response

        except json.JSONDecodeError as e:
            response.set_error(f"Invalid JSON format: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Failed to read JSON: {str(e)}")
            return response

    # ===== Parquet Operations =====

    @read_only
    @cached(ttl=300)
    def read_parquet(self, path: str, columns: Optional[List[str]] = None) -> MCPResponse:
        """
        Read a Parquet file into a pandas DataFrame.

        Args:
            path: Path to Parquet file
            columns: Optional list of columns to read (default: all)

        Returns:
            MCPResponse with data containing:
            - path: File path
            - shape: (rows, columns)
            - columns: List of column names
            - dtypes: Data types per column
            - preview: First 5 rows as dict
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Reading Parquet file: {path}')

        try:
            # Validate file
            is_valid, file_path, error = self._validate_file(path, ['.parquet', '.pq'])
            if not is_valid:
                response.set_error(error)
                return response

            # Read Parquet
            df = pd.read_parquet(file_path, columns=columns)

            response.data = {
                'path': str(file_path),
                'shape': df.shape,
                'rows': df.shape[0],
                'columns': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'preview': df.head().to_dict(orient='records'),
                'has_data': True
            }

            # Include full data if small enough
            if df.shape[0] <= 1000:
                response.data['data'] = df.to_dict(orient='records')

            response.add_trace(f'Parquet loaded: {df.shape[0]} rows, {df.shape[1]} columns')
            return response

        except Exception as e:
            response.set_error(f"Failed to read Parquet: {str(e)}")
            return response

    # ===== Excel Operations =====

    @read_only
    @cached(ttl=300)
    def read_excel(
        self,
        path: str,
        sheet_name: Union[str, int] = 0,
        header: int = 0,
        max_rows: Optional[int] = None
    ) -> MCPResponse:
        """
        Read an Excel file into a pandas DataFrame.

        Args:
            path: Path to Excel file
            sheet_name: Sheet name or index (default: 0 = first sheet)
            header: Row number to use as header (default: 0)
            max_rows: Maximum number of rows to read (default: None = all)

        Returns:
            MCPResponse with data containing:
            - path: File path
            - sheet: Sheet name
            - shape: (rows, columns)
            - columns: List of column names
            - dtypes: Data types per column
            - preview: First 5 rows as dict
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Reading Excel file: {path}, sheet: {sheet_name}')

        try:
            # Validate file
            is_valid, file_path, error = self._validate_file(path, ['.xlsx', '.xls', '.xlsm'])
            if not is_valid:
                response.set_error(error)
                return response

            # Read Excel
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header,
                nrows=max_rows
            )

            response.data = {
                'path': str(file_path),
                'sheet': sheet_name,
                'shape': df.shape,
                'rows': df.shape[0],
                'columns': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'preview': df.head().to_dict(orient='records'),
                'has_data': True
            }

            # Include full data if small enough
            if df.shape[0] <= 1000:
                response.data['data'] = df.to_dict(orient='records')

            response.add_trace(f'Excel loaded: {df.shape[0]} rows, {df.shape[1]} columns')
            return response

        except Exception as e:
            response.set_error(f"Failed to read Excel: {str(e)}")
            return response

    # ===== Schema Introspection =====

    @read_only
    @cached(ttl=300)
    def get_schema(self, path: str, format: Optional[str] = None) -> MCPResponse:
        """
        Get schema information for a data file.

        Args:
            path: Path to data file
            format: Optional format hint ('csv', 'json', 'parquet', 'excel')
                   If not provided, will be inferred from extension

        Returns:
            MCPResponse with data containing:
            - path: File path
            - format: Detected format
            - columns: Column names (if applicable)
            - dtypes: Data types (if applicable)
            - row_count: Approximate row count
            - file_size: File size in bytes
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Getting schema for: {path}')

        try:
            file_path = Path(path).resolve()

            if not file_path.exists():
                response.set_error(f"File not found: {path}")
                return response

            # Infer format from extension if not provided
            if not format:
                ext = file_path.suffix.lower()
                format_map = {
                    '.csv': 'csv',
                    '.txt': 'csv',
                    '.json': 'json',
                    '.parquet': 'parquet',
                    '.pq': 'parquet',
                    '.xlsx': 'excel',
                    '.xls': 'excel'
                }
                format = format_map.get(ext, 'unknown')

            # Get file size
            file_size = file_path.stat().st_size

            # Get schema based on format
            schema_data = {
                'path': str(file_path),
                'format': format,
                'file_size': file_size
            }

            if format == 'csv':
                df = pd.read_csv(file_path, nrows=1)
                schema_data.update({
                    'columns': df.columns.tolist(),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'column_count': len(df.columns)
                })

            elif format == 'parquet':
                df = pd.read_parquet(file_path)
                schema_data.update({
                    'columns': df.columns.tolist(),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'row_count': len(df),
                    'column_count': len(df.columns)
                })

            elif format == 'excel':
                df = pd.read_excel(file_path, nrows=1)
                schema_data.update({
                    'columns': df.columns.tolist(),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'column_count': len(df.columns)
                })

            elif format == 'json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                schema_data.update({
                    'type': type(data).__name__,
                    'size': len(data) if isinstance(data, (list, dict)) else None
                })

            response.data = schema_data
            response.add_trace(f'Schema retrieved for {format} file')
            return response

        except Exception as e:
            response.set_error(f"Failed to get schema: {str(e)}")
            return response

    # ===== Query Operations =====

    @read_only
    def query_dataframe(self, data: Union[Dict, List], query: str) -> MCPResponse:
        """
        Query a dataframe using pandas query syntax.

        Args:
            data: Data as dict or list (will be converted to DataFrame)
            query: Pandas query string (e.g., "age > 30 and city == 'NYC'")

        Returns:
            MCPResponse with data containing:
            - query: Original query string
            - result: Query result as list of dicts
            - row_count: Number of rows in result
        """
        response = MCPResponse.success_response()
        response.add_trace(f'Querying dataframe: {query}')

        try:
            # Convert to DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                response.set_error("Data must be a dict or list")
                return response

            # Execute query
            result_df = df.query(query)

            response.data = {
                'query': query,
                'result': result_df.to_dict(orient='records'),
                'row_count': len(result_df),
                'original_row_count': len(df)
            }
            response.add_trace(f'Query returned {len(result_df)} rows')
            return response

        except pd.errors.UndefinedVariableError as e:
            response.set_error(f"Invalid query - undefined variable: {str(e)}")
            return response
        except Exception as e:
            response.set_error(f"Query failed: {str(e)}")
            return response
