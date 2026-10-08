from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import _
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    """Model trung tâm quản lý tin đăng và vòng đời của bất động sản.

    ``self`` trong Odoo luôn là recordset 0..n record, không mặc định là một
    object đơn. Vì vậy compute, constraint và action phải xử lý nhiều record.
    """

    # Tên kỹ thuật ORM/RPC; mặc định ánh xạ sang table ``estate_property``.
    _name = "estate.property"
    # Nhãn dễ đọc dùng trong metadata/log và màn hình kỹ thuật.
    _description = "Real Estate Property"
    # Search không truyền order sẽ đưa property mới nhất lên trước.
    _order = "id desc"

    # ------------------------------------------------------------------
    # Thông tin cơ bản
    # ------------------------------------------------------------------
    # required=True được ORM kiểm tra và tương ứng NOT NULL trong PostgreSQL.
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    # copy=False: Duplicate không mang ngày cũ. Callable default được gọi tại
    # thời điểm create, tránh ngày bị cố định từ lúc server import module.
    date_availability = fields.Date(
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3),
    )
    expected_price = fields.Float(required=True)
    # User không nhập trực tiếp; Accept Offer sẽ ghi selling_price bằng ORM.
    # readonly là UX, còn invariant thật nằm trong action/constraint server.
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    # PostgreSQL lưu key (north...), còn label (North...) dành cho giao diện.
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )
    # Reserved field: active=False làm record bị loại khỏi search mặc định
    # (archive) nhưng dữ liệu vẫn tồn tại trong database.
    active = fields.Boolean(default=True)
    # State điều khiển workflow, statusbar và visibility của buttons.
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    # ------------------------------------------------------------------
    # Quan hệ giữa các model
    # ------------------------------------------------------------------
    # Many2one lưu foreign key trên table estate_property.
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
    )
    # Many2many được ORM lưu trong relation table trung gian.
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag",
        string="Tags",
    )
    # One2many là quan hệ ảo đọc qua inverse offer.property_id; nó không tạo
    # một column danh sách ID trên table estate_property.
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Offers",
    )
    # Environment cung cấp user đang đăng nhập làm salesperson mặc định.
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
    )
    # Buyer chỉ có sau khi accept offer và không được copy sang tin mới.
    buyer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        copy=False,
    )

    # Computed fields không store: ORM tính khi đọc và cache trong Environment.
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    # ------------------------------------------------------------------
    # SQL constraints của Odoo 19
    # ------------------------------------------------------------------
    # Chạy tại PostgreSQL nên bảo vệ mọi đường ghi: UI, RPC, import và code.
    _expected_price_positive = models.Constraint(
        "CHECK(expected_price > 0)",
        "The expected price must be strictly positive.",
    )
    _selling_price_positive = models.Constraint(
        "CHECK(selling_price >= 0)",
        "The selling price must be positive.",
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        """Tính living area + garden area cho từng record.

        @api.depends giúp ORM biết khi nào cần invalidate cache/recompute. Compute
        luôn phải gán giá trị cho tất cả record trong self.
        """
        for property_record in self:
            property_record.total_area = (
                property_record.living_area + property_record.garden_area
            )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        """Lấy giá offer lớn nhất hoặc 0 nếu chưa có offer.

        ``mapped`` lấy field price trên toàn recordset; default tránh max() báo
        lỗi khi danh sách rỗng.
        """
        for property_record in self:
            property_record.best_price = max(
                property_record.offer_ids.mapped("price"), default=0.0
            )

    @api.onchange("garden")
    def _onchange_garden(self):
        """Gợi ý giá trị garden trên form, không phải business invariant.

        Onchange chạy với pseudo-record khi user sửa form; import/RPC có thể
        không chạy nó, vì vậy không đặt validation quan trọng tại đây.
        """
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        """Chặn giá bán dưới 90% giá kỳ vọng bằng so sánh float an toàn.

        Giá 0 nghĩa là chưa accept offer nên được bỏ qua. Khai báo cả hai field
        giúp constraint chạy khi bất kỳ vế nào thay đổi.
        """
        for property_record in self:
            if not property_record.selling_price:
                continue
            minimum_price = property_record.expected_price * 0.9
            if float_compare(
                property_record.selling_price,
                minimum_price,
                precision_digits=2,
            ) < 0:
                raise ValidationError(
                    _("The selling price cannot be lower than 90% of the expected price.")
                )

    def action_sold(self):
        """Đánh dấu Sold sau khi kiểm tra transition và buyer.

        Button chỉ là một client của method này. Checks vẫn phải ở server vì
        RPC hoặc module khác có thể gọi method mà không đi qua button.
        """
        for property_record in self:
            if property_record.state == "canceled":
                raise UserError(_("A canceled property cannot be sold."))
            if property_record.state == "sold":
                raise UserError(_("This property is already sold."))
            if not property_record.buyer_id:
                raise UserError(_("Accept an offer before marking the property as sold."))
            property_record.state = "sold"
        return True

    def action_cancel(self):
        """Hủy các property chưa Sold; hỗ trợ recordset nhiều record."""
        for property_record in self:
            if property_record.state == "sold":
                raise UserError(_("A sold property cannot be canceled."))
            property_record.state = "canceled"
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        """Chỉ cho xóa New/Canceled trong hoạt động bình thường.

        at_uninstall=False cho phép Odoo bỏ qua rule khi uninstall module, tránh
        business data cản việc gỡ module.
        """
        for property_record in self:
            if property_record.state not in ("new", "canceled"):
                raise UserError(
                    _("Only new or canceled properties can be deleted.")
                )
