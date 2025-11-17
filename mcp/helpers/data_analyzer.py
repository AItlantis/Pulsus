"""
DataAnalyzer - Class-Based MCP Helper for Data Analysis Operations

Provides MCP-compliant methods for:
- Querying and filtering data
- Aggregating and summarizing data
- Statistical analysis
- Data transformation
- Export and reporting

This is a general-purpose data analyzer that works with various data sources.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json

# MCP Core Framework imports
from agents.mcp.core import (
    MCPBase,
    MCPResponse,
    read_only,
    write_safe,
    cached,
    get_mcp_logger
)


class DataAnalyzer(MCPBase):
    """
    Class-based MCP helper for data analysis operations.

    Provides safe, structured methods for:
    - Data querying and filtering
    - Statistical analysis
    - Aggregation and grouping
    - Data transformation
    - Report generation

    All methods return MCPResponse objects with standardized structure.
    """

    def __init__(self, logger=None, context=None):
        """
        Initialize DataAnalyzer.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        if logger is None:
            logger = get_mcp_logger()

        if context is None:
            context = {'caller': 'DataAnalyzer'}

        super().__init__(logger=logger, context=context)

    # ===== Data Querying =====

    @read_only
    def query_data(self, data: Union[List[Dict], Dict], filter_criteria: Optional[Dict[str, Any]] = None,
                  max_results: int = 1000) -> MCPResponse:
        """
        Query and filter data.

        Safe read-only operation.

        Args:
            data: Data to query (list of dicts or dict)
            filter_criteria: Optional filter dictionary
            max_results: Maximum number of results to return

        Returns:
            MCPResponse with filtered data
        """
        response = self._create_response()
        response.add_trace("Querying data")

        try:
            # Normalize data to list
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                response.set_error("Data must be a list of dictionaries or a dictionary")
                return response

            response.add_trace(f"Input records: {len(data)}")

            # Apply filters
            if filter_criteria:
                filtered_data = self._apply_filters(data, filter_criteria)
                response.add_trace(f"After filtering: {len(filtered_data)} records")
            else:
                filtered_data = data

            # Limit results
            if len(filtered_data) > max_results:
                filtered_data = filtered_data[:max_results]
                response.add_trace(f"Limited to {max_results} results")

            response.data = {
                'total_input': len(data),
                'total_filtered': len(filtered_data),
                'filter_applied': filter_criteria is not None,
                'filter_criteria': filter_criteria,
                'max_results': max_results,
                'records': filtered_data
            }

            return response

        except Exception as e:
            response.set_error(f"Error querying data: {str(e)}")
            return response

    def _apply_filters(self, data: List[Dict], filter_criteria: Dict[str, Any]) -> List[Dict]:
        """
        Apply filter criteria to data.

        Args:
            data: List of dictionaries
            filter_criteria: Filter dictionary

        Returns:
            Filtered list
        """
        filtered = []

        for record in data:
            match = True
            for key, value in filter_criteria.items():
                # Handle special operators
                if isinstance(value, dict) and '$gt' in value:
                    if key not in record or not (record[key] > value['$gt']):
                        match = False
                        break
                elif isinstance(value, dict) and '$lt' in value:
                    if key not in record or not (record[key] < value['$lt']):
                        match = False
                        break
                elif isinstance(value, dict) and '$in' in value:
                    if key not in record or record[key] not in value['$in']:
                        match = False
                        break
                # Exact match
                elif key not in record or record[key] != value:
                    match = False
                    break

            if match:
                filtered.append(record)

        return filtered

    # ===== Statistical Analysis =====

    @read_only
    @cached(ttl=300)
    def analyze_field(self, data: List[Dict], field_name: str) -> MCPResponse:
        """
        Perform statistical analysis on a field.

        Safe read-only operation. Results cached for 5 minutes.

        Args:
            data: List of dictionaries
            field_name: Field to analyze

        Returns:
            MCPResponse with field statistics
        """
        response = self._create_response()
        response.add_trace(f"Analyzing field: {field_name}")

        try:
            # Extract field values
            values = []
            for record in data:
                if field_name in record and record[field_name] is not None:
                    values.append(record[field_name])

            if not values:
                response.set_error(f"No values found for field: {field_name}")
                return response

            response.add_trace(f"Found {len(values)} values")

            # Determine value type and calculate statistics
            stats = self._calculate_statistics(values)
            response.add_trace(f"Statistics calculated: {stats.get('type', 'unknown')} type")

            response.data = {
                'field_name': field_name,
                'value_count': len(values),
                'statistics': stats
            }

            return response

        except Exception as e:
            response.set_error(f"Error analyzing field: {str(e)}")
            return response

    def _calculate_statistics(self, values: List[Any]) -> Dict[str, Any]:
        """
        Calculate statistics for values.

        Args:
            values: List of values

        Returns:
            Statistics dictionary
        """
        stats = {
            'count': len(values)
        }

        try:
            # Try numeric analysis
            numeric_values = [float(v) for v in values if v is not None]
            if numeric_values:
                stats['type'] = 'numeric'
                stats['min'] = min(numeric_values)
                stats['max'] = max(numeric_values)
                stats['mean'] = sum(numeric_values) / len(numeric_values)
                stats['sum'] = sum(numeric_values)

                # Calculate median
                sorted_values = sorted(numeric_values)
                mid = len(sorted_values) // 2
                if len(sorted_values) % 2 == 0:
                    stats['median'] = (sorted_values[mid - 1] + sorted_values[mid]) / 2
                else:
                    stats['median'] = sorted_values[mid]

                # Calculate standard deviation
                mean = stats['mean']
                variance = sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
                stats['std_dev'] = variance ** 0.5

        except (ValueError, TypeError):
            # Categorical analysis
            stats['type'] = 'categorical'
            unique_values = set(str(v) for v in values)
            stats['unique_count'] = len(unique_values)
            stats['sample_values'] = list(unique_values)[:10]

            # Value counts
            from collections import Counter
            value_counts = Counter(str(v) for v in values)
            stats['most_common'] = [
                {'value': v, 'count': c}
                for v, c in value_counts.most_common(5)
            ]

        return stats

    # ===== Aggregation =====

    @read_only
    def aggregate_data(self, data: List[Dict], group_by: str,
                      aggregate_fields: Dict[str, str]) -> MCPResponse:
        """
        Aggregate data by grouping field.

        Safe read-only operation.

        Args:
            data: List of dictionaries
            group_by: Field to group by
            aggregate_fields: Dict of {field: operation} pairs
                             Operations: 'sum', 'avg', 'count', 'min', 'max'

        Returns:
            MCPResponse with aggregated data
        """
        response = self._create_response()
        response.add_trace(f"Aggregating by: {group_by}")

        try:
            # Group data
            groups = self._group_data(data, group_by)
            response.add_trace(f"Found {len(groups)} groups")

            # Calculate aggregations
            results = []
            for group_value, records in groups.items():
                result = {group_by: group_value}

                for field, operation in aggregate_fields.items():
                    agg_value = self._calculate_aggregate(records, field, operation)
                    result[f"{field}_{operation}"] = agg_value

                results.append(result)

            response.add_trace(f"Aggregation complete: {len(results)} results")

            response.data = {
                'group_by': group_by,
                'aggregate_fields': aggregate_fields,
                'group_count': len(results),
                'results': results
            }

            return response

        except Exception as e:
            response.set_error(f"Error aggregating data: {str(e)}")
            return response

    def _group_data(self, data: List[Dict], group_by: str) -> Dict[Any, List[Dict]]:
        """
        Group data by field.

        Args:
            data: List of dictionaries
            group_by: Field to group by

        Returns:
            Dictionary of groups
        """
        groups = {}

        for record in data:
            if group_by in record:
                group_value = record[group_by]
                if group_value not in groups:
                    groups[group_value] = []
                groups[group_value].append(record)

        return groups

    def _calculate_aggregate(self, records: List[Dict], field: str, operation: str) -> Any:
        """
        Calculate aggregate value.

        Args:
            records: List of records
            field: Field to aggregate
            operation: Aggregation operation

        Returns:
            Aggregated value
        """
        # Extract values
        values = [r[field] for r in records if field in r and r[field] is not None]

        if not values:
            return None

        operation = operation.lower()

        if operation == 'count':
            return len(values)
        elif operation == 'sum':
            return sum(float(v) for v in values)
        elif operation == 'avg':
            return sum(float(v) for v in values) / len(values)
        elif operation == 'min':
            return min(values)
        elif operation == 'max':
            return max(values)
        else:
            return None

    # ===== Data Transformation =====

    @read_only
    def transform_data(self, data: List[Dict], transformations: Dict[str, str]) -> MCPResponse:
        """
        Transform data fields.

        Safe read-only operation that applies transformations without modifying original data.

        Args:
            data: List of dictionaries
            transformations: Dict of {new_field: expression} pairs
                           Expressions can use existing fields

        Returns:
            MCPResponse with transformed data
        """
        response = self._create_response()
        response.add_trace(f"Applying {len(transformations)} transformations")

        try:
            transformed_data = []

            for record in data:
                new_record = record.copy()

                for new_field, expression in transformations.items():
                    try:
                        # Simple expression evaluation (limited for safety)
                        # In production, use a safer expression evaluator
                        value = self._evaluate_expression(expression, record)
                        new_record[new_field] = value
                    except Exception as e:
                        new_record[new_field] = None
                        new_record[f"{new_field}_error"] = str(e)

                transformed_data.append(new_record)

            response.add_trace(f"Transformed {len(transformed_data)} records")

            response.data = {
                'transformations_applied': transformations,
                'record_count': len(transformed_data),
                'records': transformed_data
            }

            return response

        except Exception as e:
            response.set_error(f"Error transforming data: {str(e)}")
            return response

    def _evaluate_expression(self, expression: str, record: Dict[str, Any]) -> Any:
        """
        Evaluate expression safely (simplified implementation).

        Args:
            expression: Expression string
            record: Record dictionary

        Returns:
            Evaluated value
        """
        # This is a simplified implementation
        # In production, use a proper expression evaluator with safety restrictions

        # Simple field reference
        if expression in record:
            return record[expression]

        # Simple arithmetic (very limited)
        try:
            # Replace field names with values
            eval_expr = expression
            for key, value in record.items():
                if key in eval_expr:
                    eval_expr = eval_expr.replace(key, str(value))

            # Evaluate (UNSAFE - should use safer alternative in production)
            # result = eval(eval_expr)
            # For now, return the expression as-is
            return eval_expr
        except:
            return None

    # ===== Export Operations =====

    @write_safe
    def export_to_json(self, data: List[Dict], output_path: str,
                      pretty: bool = True) -> MCPResponse:
        """
        Export data to JSON file.

        This is a write operation that creates a file.
        Requires user confirmation in interactive mode.

        Args:
            data: Data to export
            output_path: Output file path
            pretty: Use pretty formatting

        Returns:
            MCPResponse with export results
        """
        response = self._create_response()
        response.add_trace(f"Exporting to JSON: {output_path}")

        try:
            output_file = Path(output_path)

            # Ensure directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)

            response.add_trace(f"Exported {len(data)} records")

            response.data = {
                'output_path': str(output_file),
                'record_count': len(data),
                'pretty_format': pretty,
                'message': f"Data exported to {output_file.name}"
            }

            return response

        except Exception as e:
            response.set_error(f"Error exporting to JSON: {str(e)}")
            return response

    @write_safe
    def export_to_csv(self, data: List[Dict], output_path: str,
                     fields: Optional[List[str]] = None) -> MCPResponse:
        """
        Export data to CSV file.

        This is a write operation that creates a file.
        Requires user confirmation in interactive mode.

        Args:
            data: Data to export
            output_path: Output file path
            fields: Optional list of fields to export (all if None)

        Returns:
            MCPResponse with export results
        """
        response = self._create_response()
        response.add_trace(f"Exporting to CSV: {output_path}")

        try:
            import csv

            output_file = Path(output_path)

            # Ensure directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Determine fields
            if fields is None and data:
                fields = list(data[0].keys())

            response.add_trace(f"Exporting {len(fields)} fields")

            # Write CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for record in data:
                    # Filter to selected fields
                    filtered_record = {k: v for k, v in record.items() if k in fields}
                    writer.writerow(filtered_record)

            response.add_trace(f"Exported {len(data)} records")

            response.data = {
                'output_path': str(output_file),
                'record_count': len(data),
                'field_count': len(fields),
                'fields': fields,
                'message': f"Data exported to {output_file.name}"
            }

            return response

        except Exception as e:
            response.set_error(f"Error exporting to CSV: {str(e)}")
            return response

    # ===== Summary Reports =====

    @read_only
    def generate_summary(self, data: List[Dict],
                        fields_to_analyze: Optional[List[str]] = None) -> MCPResponse:
        """
        Generate comprehensive data summary.

        Safe read-only operation.

        Args:
            data: Data to summarize
            fields_to_analyze: Optional list of fields to analyze (all if None)

        Returns:
            MCPResponse with summary report
        """
        response = self._create_response()
        response.add_trace(f"Generating summary for {len(data)} records")

        try:
            # Determine fields
            if fields_to_analyze is None and data:
                fields_to_analyze = list(data[0].keys())

            response.add_trace(f"Analyzing {len(fields_to_analyze)} fields")

            # Generate summary for each field
            field_summaries = {}
            for field in fields_to_analyze:
                analysis_result = self.analyze_field(data, field)
                if analysis_result.success:
                    field_summaries[field] = analysis_result.data.get('statistics', {})

            response.add_trace("Summary generation complete")

            response.data = {
                'record_count': len(data),
                'field_count': len(fields_to_analyze),
                'fields_analyzed': fields_to_analyze,
                'field_summaries': field_summaries
            }

            return response

        except Exception as e:
            response.set_error(f"Error generating summary: {str(e)}")
            return response
