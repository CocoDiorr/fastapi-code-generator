
from typing import List, Type, Any, Dict, Tuple
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, load_only, contains_eager, joinedload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.inspection import inspect as sa_inspect

# Import all generated ORM models
from test_output.models import User, Post

# Registry to map model_name strings to classes
MODEL_REGISTRY: Dict[str, Type[Any]] = {
    "User": User,
    "Post": Post
}

# ---------------------
# Flatten include spec into paths, filters, and field maps
# ---------------------
def flatten_includes(
    include_spec: Dict[str, Any],
    prefix: str = ""
) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
    paths: List[str] = []
    filter_map: Dict[str, Dict[str, Any]] = {}
    fields_map: Dict[str, List[str]] = {}
    for rel, cfg in include_spec.items():
        path = rel if not prefix else f"{prefix}.{rel}"
        paths.append(path)
        if 'filters' in cfg and cfg['filters']:
            filter_map[path] = cfg['filters']
        if 'fields' in cfg and cfg['fields']:
            fields_map[path] = cfg['fields']
        if 'include' in cfg and cfg['include']:
            sub_paths, sub_filters, sub_fields = flatten_includes(cfg['include'], prefix=path)
            paths += sub_paths
            filter_map.update(sub_filters)
            fields_map.update(sub_fields)
    return paths, filter_map, fields_map

# ---------------------
# Build query options for eager loading and filtering relationships
# ---------------------
def make_selectin_loaders(
    model: Type[Any],
    include_paths: List[str],
    filter_map: Dict[str, Dict[str, Any]],
    fields_map: Dict[str, List[str]]
) -> List[Any]:
    loaders: List[Any] = []
    for path in include_paths:
        parts = path.split('.')
        rel_name = parts[0]
        attr: InstrumentedAttribute = getattr(model, rel_name)
        prop = sa_inspect(model).all_orm_descriptors.get(rel_name)
        if not prop or not isinstance(prop.property, RelationshipProperty):
            raise ValueError(f"{rel_name} is not a valid relationship on {model.__name__}")
        
        target_cls = prop.property.mapper.class_
        loader = selectinload(attr)
        current_model = target_cls
        
        # project fields if requested
        if path in fields_map:
            field_attrs = [getattr(current_model, f) for f in fields_map[path]]
            loader = loader.load_only(*field_attrs)
        
        # chain nested relationships
        for sub_rel in parts[1:]:
            attr: InstrumentedAttribute = getattr(current_model, sub_rel)
            prop = sa_inspect(current_model).all_orm_descriptors.get(sub_rel)
            if not prop or not isinstance(prop.property, RelationshipProperty):
                raise ValueError(f"{sub_rel} is not a valid relationship on {current_model.__name__}")
            loader = loader.selectinload(attr)
            target_cls = prop.property.mapper.class_
            current_model = target_cls
            
            # Handle nested field selection
            sub_path = f"{path}.{sub_rel}"
            if sub_path in fields_map:
                field_attrs = [getattr(current_model, f) for f in fields_map[sub_path]]
                loader = loader.load_only(*field_attrs)
        
        loaders.append(loader)
    return loaders

# ---------------------
# Main query function
# ---------------------
def query_with_include(
    session: Any,
    model: Type[Any],
    filters: Dict[str, Any] = None,
    fields: List[str] = None,
    include_spec: Dict[str, Any] = None
) -> List[Any]:
    # Start with base query
    stmt = select(model)

    # Handle root level filters
    root_conditions = []
    if filters:
        root_conditions.extend(getattr(model, k) == v for k, v in filters.items())

    # Process includes and nested filters
    if include_spec:
        include_paths, filter_map, fields_map = flatten_includes(include_spec)
        
        # Add eager loading options with nested relationships
        loaders = make_selectin_loaders(model, include_paths, filter_map, fields_map)
        stmt = stmt.options(*loaders)
        
        # Add relationship joins and filters
        for path, rel_filters in filter_map.items():
            parts = path.split('.')
            current_model = model
            for part in parts:
                attr = getattr(current_model, part)
                stmt = stmt.join(attr)
                current_model = attr.property.mapper.class_
            
            # Apply filters on the joined model
            conditions = [getattr(current_model, k) == v for k, v in rel_filters.items()]
            if conditions:
                stmt = stmt.filter(and_(*conditions))

    # Apply root level conditions
    if root_conditions:
        stmt = stmt.filter(and_(*root_conditions))

    # Apply field selection if requested
    if fields:
        field_attrs = [getattr(model, f) for f in fields]
        stmt = stmt.options(load_only(*field_attrs))

    result = session.execute(stmt)
    return result.scalars().all()