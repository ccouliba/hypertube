"""Search domain Marshmallow schemas"""
from marshmallow import Schema, fields, validate, EXCLUDE
from app.services.search import providers_settings

_MAX_PER_PAGE: int = providers_settings["RESULTS_MAX_PER_PAGE"]
_MAX_TOTAL: int = providers_settings["RESULTS_TOTAL_RESULTS"]


class SearchQuerySchema(Schema):
    """Query parameters for the search endpoint"""

    class Meta:
        unknown = EXCLUDE

    query = fields.Str(
        load_default="",
        validate=validate.Length(
            min=0,
            max=100,
            error="Search query must be under 100 characters",
        ),
    )
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="Page must be >= 1"),
    )
    limit = fields.Int(
        load_default=_MAX_PER_PAGE,
        validate=validate.Range(
            min=1,
            max=_MAX_TOTAL,
            error=f"Limit must be between 1 and {_MAX_TOTAL}",
        ),
    )
