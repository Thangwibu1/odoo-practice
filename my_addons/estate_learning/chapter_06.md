# Chapter 6 - Basic Views

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

`estate_property_views.xml` có list, form (`sheet/group/notebook/page`) và search.
`arch` là XML metadata, không phải HTML cuối. Domain là danh sách điều kiện;
Available lọc state new/offer_received. Living area dùng `filter_domain` với
toán tử lớn hơn hoặc bằng. Group By có postcode và property type.

Odoo đã validate/load views. Lỗi phổ biến: field không tồn tại, domain sai, XML
sai, nhầm invisible với ACL. Tự kiểm tra: search field khác filter ra sao? `arch`
lưu ở đâu? Bài tập: thêm Group By salesperson.
