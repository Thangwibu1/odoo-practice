from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import _
from odoo.tools.float_utils import float_compare

from . import constants


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

    def _default_date_availability(self):
        """Trả về ngày có thể giao nhà mặc định cho một property mới.

        Odoo gọi hàm này trong quá trình ``default_get/create`` khi client không
        truyền ``date_availability``. Việc dùng callable có tên giúp ngày được
        tính tại đúng thời điểm tạo record và dễ đọc hơn một ``lambda`` ẩn ngay
        trong khai báo field.

        Returns:
            date: Ngày hiện tại cộng số tháng mặc định trong ``constants``.
        """
        return fields.Date.today() + relativedelta(
            months=constants.DEFAULT_AVAILABILITY_MONTHS
        )

    def _default_salesperson(self):
        """Trả về user đang đăng nhập để làm salesperson mặc định.

        Odoo gọi hàm này khi khởi tạo form/record nếu ``user_id`` chưa được
        truyền. ``self.env.user`` là record ``res.users`` của request hiện tại.

        Returns:
            res.users: User hiện tại trong Odoo Environment.
        """
        return self.env.user

    # ------------------------------------------------------------------
    # Thông tin cơ bản
    # ------------------------------------------------------------------
    # required=True được ORM kiểm tra và tương ứng NOT NULL trong PostgreSQL.
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    # copy=False: Duplicate không mang ngày cũ. Callable có tên được gọi tại
    # thời điểm create, tránh ngày bị cố định từ lúc server import module.
    date_availability = fields.Date(
        copy=False,
        default=_default_date_availability,
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
        selection=constants.GARDEN_ORIENTATION_SELECTION,
    )
    # Reserved field: active=False làm record bị loại khỏi search mặc định
    # (archive) nhưng dữ liệu vẫn tồn tại trong database.
    active = fields.Boolean(default=True)
    # State điều khiển workflow, statusbar và visibility của buttons.
    state = fields.Selection(
        selection=constants.PROPERTY_STATE_SELECTION,
        required=True,
        copy=False,
        default=constants.PROPERTY_STATE_NEW,
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
        default=_default_salesperson,
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

        Odoo gọi lại hàm khi ``living_area`` hoặc ``garden_area`` thay đổi vì
        chúng được khai báo trong ``@api.depends``. Compute method không nhận
        tham số ngoài ``self`` và bắt buộc gán ``total_area`` cho mọi record.

        Side effects:
            Gán field computed ``total_area`` trong cache ORM; field này không
            có ``store=True`` nên không tạo cột lưu kết quả trong PostgreSQL.
        """
        for property_record in self:
            property_record.total_area = (
                property_record.living_area + property_record.garden_area
            )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        """Lấy giá offer lớn nhất hoặc 0 nếu chưa có offer.

        Odoo gọi hàm khi giá của offer liên quan thay đổi. ``mapped("price")``
        biến recordset offer thành danh sách giá; ``default=0.0`` ngăn ``max``
        báo lỗi khi property chưa có offer.

        Side effects:
            Gán field computed ``best_price`` cho từng property trong ``self``.
        """
        for property_record in self:
            property_record.best_price = max(
                property_record.offer_ids.mapped("price"), default=0.0
            )

    @api.onchange("garden")
    def _onchange_garden(self):
        """Gợi ý giá trị garden trên form, không phải business invariant.

        Onchange chạy với pseudo-record khi user sửa form. Nếu bật Garden, form
        được gợi ý diện tích và hướng mặc định; nếu tắt, hai giá trị được xóa.
        Import/RPC có thể không chạy onchange, vì vậy đây chỉ là hỗ trợ nhập liệu
        chứ không phải validation bảo vệ dữ liệu.

        Side effects:
            Chỉ thay đổi giá trị tạm trên form cho đến khi user bấm Save.
        """
        if self.garden:
            self.garden_area = constants.DEFAULT_GARDEN_AREA
            self.garden_orientation = constants.GARDEN_ORIENTATION_NORTH
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        """Chặn giá bán dưới 90% giá kỳ vọng bằng so sánh float an toàn.

        Odoo gọi constraint sau ``create/write`` khi một trong hai field khai báo
        thay đổi. Giá 0 nghĩa là chưa accept offer nên được bỏ qua. So sánh qua
        ``float_compare`` để tránh sai số số thực.

        Raises:
            ValidationError: Nếu giá bán khác 0 nhưng thấp hơn tỷ lệ tối thiểu.
        """
        for property_record in self:
            if not property_record.selling_price:
                continue
            minimum_price = (
                property_record.expected_price
                * constants.MINIMUM_SELLING_PRICE_RATIO
            )
            if float_compare(
                property_record.selling_price,
                minimum_price,
                precision_digits=2,
            ) < 0:
                raise ValidationError(
                    _(
                        "The selling price cannot be lower than "
                        "%(minimum_percentage)s%% of the expected price.",
                        minimum_percentage=(
                            constants.MINIMUM_SELLING_PRICE_PERCENT
                        ),
                    )
                )

    def action_sold(self):
        """Đánh dấu Sold sau khi kiểm tra transition và buyer.

        Button Sold gọi method qua RPC, nhưng module khác cũng có thể gọi trực
        tiếp. Vì vậy mọi kiểm tra phải nằm ở server. Hàm xử lý được nhiều record
        và chỉ bán property đã có buyer từ một offer được chấp nhận.

        Raises:
            UserError: Nếu property đã hủy, đã bán hoặc chưa có buyer.

        Returns:
            bool: ``True`` sau khi toàn bộ record chuyển trạng thái thành công.
        """
        for property_record in self:
            if property_record.state == constants.PROPERTY_STATE_CANCELED:
                raise UserError(_("A canceled property cannot be sold."))
            if property_record.state == constants.PROPERTY_STATE_SOLD:
                raise UserError(_("This property is already sold."))
            if not property_record.buyer_id:
                raise UserError(
                    _("Accept an offer before marking the property as sold.")
                )
            property_record.state = constants.PROPERTY_STATE_SOLD
        return True

    def action_cancel(self):
        """Chuyển các property được chọn sang trạng thái Canceled.

        Hàm được button Cancel gọi bằng RPC. Nó xử lý toàn bộ record trong
        ``self``, từ chối property đã bán và trả ``True`` khi hoàn tất.

        Raises:
            UserError: Nếu một property trong recordset đã ở trạng thái Sold.

        Returns:
            bool: ``True`` để báo action server đã thực thi thành công.
        """
        for property_record in self:
            if property_record.state == constants.PROPERTY_STATE_SOLD:
                raise UserError(_("A sold property cannot be canceled."))
            property_record.state = constants.PROPERTY_STATE_CANCELED
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        """Chỉ cho xóa New/Canceled trong hoạt động bình thường.

        Odoo gọi hook ngay trước ``unlink``. ``at_uninstall=False`` cho phép bỏ
        qua rule khi uninstall module để dữ liệu nghiệp vụ không cản việc gỡ.

        Raises:
            UserError: Nếu có property không ở trạng thái New hoặc Canceled.
        """
        for property_record in self:
            if property_record.state not in constants.PROPERTY_DELETABLE_STATES:
                raise UserError(
                    _("Only new or canceled properties can be deleted.")
                )
