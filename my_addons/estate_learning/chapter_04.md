# Chapter 4 - Security: A Brief Introduction

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

`security/ir.model.access.csv` cấp read/write/create/unlink cho
`base.group_user` trên property, type, tag và offer. `model_estate_property` là
external ID Odoo tự sinh cho `ir.model`.

ACL quyết định thao tác trên model; record rule lọc record cụ thể. Ẩn nút không
phải security vì RPC vẫn gọi được. Security ORM áp dụng cho UI, import, RPC và
module code; không dùng `sudo()` để né ACL.

CSV đã load thành công. Lỗi thường gặp: sai model external ID, quên manifest,
CSV sai header. Tự kiểm tra: ACL khác record rule thế nào? Bốn permission ứng với
method nào? Bài tập: tạo group chỉ đọc và thử CRUD bằng user của group đó.
