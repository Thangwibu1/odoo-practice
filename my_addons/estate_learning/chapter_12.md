# Chapter 12 - Inheritance

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

`res_users.py` dùng `_inherit="res.users"` để thêm One2many property mà không tạo
model mới. `res_users_views.xml` kế thừa `base.view_users_form`, dùng XPath chèn
page Real Estate Properties vào notebook. Vì module extension được ghép lúc load,
không cần và không được sửa source core.

Offer override `create()` bằng `@api.model_create_multi`: từ vals browse property,
chặn offer thấp hơn best hiện có, gọi `super()`, rồi đổi state sang Offer Received.
Property dùng `@api.ondelete(at_uninstall=False)` để chỉ cho xóa New/Canceled mà
không cản uninstall module.

`super()` giữ hành vi framework và các module khác trong chuỗi MRO. Lỗi phổ biến:
quên super, XPath quá mong manh, assume singleton, override create kiểu cũ.

Tự kiểm tra: `_inherit` khác `_name`? Vì sao ondelete tốt hơn override unlink cho
quy tắc này? Bài tập: kế thừa user list để thêm số property computed.
