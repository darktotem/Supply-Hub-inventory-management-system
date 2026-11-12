from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE

NAME_MAX = 120
REPORT_MAX = 20000


class TrimmedString(fields.String):
    """A string that has its spaces trimmed before it is checked."""

    def _deserialize(self, value, attr, data, **kwargs):
        return super()._deserialize(value, attr, data, **kwargs).strip()


class CreateReportSchema(Schema):
    """POST /api/reports  (JSON body)"""

    class Meta:
        unknown = EXCLUDE  # ignore any extra fields

    name = TrimmedString(
        required=True,
        validate=validate.Length(min=1, max=NAME_MAX,
                                 error=f"Must be 1-{NAME_MAX} characters"),
    )
    report = TrimmedString(
        required=True,
        validate=validate.Length(min=1, max=REPORT_MAX,
                                 error=f"Must be 1-{REPORT_MAX} characters"),
    )


class ListReportsQuerySchema(Schema):
    """GET /api/reports  (query string: ?search=&page=&per_page=)"""

    class Meta:
        unknown = EXCLUDE

    search = TrimmedString(load_default="",
                           validate=validate.Length(max=NAME_MAX))
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20,
                              validate=validate.Range(min=1, max=100))


class ReportIdSchema(Schema):
    """GET and DELETE /api/reports/<report_id>  (id in the URL)"""

    class Meta:
        unknown = EXCLUDE

    report_id = fields.Integer(required=True, validate=validate.Range(min=1))


create_report_schema = CreateReportSchema()
list_reports_query_schema = ListReportsQuerySchema()
report_id_schema = ReportIdSchema()