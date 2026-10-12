"""Các hằng số nghiệp vụ riêng của phần tích hợp Estate–Accounting."""

# ``account.move.move_type`` dùng key này cho hóa đơn bán hàng của khách hàng.
CUSTOMER_INVOICE_MOVE_TYPE = "out_invoice"

# Các tham số tạo dòng hóa đơn khi property được đánh dấu Sold.
COMMISSION_PERCENT = 6
COMMISSION_RATE = COMMISSION_PERCENT / 100
COMMISSION_LINE_NAME = f"Real estate commission ({COMMISSION_PERCENT}%)"
ADMINISTRATIVE_FEE_LINE_NAME = "Administrative fees"
ADMINISTRATIVE_FEE_AMOUNT = 100.0
