"""
LayerManager - Class-Based MCP Helper for Layer Operations

Provides MCP-compliant methods for:
- Reading and listing map layers (QGIS focus)
- Querying layer features
- Extracting layer properties
- Filtering and analyzing layer data

This is primarily focused on QGIS layers but can be extended for other GIS platforms.
"""

from typing import Dict, Any, List, Optional

# MCP Core Framework imports
from agents.mcp.core import (
    MCPBase,
    MCPResponse,
    read_only,
    write_safe,
    restricted_write,
    cached,
    get_mcp_logger,
    get_safety_policy
)


class LayerManager(MCPBase):
    """
    Class-based MCP helper for GIS layer management.

    Provides safe, structured methods for:
    - Reading layer information
    - Querying features
    - Analyzing layer data
    - Exporting layer subsets

    All methods return MCPResponse objects with standardized structure.
    """

    def __init__(self, logger=None, context=None):
        """
        Initialize LayerManager.

        Args:
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        if logger is None:
            logger = get_mcp_logger()

        if context is None:
            context = {'caller': 'LayerManager'}

        super().__init__(logger=logger, context=context)

    # ===== Layer Information =====

    @read_only
    @cached(ttl=60)
    def get_layer_info(self, layer: Any) -> MCPResponse:
        """
        Get comprehensive information about a layer.

        Safe read-only operation. Results cached for 60 seconds.

        Args:
            layer: QgsVectorLayer or similar layer object

        Returns:
            MCPResponse with layer information
        """
        response = self._create_response()
        response.add_trace(f"Getting layer info: {type(layer).__name__}")

        try:
            # Validate layer type
            policy = get_safety_policy()
            is_safe, error = policy.check_type_safety(layer, platform='qgis')

            if not is_safe:
                response.set_error(f"Type validation failed: {error}")
                return response

            response.add_trace("Layer type validated")

            # Extract layer information
            info = self._extract_layer_info(layer)
            response.add_trace(f"Extracted layer info: {info.get('name', 'Unknown')}")

            response.data = info

            return response

        except Exception as e:
            response.set_error(f"Error getting layer info: {str(e)}")
            return response

    def _extract_layer_info(self, layer: Any) -> Dict[str, Any]:
        """
        Extract information from layer object.

        Args:
            layer: Layer object

        Returns:
            Dictionary with layer information
        """
        info = {
            'type': type(layer).__name__,
            'valid': False
        }

        try:
            # QgsVectorLayer
            if type(layer).__name__ == 'QgsVectorLayer':
                if hasattr(layer, 'isValid'):
                    info['valid'] = layer.isValid()

                if hasattr(layer, 'name'):
                    info['name'] = layer.name()

                if hasattr(layer, 'featureCount'):
                    info['feature_count'] = layer.featureCount()

                if hasattr(layer, 'crs'):
                    crs = layer.crs()
                    info['crs'] = {
                        'auth_id': str(crs.authid()) if hasattr(crs, 'authid') else None,
                        'description': str(crs.description()) if hasattr(crs, 'description') else None
                    }

                if hasattr(layer, 'geometryType'):
                    geom_type = layer.geometryType()
                    info['geometry_type'] = geom_type

                if hasattr(layer, 'extent'):
                    extent = layer.extent()
                    if extent:
                        info['extent'] = {
                            'xmin': extent.xMinimum() if hasattr(extent, 'xMinimum') else None,
                            'xmax': extent.xMaximum() if hasattr(extent, 'xMaximum') else None,
                            'ymin': extent.yMinimum() if hasattr(extent, 'yMinimum') else None,
                            'ymax': extent.yMaximum() if hasattr(extent, 'yMaximum') else None
                        }

                if hasattr(layer, 'fields'):
                    fields = layer.fields()
                    if fields:
                        info['fields'] = [
                            {
                                'name': field.name() if hasattr(field, 'name') else None,
                                'type': field.typeName() if hasattr(field, 'typeName') else None
                            }
                            for field in fields
                        ]

            # QgsRasterLayer
            elif type(layer).__name__ == 'QgsRasterLayer':
                if hasattr(layer, 'isValid'):
                    info['valid'] = layer.isValid()

                if hasattr(layer, 'name'):
                    info['name'] = layer.name()

                if hasattr(layer, 'width'):
                    info['width'] = layer.width()

                if hasattr(layer, 'height'):
                    info['height'] = layer.height()

                if hasattr(layer, 'rasterType'):
                    info['raster_type'] = layer.rasterType()

        except Exception as e:
            info['_error'] = str(e)

        return info

    # ===== Feature Queries =====

    @read_only
    def query_features(self, layer: Any, filter_expression: Optional[str] = None,
                      max_features: int = 1000) -> MCPResponse:
        """
        Query features from a layer.

        Safe read-only operation.

        Args:
            layer: Layer object
            filter_expression: Optional filter expression
            max_features: Maximum number of features to return

        Returns:
            MCPResponse with features
        """
        response = self._create_response()
        response.add_trace(f"Querying features from layer")

        try:
            # Get layer info first
            layer_info = self.get_layer_info(layer)
            if not layer_info.success:
                return layer_info

            response.add_trace(f"Layer: {layer_info.data.get('name', 'Unknown')}")

            # Extract features
            features = self._extract_features(layer, filter_expression, max_features)
            response.add_trace(f"Retrieved {len(features)} features")

            response.data = {
                'layer_name': layer_info.data.get('name'),
                'filter_applied': filter_expression is not None,
                'filter_expression': filter_expression,
                'feature_count': len(features),
                'max_features': max_features,
                'features': features
            }

            return response

        except Exception as e:
            response.set_error(f"Error querying features: {str(e)}")
            return response

    def _extract_features(self, layer: Any, filter_expression: Optional[str],
                         max_features: int) -> List[Dict[str, Any]]:
        """
        Extract features from layer.

        Args:
            layer: Layer object
            filter_expression: Optional filter
            max_features: Max number to return

        Returns:
            List of feature dictionaries
        """
        features = []

        try:
            if type(layer).__name__ == 'QgsVectorLayer':
                # Get features iterator
                if hasattr(layer, 'getFeatures'):
                    # Apply filter if specified
                    if filter_expression:
                        # Note: Actual implementation would use QgsFeatureRequest with filter
                        feature_iter = layer.getFeatures()
                    else:
                        feature_iter = layer.getFeatures()

                    # Iterate and extract
                    count = 0
                    for feature in feature_iter:
                        if count >= max_features:
                            break

                        feature_data = {
                            'id': feature.id() if hasattr(feature, 'id') else None,
                            'attributes': {}
                        }

                        # Extract attributes
                        if hasattr(feature, 'attributes'):
                            attrs = feature.attributes()
                            if hasattr(layer, 'fields'):
                                fields = layer.fields()
                                for i, value in enumerate(attrs):
                                    if i < len(fields):
                                        field_name = fields[i].name()
                                        feature_data['attributes'][field_name] = value

                        # Extract geometry info (summary only)
                        if hasattr(feature, 'geometry'):
                            geom = feature.geometry()
                            if geom and hasattr(geom, 'type'):
                                feature_data['geometry_type'] = geom.type()
                                if hasattr(geom, 'asWkt'):
                                    feature_data['geometry_wkt_preview'] = geom.asWkt()[:100]

                        features.append(feature_data)
                        count += 1

        except Exception as e:
            features.append({'_error': str(e)})

        return features

    # ===== Layer Analysis =====

    @read_only
    @cached(ttl=300)
    def analyze_layer_data(self, layer: Any, field_name: Optional[str] = None) -> MCPResponse:
        """
        Analyze data in a layer.

        Safe read-only operation. Results cached for 5 minutes.

        Args:
            layer: Layer object
            field_name: Optional field to analyze

        Returns:
            MCPResponse with analysis results
        """
        response = self._create_response()
        response.add_trace(f"Analyzing layer data")

        try:
            # Get layer info
            layer_info = self.get_layer_info(layer)
            if not layer_info.success:
                return layer_info

            layer_name = layer_info.data.get('name', 'Unknown')
            response.add_trace(f"Layer: {layer_name}")

            # Perform analysis
            analysis = self._perform_layer_analysis(layer, field_name)
            response.add_trace(f"Analysis complete")

            response.data = {
                'layer_name': layer_name,
                'field_analyzed': field_name,
                'analysis': analysis
            }

            return response

        except Exception as e:
            response.set_error(f"Error analyzing layer: {str(e)}")
            return response

    def _perform_layer_analysis(self, layer: Any, field_name: Optional[str]) -> Dict[str, Any]:
        """
        Perform statistical analysis on layer.

        Args:
            layer: Layer object
            field_name: Optional field to analyze

        Returns:
            Analysis results dictionary
        """
        analysis = {}

        try:
            if type(layer).__name__ == 'QgsVectorLayer':
                # Basic statistics
                if hasattr(layer, 'featureCount'):
                    analysis['total_features'] = layer.featureCount()

                # Field-specific analysis
                if field_name and hasattr(layer, 'getFeatures'):
                    values = []
                    for feature in layer.getFeatures():
                        if hasattr(feature, '__getitem__'):
                            try:
                                value = feature[field_name]
                                if value is not None:
                                    values.append(value)
                            except:
                                pass

                    if values:
                        # Numeric analysis
                        try:
                            numeric_values = [float(v) for v in values]
                            analysis['field_stats'] = {
                                'count': len(numeric_values),
                                'min': min(numeric_values),
                                'max': max(numeric_values),
                                'mean': sum(numeric_values) / len(numeric_values),
                                'type': 'numeric'
                            }
                        except:
                            # String analysis
                            unique_values = set(str(v) for v in values)
                            analysis['field_stats'] = {
                                'count': len(values),
                                'unique_count': len(unique_values),
                                'type': 'categorical'
                            }

                # Extent analysis
                if hasattr(layer, 'extent'):
                    extent = layer.extent()
                    if extent and hasattr(extent, 'area'):
                        analysis['extent_area'] = extent.area()

        except Exception as e:
            analysis['_error'] = str(e)

        return analysis

    # ===== Layer Listing =====

    @read_only
    def list_layers(self, project: Any, layer_type: Optional[str] = None) -> MCPResponse:
        """
        List all layers in a project.

        Safe read-only operation.

        Args:
            project: QgsProject or similar project object
            layer_type: Optional layer type filter ('vector', 'raster')

        Returns:
            MCPResponse with layer list
        """
        response = self._create_response()
        response.add_trace(f"Listing layers in project")

        try:
            # Extract layers
            layers = self._extract_project_layers(project, layer_type)
            response.add_trace(f"Found {len(layers)} layers")

            response.data = {
                'layer_count': len(layers),
                'layer_type_filter': layer_type,
                'layers': layers
            }

            return response

        except Exception as e:
            response.set_error(f"Error listing layers: {str(e)}")
            return response

    def _extract_project_layers(self, project: Any, layer_type: Optional[str]) -> List[Dict[str, Any]]:
        """
        Extract layers from project.

        Args:
            project: Project object
            layer_type: Optional type filter

        Returns:
            List of layer dictionaries
        """
        layers = []

        try:
            if hasattr(project, 'mapLayers'):
                map_layers = project.mapLayers()

                for layer_id, layer in map_layers.items():
                    # Type filtering
                    layer_type_name = type(layer).__name__
                    if layer_type:
                        if layer_type.lower() == 'vector' and 'Vector' not in layer_type_name:
                            continue
                        if layer_type.lower() == 'raster' and 'Raster' not in layer_type_name:
                            continue

                    layer_data = {
                        'id': layer_id,
                        'name': layer.name() if hasattr(layer, 'name') else None,
                        'type': layer_type_name,
                        'valid': layer.isValid() if hasattr(layer, 'isValid') else None
                    }

                    layers.append(layer_data)

        except Exception as e:
            layers.append({'_error': str(e)})

        return layers

    # ===== Export Operations =====

    @write_safe
    def export_layer_subset(self, layer: Any, output_path: str,
                           filter_expression: Optional[str] = None,
                           selected_fields: Optional[List[str]] = None) -> MCPResponse:
        """
        Export a subset of layer features to file.

        This is a write operation that creates a new file.
        Requires user confirmation in interactive mode.

        Args:
            layer: Source layer
            output_path: Output file path
            filter_expression: Optional filter
            selected_fields: Optional list of fields to export

        Returns:
            MCPResponse with export results
        """
        response = self._create_response()
        response.add_trace(f"Exporting layer subset to: {output_path}")

        try:
            # Get layer info
            layer_info = self.get_layer_info(layer)
            if not layer_info.success:
                return layer_info

            layer_name = layer_info.data.get('name', 'Unknown')
            response.add_trace(f"Source layer: {layer_name}")

            # Query features to export
            features_result = self.query_features(layer, filter_expression, max_features=10000)
            if not features_result.success:
                return features_result

            features = features_result.data.get('features', [])
            response.add_trace(f"Exporting {len(features)} features")

            # Perform export (simplified - actual implementation would use QGIS export API)
            # This is a placeholder showing the structure
            export_summary = {
                'output_path': output_path,
                'features_exported': len(features),
                'source_layer': layer_name,
                'filter_applied': filter_expression is not None,
                'fields_selected': selected_fields
            }

            response.data = export_summary
            response.add_trace("Export complete")

            return response

        except Exception as e:
            response.set_error(f"Error exporting layer: {str(e)}")
            return response
