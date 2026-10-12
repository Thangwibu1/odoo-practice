from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import _
from odoo.tools.float_utils import float_compare

from . import constants


class EstatePropertyOffer(models.Model):
    """Một đề nghị mua dành cho một property và một partner cụ thể."""

    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    # Giá cao nhất đứng đầu trong list/recordset mặc định.
    _order = "price desc"

    # Giá là required ở ORM và còn được bảo vệ > 0 bởi SQL constraint phía dưới.
    price = fields.Float(required=True)
    # False nghĩa là offer chưa xử lý; accepted/refused là trạng thái cuối.
    status = fields.Selection(
        selection=constants.OFFER_STATUS_SELECTION,
        copy=False,
    )
    # Người đưa ra offer. res.partner dùng chung cho cá nhân/doanh nghiệp.
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
    )
    # Foreign key tới property. cascade bảo đảm offer con bị xóa cùng property,
    # tránh record mồ côi không còn tin đăng cha.
    property_id = fields.Many2one(
        comodel_name="estate.property",
        string="Property",
        required=True,
        ondelete="cascade",
    )
    # Số ngày offer còn hiệu lực; user có thể sửa validity hoặc deadline.
    validity = fields.Integer(default=constants.DEFAULT_OFFER_VALIDITY_DAYS)
    # inverse làm computed field có thể nhập ngược: đổi deadline sẽ tính validity.
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )
    # Related field đi theo property.type. store=True tạo column thực để action
    # stat button có thể search/domain/group hiệu quả theo property type.
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        store=True,
    )

    # Database luôn từ chối offer 0 hoặc âm, bất kể nguồn ghi dữ liệu.
    _price_positive = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be strictly positive.",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        """Tính deadline từ ngày tạo và số ngày validity.

        Odoo gọi hàm khi ``create_date`` hoặc ``validity`` thay đổi. Khi form
        đang tạo record, ``create_date`` chưa tồn tại vì chưa INSERT; ngày hiện
        tại theo context/timezone của user là fallback an toàn.

        Side effects:
            Gán ``date_deadline`` cho từng offer trong ``self``.
        """
        for offer in self:
            creation_date = fields.Date.to_date(offer.create_date)
            if not creation_date:
                creation_date = fields.Date.context_today(offer)
            offer.date_deadline = creation_date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        """Tính ngược validity khi user trực tiếp thay đổi deadline.

        Odoo gọi inverse lúc lưu một ``date_deadline`` do user nhập. Số ngày
        được tính từ ngày tạo; offer mới chưa có ``create_date`` nên dùng ngày
        hiện tại theo context làm mốc.

        Side effects:
            Gán lại ``validity`` cho từng offer có deadline.
        """
        for offer in self:
            if not offer.date_deadline:
                continue
            creation_date = fields.Date.to_date(offer.create_date)
            if not creation_date:
                creation_date = fields.Date.context_today(offer)
            offer.validity = (offer.date_deadline - creation_date).days

    @api.model_create_multi
    def create(self, vals_list):
        """Tạo một batch offer và cập nhật state của property.

        Odoo gọi override này cho cả form, import và RPC. ``vals_list`` là danh
        sách dict vì decorator hỗ trợ tạo nhiều offer trong một lệnh. Validation
        chạy trước ``super`` để không INSERT offer thấp hơn giá tốt nhất; sau
        ``super`` mới có recordset thật để đổi trạng thái property.

        Args:
            vals_list (list[dict]): Các giá trị thô dùng để tạo offer.

        Raises:
            UserError: Nếu giá mới thấp hơn best price hiện có hoặc trước đó
                trong cùng batch.

        Returns:
            estate.property.offer: Recordset các offer vừa được ORM tạo.
        """

        # Cache giá cao nhất theo property trong chính batch. Nếu batch chứa hai
        # offer cho cùng property, offer sau còn phải so với offer trước dù offer
        # trước chưa được INSERT vào database.
        batch_best_prices = {}
        for values in vals_list:
            # Many2one trong vals là integer ID, vì vậy dùng browse để lấy recordset.
            property_record = self.env["estate.property"].browse(
                values.get("property_id")
            )
            # Giữ create linh hoạt nếu ORM gọi với vals chưa có property; required
            # field/SQL sẽ đưa lỗi chuẩn ở bước super().create().
            if not property_record:
                continue
            current_best = batch_best_prices.get(
                property_record.id, property_record.best_price
            )
            offer_price = values.get("price", 0.0)
            if current_best and float_compare(
                offer_price, current_best, precision_digits=2
            ) < 0:
                raise UserError(
                    _("An offer cannot be lower than the existing best offer.")
                )
            batch_best_prices[property_record.id] = max(current_best, offer_price)

        # super thực hiện security checks, conversion, INSERT và constraints.
        offers = super().create(vals_list)
        # Dùng vòng lặp tường minh thay cho lambda để người mới có thể lần theo
        # từng property. Chỉ chuyển New -> Offer Received, không ghi đè state sau.
        for property_record in offers.property_id:
            if property_record.state == constants.PROPERTY_STATE_NEW:
                property_record.state = constants.PROPERTY_STATE_OFFER_RECEIVED
        return offers

    def _has_another_accepted_offer(self):
        """Kiểm tra property đã có một offer khác được chấp nhận hay chưa.

        Đây là helper nội bộ được ``action_accept`` gọi cho từng offer. Vòng lặp
        có tên biến rõ ràng được dùng thay cho ``filtered(lambda ...)`` để dễ
        debug và giúp quy tắc “mỗi property chỉ có một offer accepted” lộ rõ.

        Returns:
            bool: ``True`` nếu tồn tại sibling offer có trạng thái Accepted.
        """
        self.ensure_one()
        for candidate_offer in self.property_id.offer_ids:
            is_current_offer = candidate_offer == self
            is_accepted = (
                candidate_offer.status == constants.OFFER_STATUS_ACCEPTED
            )
            if not is_current_offer and is_accepted:
                return True
        return False

    def action_accept(self):
        """Chấp nhận offer và đồng bộ dữ liệu sang property.

        Button dấu tick gọi method này. Mỗi offer phải chưa được xử lý, property
        phải còn mở và không được có offer khác Accepted. Nếu hợp lệ, hàm ghi
        buyer, selling price và state lên property trong cùng transaction.

        Raises:
            UserError: Nếu offer đã xử lý, property đã đóng hoặc đã có offer
                khác được chấp nhận.

        Returns:
            bool: ``True`` khi tất cả offer trong ``self`` được chấp nhận.
        """
        for offer in self:
            if offer.status:
                raise UserError(_("A processed offer cannot be accepted again."))
            property_record = offer.property_id
            property_is_closed = (
                property_record.state in constants.PROPERTY_CLOSED_STATES
            )
            if offer._has_another_accepted_offer() or property_is_closed:
                raise UserError(
                    _("Only one offer can be accepted for an available property.")
                )
            offer.status = constants.OFFER_STATUS_ACCEPTED
            # write một dict giúp ba field thay đổi trong cùng transaction.
            property_record.write(
                {
                    "buyer_id": offer.partner_id.id,
                    "selling_price": offer.price,
                    "state": constants.PROPERTY_STATE_OFFER_ACCEPTED,
                }
            )
        return True

    def action_refuse(self):
        """Từ chối toàn bộ offer chưa xử lý trong ``self``.

        Button dấu X gọi method này. Kiểm tra cả recordset trước rồi mới ``write``
        một lần để tránh trạng thái nửa thành công khi chọn nhiều record.

        Raises:
            UserError: Nếu ít nhất một offer đã Accepted hoặc Refused.

        Returns:
            bool: ``True`` sau khi cập nhật trạng thái thành công.
        """
        if self.filtered("status"):
            raise UserError(_("A processed offer cannot be refused again."))
        self.write({"status": constants.OFFER_STATUS_REFUSED})
        return True
