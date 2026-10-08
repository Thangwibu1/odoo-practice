from odoo import fields, models


class ResUsers(models.Model):
    """Mở rộng user chuẩn bằng danh sách property phụ trách.

    Chỉ có _inherit và không có _name, nên class này mở rộng cùng model/table
    ``res.users`` thay vì tạo một model mới.
    """

    _inherit = "res.users"

    # Inverse của estate.property.user_id. Domain chỉ ảnh hưởng những property
    # được chọn/hiển thị qua field này, không phải một record rule bảo mật.
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="user_id",
        string="Real Estate Properties",
        domain=[("state", "in", ["new", "offer_received"])],
    )
