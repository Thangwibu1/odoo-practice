from odoo.tests import TransactionCase, tagged

from odoo.addons.estate_account.models import constants


@tagged("post_install", "-at_install")
class TestEstateAccount(TransactionCase):
    """Kiểm tra contract giữa Estate workflow và Accounting ORM."""

    def test_sold_property_creates_customer_invoice(self):
        """Sold phải tạo đúng một customer invoice gồm đúng hai dòng phí."""
        # Chuẩn bị buyer, property và offer giống thao tác thực tế trên UI.
        partner = self.env["res.partner"].create({"name": "Invoice Buyer"})
        property_record = self.env["estate.property"].create(
            {"name": "Invoiced Property", "expected_price": 100_000}
        )
        offer = self.env["estate.property.offer"].create(
            {
                "price": 100_000,
                "partner_id": partner.id,
                "property_id": property_record.id,
            }
        )
        offer.action_accept()

        # Ghi nhận số invoice trước action để assertion không phụ thuộc dữ liệu
        # có sẵn trong database chạy test.
        invoice_count = self.env["account.move"].search_count(
            [
                ("move_type", "=", constants.CUSTOMER_INVOICE_MOVE_TYPE),
                ("partner_id", "=", partner.id),
            ]
        )
        # Đây là method đã được estate_account override; super đổi state trước,
        # sau đó extension tạo account.move trong cùng transaction.
        property_record.action_sold()
        invoice = self.env["account.move"].search(
            [
                ("move_type", "=", constants.CUSTOMER_INVOICE_MOVE_TYPE),
                ("partner_id", "=", partner.id),
            ],
            order="id desc",
            limit=1,
        )

        self.assertEqual(
            self.env["account.move"].search_count(
                [
                    ("move_type", "=", constants.CUSTOMER_INVOICE_MOVE_TYPE),
                    ("partner_id", "=", partner.id),
                ]
            ),
            invoice_count + 1,
        )
        # Một dòng commission 6% của 100,000 và một dòng admin fee 100.
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        self.assertEqual(
            sorted(invoice.invoice_line_ids.mapped("price_unit")),
            sorted(
                [
                    constants.ADMINISTRATIVE_FEE_AMOUNT,
                    100_000 * constants.COMMISSION_RATE,
                ]
            ),
        )
