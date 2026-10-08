# Chapter 3 - Models And Basic Fields

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

`EstateProperty(models.Model)` với `_name="estate.property"` tạo model nghiệp
vụ; ORM ánh xạ sang table `estate_property`. `estate_property.py` có Char, Text,
Date, Float, Integer, Boolean, Selection; `name` và `expected_price` là required.

Odoo tự thêm `id`, `create_uid/date`, `write_uid/date`. Model giống TypeORM Entity
ở ánh xạ dữ liệu nhưng còn là recordset gắn env, security và business methods.
Upgrade tạo/alter schema; `create()` chuyển dict thành INSERT và trả recordset.

Python parse và registry upgrade thành công. Lỗi phổ biến: quên import, Selection
key không ổn định, đổi schema nhưng không `-u estate`.

Tự kiểm tra: `_name` khác `_description` ra sao? Selection lưu key hay label?
Automatic fields do ai quản lý? Bài tập: thêm Integer `floors` rồi upgrade.
