from llama_index.core.vector_stores.types import (
    MetadataFilter, 
    MetadataFilters,
    FilterOperator, 
    FilterCondition)
filters = MetadataFilters(
    filters=[
        MetadataFilter(
            key="department",
            value="Procurement"
        ),
        MetadataFilter(
            key="security_classification",
            value="<user_clearance_level>",
            operator=FilterOperator.LTE
        ),
    ],
    condition=FilterCondition.AND
)
