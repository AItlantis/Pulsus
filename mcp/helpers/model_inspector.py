"""
ModelInspector - Class-Based MCP Helper for Model Object Inspection

Provides MCP-compliant methods for:
- Inspecting Aimsun model objects (sections, nodes, centroids, etc.)
- Inspecting QGIS layer objects
- Querying model catalogs
- Extracting object properties

This is a template class that can be extended for specific platform implementations.
"""

from typing import Dict, Any, List, Optional

# MCP Core Framework imports
from agents.mcp.core import (
    MCPBase,
    MCPResponse,
    read_only,
    restricted_write,
    cached,
    get_mcp_logger,
    get_safety_policy
)


class ModelInspector(MCPBase):
    """
    Class-based MCP helper for model object inspection.

    Provides safe, structured methods for:
    - Inspecting Aimsun/QGIS objects
    - Querying catalogs and layers
    - Extracting object properties
    - Filtering and searching objects

    All methods return MCPResponse objects with standardized structure.
    Platform-specific type validation is enforced through decorators.
    """

    def __init__(self, platform='aimsun', logger=None, context=None):
        """
        Initialize ModelInspector.

        Args:
            platform: Platform type ('aimsun' or 'qgis')
            logger: Optional MCPLogger instance
            context: Optional context dict with caller info
        """
        if logger is None:
            logger = get_mcp_logger()

        if context is None:
            context = {'caller': 'ModelInspector'}

        super().__init__(logger=logger, context=context)

        # Set platform
        self.platform = platform.lower()
        if self.platform not in ['aimsun', 'qgis']:
            raise ValueError(f"Unsupported platform: {platform}. Must be 'aimsun' or 'qgis'")

        # Register with safety policy
        policy = get_safety_policy()
        policy.register_operation('get_object_properties', 'read_only')
        policy.register_operation('query_catalog', 'read_only')
        policy.register_operation('list_objects', 'read_only')

    # ===== Object Inspection =====

    @read_only
    def get_object_properties(self, obj: Any) -> MCPResponse:
        """
        Get properties of a model object.

        Safe read-only operation that extracts:
        - Object ID and name
        - Object type
        - All public properties
        - Object state

        Args:
            obj: Model object (Aimsun GK* or QGIS Qgs*)

        Returns:
            MCPResponse with object properties
        """
        response = self._create_response()
        response.add_trace(f"Inspecting object: {type(obj).__name__}")

        try:
            # Validate object type
            policy = get_safety_policy()
            is_safe, error = policy.check_type_safety(obj, platform=self.platform)

            if not is_safe:
                response.set_error(f"Type validation failed: {error}")
                return response

            response.add_trace("Object type validated")

            # Extract properties based on platform
            if self.platform == 'aimsun':
                properties = self._extract_aimsun_properties(obj)
            elif self.platform == 'qgis':
                properties = self._extract_qgis_properties(obj)
            else:
                response.set_error(f"Unsupported platform: {self.platform}")
                return response

            response.add_trace(f"Extracted {len(properties)} properties")

            response.data = {
                'object_type': type(obj).__name__,
                'platform': self.platform,
                'properties': properties
            }

            return response

        except Exception as e:
            response.set_error(f"Error inspecting object: {str(e)}")
            return response

    def _extract_aimsun_properties(self, obj: Any) -> Dict[str, Any]:
        """
        Extract properties from Aimsun object.

        Args:
            obj: Aimsun GK* object

        Returns:
            Dictionary of properties
        """
        properties = {}

        try:
            # Common Aimsun object properties
            if hasattr(obj, 'getId'):
                properties['id'] = obj.getId()
            if hasattr(obj, 'getName'):
                properties['name'] = obj.getName()
            if hasattr(obj, 'getTypeName'):
                properties['type_name'] = obj.getTypeName()

            # Section-specific properties
            if type(obj).__name__ == 'GKSection':
                if hasattr(obj, 'getSpeed'):
                    properties['speed'] = obj.getSpeed()
                if hasattr(obj, 'getCapacity'):
                    properties['capacity'] = obj.getCapacity()
                if hasattr(obj, 'getLength'):
                    properties['length'] = obj.getLength()

            # Node-specific properties
            elif type(obj).__name__ == 'GKNode':
                if hasattr(obj, 'getPosition'):
                    pos = obj.getPosition()
                    properties['position'] = {'x': pos.x, 'y': pos.y} if pos else None

            # Generic property extraction
            for attr in dir(obj):
                if attr.startswith('get') and not attr.startswith('__'):
                    try:
                        method = getattr(obj, attr)
                        if callable(method) and method.__code__.co_argcount == 1:  # Only self
                            value = method()
                            properties[attr.replace('get', '', 1).lower()] = str(value)
                    except:
                        pass

        except Exception as e:
            properties['_error'] = str(e)

        return properties

    def _extract_qgis_properties(self, obj: Any) -> Dict[str, Any]:
        """
        Extract properties from QGIS object.

        Args:
            obj: QGIS Qgs* object

        Returns:
            Dictionary of properties
        """
        properties = {}

        try:
            # QgsVectorLayer properties
            if type(obj).__name__ == 'QgsVectorLayer':
                if hasattr(obj, 'name'):
                    properties['name'] = obj.name()
                if hasattr(obj, 'featureCount'):
                    properties['feature_count'] = obj.featureCount()
                if hasattr(obj, 'crs'):
                    properties['crs'] = str(obj.crs().authid())
                if hasattr(obj, 'geometryType'):
                    properties['geometry_type'] = obj.geometryType()

            # QgsFeature properties
            elif type(obj).__name__ == 'QgsFeature':
                if hasattr(obj, 'id'):
                    properties['id'] = obj.id()
                if hasattr(obj, 'attributes'):
                    properties['attributes'] = obj.attributes()
                if hasattr(obj, 'geometry'):
                    geom = obj.geometry()
                    if geom:
                        properties['geometry_type'] = geom.type()
                        properties['geometry_wkt'] = geom.asWkt()[:100]  # First 100 chars

            # Generic property extraction
            for attr in dir(obj):
                if not attr.startswith('_') and not attr.startswith('Q'):
                    try:
                        value = getattr(obj, attr)
                        if not callable(value):
                            properties[attr] = str(value)
                    except:
                        pass

        except Exception as e:
            properties['_error'] = str(e)

        return properties

    # ===== Catalog Queries =====

    @read_only
    @cached(ttl=60)
    def query_catalog(self, catalog: Any, object_type: Optional[str] = None,
                     filter_criteria: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """
        Query model catalog for objects.

        Safe read-only operation. Results cached for 60 seconds.

        Args:
            catalog: Model catalog object
            object_type: Optional type filter (e.g., 'GKSection', 'QgsVectorLayer')
            filter_criteria: Optional filter dictionary

        Returns:
            MCPResponse with matching objects
        """
        response = self._create_response()
        response.add_trace(f"Querying catalog: {type(catalog).__name__}")

        try:
            # Extract all objects from catalog
            objects = self._extract_catalog_objects(catalog, object_type)
            response.add_trace(f"Found {len(objects)} objects")

            # Apply filters if specified
            if filter_criteria:
                objects = self._apply_filters(objects, filter_criteria)
                response.add_trace(f"After filtering: {len(objects)} objects")

            response.data = {
                'catalog_type': type(catalog).__name__,
                'object_type': object_type,
                'filter_applied': filter_criteria is not None,
                'object_count': len(objects),
                'objects': objects
            }

            return response

        except Exception as e:
            response.set_error(f"Error querying catalog: {str(e)}")
            return response

    def _extract_catalog_objects(self, catalog: Any, object_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract objects from catalog.

        Args:
            catalog: Catalog object
            object_type: Optional type filter

        Returns:
            List of object dictionaries
        """
        objects = []

        try:
            # Aimsun catalog
            if self.platform == 'aimsun':
                if hasattr(catalog, 'getObjectsOfType'):
                    # Get all objects of specified type
                    if object_type:
                        obj_list = catalog.getObjectsOfType(object_type)
                    else:
                        # Get all objects (implementation depends on Aimsun API)
                        obj_list = []

                    for obj in obj_list:
                        obj_data = {
                            'id': obj.getId() if hasattr(obj, 'getId') else None,
                            'name': obj.getName() if hasattr(obj, 'getName') else None,
                            'type': type(obj).__name__
                        }
                        objects.append(obj_data)

            # QGIS project
            elif self.platform == 'qgis':
                if hasattr(catalog, 'mapLayers'):
                    layers = catalog.mapLayers()
                    for layer_id, layer in layers.items():
                        if not object_type or type(layer).__name__ == object_type:
                            obj_data = {
                                'id': layer_id,
                                'name': layer.name() if hasattr(layer, 'name') else None,
                                'type': type(layer).__name__
                            }
                            objects.append(obj_data)

        except Exception as e:
            objects.append({'_error': str(e)})

        return objects

    def _apply_filters(self, objects: List[Dict[str, Any]],
                      filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filter criteria to object list.

        Args:
            objects: List of object dictionaries
            filter_criteria: Filter dictionary (key-value pairs)

        Returns:
            Filtered list of objects
        """
        filtered = []

        for obj in objects:
            match = True
            for key, value in filter_criteria.items():
                if key not in obj or obj[key] != value:
                    match = False
                    break
            if match:
                filtered.append(obj)

        return filtered

    # ===== Object Listing =====

    @read_only
    def list_objects(self, container: Any, object_type: Optional[str] = None,
                    max_results: int = 100) -> MCPResponse:
        """
        List objects in a container (folder, layer, group).

        Safe read-only operation.

        Args:
            container: Container object (folder, layer group, etc.)
            object_type: Optional type filter
            max_results: Maximum number of results to return

        Returns:
            MCPResponse with object list
        """
        response = self._create_response()
        response.add_trace(f"Listing objects in: {type(container).__name__}")

        try:
            # Extract objects from container
            objects = self._extract_container_objects(container, object_type)
            response.add_trace(f"Found {len(objects)} objects")

            # Limit results
            if len(objects) > max_results:
                objects = objects[:max_results]
                response.add_trace(f"Limited to {max_results} results")

            response.data = {
                'container_type': type(container).__name__,
                'object_type': object_type,
                'total_found': len(objects),
                'max_results': max_results,
                'objects': objects
            }

            return response

        except Exception as e:
            response.set_error(f"Error listing objects: {str(e)}")
            return response

    def _extract_container_objects(self, container: Any, object_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract objects from container.

        Args:
            container: Container object
            object_type: Optional type filter

        Returns:
            List of object dictionaries
        """
        objects = []

        try:
            # Aimsun folder
            if self.platform == 'aimsun':
                if hasattr(container, 'getContents'):
                    contents = container.getContents()
                    for obj in contents:
                        if not object_type or type(obj).__name__ == object_type:
                            obj_data = {
                                'id': obj.getId() if hasattr(obj, 'getId') else None,
                                'name': obj.getName() if hasattr(obj, 'getName') else None,
                                'type': type(obj).__name__
                            }
                            objects.append(obj_data)

            # QGIS layer group
            elif self.platform == 'qgis':
                if hasattr(container, 'children'):
                    children = container.children()
                    for child in children:
                        if hasattr(child, 'layer'):
                            layer = child.layer()
                            if layer and (not object_type or type(layer).__name__ == object_type):
                                obj_data = {
                                    'id': layer.id() if hasattr(layer, 'id') else None,
                                    'name': layer.name() if hasattr(layer, 'name') else None,
                                    'type': type(layer).__name__
                                }
                                objects.append(obj_data)

        except Exception as e:
            objects.append({'_error': str(e)})

        return objects

    # ===== Search Operations =====

    @read_only
    def search_objects(self, catalog: Any, search_term: str,
                      object_type: Optional[str] = None,
                      search_fields: Optional[List[str]] = None) -> MCPResponse:
        """
        Search for objects by name or properties.

        Safe read-only operation.

        Args:
            catalog: Model catalog object
            search_term: Search string
            object_type: Optional type filter
            search_fields: Optional list of fields to search (default: ['name'])

        Returns:
            MCPResponse with matching objects
        """
        response = self._create_response()
        response.add_trace(f"Searching for: '{search_term}'")

        try:
            if search_fields is None:
                search_fields = ['name']

            # Query catalog
            query_result = self.query_catalog(catalog, object_type)

            if not query_result.success:
                return query_result

            # Filter by search term
            all_objects = query_result.data.get('objects', [])
            matched_objects = []

            search_term_lower = search_term.lower()

            for obj in all_objects:
                match = False
                for field in search_fields:
                    if field in obj:
                        value = str(obj[field]).lower()
                        if search_term_lower in value:
                            match = True
                            break
                if match:
                    matched_objects.append(obj)

            response.add_trace(f"Found {len(matched_objects)} matches")

            response.data = {
                'search_term': search_term,
                'search_fields': search_fields,
                'object_type': object_type,
                'match_count': len(matched_objects),
                'matches': matched_objects
            }

            return response

        except Exception as e:
            response.set_error(f"Error searching objects: {str(e)}")
            return response
