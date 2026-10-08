# Chapter 7 - Relations Between Models

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

```text
res.users 1 -- * estate.property * -- 1 estate.property.type
res.partner 1 -- * estate.property (buyer)
estate.property * -- * estate.property.tag
estate.property 1 -- * estate.property.offer * -- 1 res.partner
```

Type/tag/offer và views đã tạo. Many2one thường tạo foreign key; One2many không
tạo column mà truy vấn qua inverse Many2one; Many2many dùng relation table.
Salesperson mặc định `self.env.user`; buyer `copy=False`; property xóa cascade
offer. `self.env` mang cursor, user, context, company và cache, rộng hơn DI.

Schema/views đã upgrade. Lỗi phổ biến: inverse name sai, quên ACL/import, truyền
recordset thay `.id`. Tự kiểm tra: vì sao One2many cần inverse? Bài tập: tạo hai
property chung một type rồi đọc `type.property_ids`.
