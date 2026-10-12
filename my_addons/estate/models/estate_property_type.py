from odoo import api, fields, models


class EstatePropertyType(models.Model):
    """Danh mục loại bất động sản, ví dụ Apartment hoặc House."""

    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    # sequence hỗ trợ drag handle; số nhỏ đứng trước do _order.
    sequence = fields.Integer(default=10)
    # Hai One2many đều đọc qua inverse fields ở model property/offer.
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="property_type_id",
        string="Properties",
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_type_id",
        string="Offers",
    )
    # Giá trị dùng cho stat button; không cần store vì chỉ hiển thị khi đọc form.
    offer_count = fields.Integer(compute="_compute_offer_count")

    # UNIQUE chạy ở PostgreSQL, tránh race condition tốt hơn kiểm tra search rồi create.
    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "A property type name must be unique.",
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        """Đếm offer liên quan cho từng property type.

        Odoo gọi hàm khi tập ``offer_ids`` thay đổi theo ``@api.depends``. Kết
        quả được dùng bởi stat button Offers trên form Property Type.

        Side effects:
            Gán ``offer_count`` cho mọi record trong ``self``.
        """
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)
