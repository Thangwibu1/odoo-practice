# Chapter 10 - Constraints

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

Odoo 19 dùng `models.Constraint`: expected price > 0, selling price >= 0, offer
price > 0, type/tag name unique. PostgreSQL bảo vệ dữ liệu ở tầng cuối, kể cả khi
ghi không qua form.

`@api.constrains("selling_price", "expected_price")` bảo đảm selling price không
thấp hơn 90% expected price; giá 0 được bỏ qua trước khi offer accept. So sánh
float dùng `float_compare` thay vì so sánh nhị phân trực tiếp. `ValidationError`
rollback transaction và báo lỗi nhập liệu.

Dữ liệu cũ đã được kiểm tra trước khi thêm SQL constraints; không có row vi phạm.
Test xác nhận Python constraint chặn giá thấp. Tự kiểm tra: SQL và Python
constraint nên dùng khi nào? Bài tập: thử tạo hai tag trùng tên.
