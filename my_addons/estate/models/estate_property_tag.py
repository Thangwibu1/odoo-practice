from odoo import fields, models


class EstatePropertyTag(models.Model):
    """Nhãn màu gắn Many2many lên property để phân loại mềm."""

    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    # Widget many2many_tags/color_picker diễn giải integer này thành palette màu.
    color = fields.Integer()

    # Tên tag unique giúp tránh hai tag nhìn giống nhau trong giao diện.
    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "A property tag name must be unique.",
    )
