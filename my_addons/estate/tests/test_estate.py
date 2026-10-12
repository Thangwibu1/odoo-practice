from datetime import timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

from odoo.addons.estate.models import constants


@tagged("post_install", "-at_install")
class TestEstate(TransactionCase):
    """Integration tests chạy trong transaction và rollback sau từng test.

    post_install giúp test chạy sau khi module/registry đã load đầy đủ. Việc dùng
    TransactionCase cho phép kiểm tra ORM, SQL constraints và relational fields
    trên PostgreSQL thật mà không giữ lại dữ liệu test.
    """

    @classmethod
    def setUpClass(cls):
        """Tạo fixture dùng chung một lần để test chạy nhanh và nhất quán."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Estate Buyer"})
        cls.property_type = cls.env["estate.property.type"].create(
            {"name": "Test Apartment 19"}
        )
        cls.property = cls.env["estate.property"].create(
            {
                "name": "Test Property",
                "expected_price": 100_000,
                "living_area": 80,
                "garden_area": 20,
                "property_type_id": cls.property_type.id,
            }
        )

    def test_computed_fields_and_offer_flow(self):
        """Kiểm tra happy path từ property mới đến Sold."""
        # Compute không store vẫn được ORM tính khi đọc field.
        self.assertEqual(self.property.total_area, 100)

        # create offer phải đổi state property và cập nhật best_price.
        offer = self.env["estate.property.offer"].create(
            {
                "price": 95_000,
                "partner_id": self.partner.id,
                "property_id": self.property.id,
            }
        )
        self.assertEqual(
            self.property.state,
            constants.PROPERTY_STATE_OFFER_RECEIVED,
        )
        self.assertEqual(self.property.best_price, 95_000)
        self.assertEqual(
            offer.date_deadline,
            offer.create_date.date() + timedelta(days=offer.validity),
        )

        # Accept đồng bộ dữ liệu từ offer sang property trong một transaction.
        offer.action_accept()
        self.assertEqual(
            self.property.state,
            constants.PROPERTY_STATE_OFFER_ACCEPTED,
        )
        self.assertEqual(self.property.buyer_id, self.partner)
        self.assertEqual(self.property.selling_price, 95_000)

        # Chỉ property đã có buyer mới được chuyển sang Sold.
        self.property.action_sold()
        self.assertEqual(self.property.state, constants.PROPERTY_STATE_SOLD)

    def test_lower_offer_is_rejected(self):
        """Business create override phải chặn offer thấp hơn giá cao nhất."""
        self.env["estate.property.offer"].create(
            {
                "price": 95_000,
                "partner_id": self.partner.id,
                "property_id": self.property.id,
            }
        )
        with self.assertRaises(UserError):
            self.env["estate.property.offer"].create(
                {
                    "price": 90_000,
                    "partner_id": self.partner.id,
                    "property_id": self.property.id,
                }
            )

    def test_selling_price_constraint(self):
        """@api.constrains phải rollback giá bán dưới ngưỡng 90%."""
        with self.assertRaises(ValidationError):
            self.property.selling_price = 80_000

    def test_delete_business_rule(self):
        """@api.ondelete không cho xóa property đang có offer."""
        self.property.state = constants.PROPERTY_STATE_OFFER_RECEIVED
        with self.assertRaises(UserError):
            self.property.unlink()
