# Chapter 13 - Interact With Other Modules

Trạng thái: **HOÀN THÀNH, ĐÃ CÀI ĐẶT**.

Addon `estate_account` phụ thuộc `estate` và `account`, nhưng `estate` chỉ phụ
thuộc `base`, nên nghiệp vụ bất động sản vẫn độc lập khi không cài tích hợp.

Model kế thừa `estate.property`, override `action_sold()`, gọi `super()` trước rồi
tạo `account.move` loại `out_invoice` cho buyer. `invoice_line_ids` nhận hai
`Command.create()` trong cùng create: hoa hồng 6% selling price và phí hành chính
100 theo currency công ty/invoice.

`self.env["account.move"]` lấy model trong cùng registry/env/transaction. Nếu tạo
invoice lỗi, cả state sold và invoice rollback; không dùng `sudo()`, nên quyền
thực tế được tôn trọng. Many2one values dùng ID; One2many dùng Command namespace.

Module đã install trên `f_soft_test`. Test xác nhận invoice customer có đúng hai
dòng và price units. Tự kiểm tra: vì sao link module tốt hơn thêm `account` vào
estate? Bài tập: thêm origin/reference tới property.
