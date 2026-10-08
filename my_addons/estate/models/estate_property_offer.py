from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import _
from odoo.tools.float_utils import float_compare


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
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
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
    validity = fields.Integer(default=7)
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

        Khi form đang tạo record, ``create_date`` chưa tồn tại vì chưa INSERT.
        Ngày hiện tại theo context/timezone user là fallback an toàn.
        """
        for offer in self:
            creation_date = fields.Date.to_date(offer.create_date)
            if not creation_date:
                creation_date = fields.Date.context_today(offer)
            offer.date_deadline = creation_date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        """Tính ngược validity khi user trực tiếp thay đổi deadline."""
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

        Odoo có thể gọi create với nhiều dict một lần, nên không được giả định chỉ
        có một vals. Validation chạy trước ``super`` để transaction không INSERT
        offer sai; sau super ta mới có recordset thật để cập nhật property.
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
        # Chỉ chuyển New -> Offer Received; không ghi đè state Accepted/Sold.
        offers.property_id.filtered(
            lambda property_record: property_record.state == "new"
        ).state = "offer_received"
        return offers

    def action_accept(self):
        """Chấp nhận offer và đồng bộ buyer/giá bán/state lên property."""
        for offer in self:
            if offer.status:
                raise UserError(_("A processed offer cannot be accepted again."))
            property_record = offer.property_id
            # Lọc trong recordset sibling offers để duy trì invariant: một
            # property chỉ có tối đa một offer accepted.
            accepted_offer = property_record.offer_ids.filtered(
                lambda candidate: candidate.status == "accepted" and candidate != offer
            )
            if accepted_offer or property_record.state in ("sold", "canceled"):
                raise UserError(
                    _("Only one offer can be accepted for an available property.")
                )
            offer.status = "accepted"
            # write một dict giúp ba field thay đổi trong cùng transaction.
            property_record.write(
                {
                    "buyer_id": offer.partner_id.id,
                    "selling_price": offer.price,
                    "state": "offer_accepted",
                }
            )
        return True

    def action_refuse(self):
        """Từ chối các offer chưa xử lý; không cho đảo trạng thái cuối."""
        if self.filtered("status"):
            raise UserError(_("A processed offer cannot be refused again."))
        self.write({"status": "refused"})
        return True
