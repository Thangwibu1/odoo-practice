from odoo import Command, models


class EstateProperty(models.Model):
    """Bổ sung việc tạo customer invoice vào workflow bán property."""

    # Không khai báo _name: ta mở rộng đúng model estate.property có sẵn.
    _inherit = "estate.property"

    def action_sold(self):
        """Gọi nghiệp vụ gốc, sau đó tạo một invoice cho mỗi property.

        Toàn bộ chạy trong cùng PostgreSQL transaction. Nếu invoice create lỗi,
        thay đổi state do super() cũng rollback; nhờ vậy không có property Sold
        nhưng thiếu invoice. Không dùng sudo nên ACL của user vẫn được tôn trọng.
        """
        # super kiểm tra canceled/already sold/buyer và đổi state trước. Luôn giữ
        # super để không phá logic của estate hoặc module khác trong MRO.
        result = super().action_sold()
        for property_record in self:
            # self.env lấy account.move trong cùng cursor/user/context/cache.
            self.env["account.move"].create(
                {
                    # out_invoice là Customer Invoice, không phải vendor bill.
                    "move_type": "out_invoice",
                    # Many2one create value phải là integer ID, không phải recordset.
                    "partner_id": property_record.buyer_id.id,
                    # One2many nhận danh sách Commands. Hai line được tạo và liên
                    # kết với invoice trong cùng lệnh create/transaction.
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Real estate commission (6%)",
                                "quantity": 1,
                                # 6% giá bán đã được Accept Offer ghi lên property.
                                "price_unit": property_record.selling_price * 0.06,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Administrative fees",
                                "quantity": 1,
                                # account.move dùng currency của company/journal;
                                # 100.0 được hiểu theo đơn vị tiền tệ đó.
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
            )
        # Trả đúng kết quả action gốc để bảo toàn API contract/chaining.
        return result
