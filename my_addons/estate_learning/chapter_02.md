# Chapter 2 - A New Application

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

## Kiến thức

Addon là Python package được Odoo tìm qua `addons_path`. `__manifest__.py` khai
báo metadata, dependency và data files; hai `__init__.py` tạo chuỗi import.
`application=True` làm module xuất hiện dưới filter Apps. `depends=["base"]` bắt
Odoo load framework nền trước `estate`.

Khác `package.json`, manifest không cài Python library; nó mô tả module cho
registry của từng database. Install tạo metadata/schema; upgrade áp dụng code và
data file mới lên module đã cài.

## Code và kiểm tra

- Manifest được chuẩn hóa version `19.0.1.0.0`, summary và thứ tự XML/CSV.
- `addons_path=addons,my_addons`; database thực tế là `f_soft_test`.
- Manifest parse và upgrade Odoo 19 thành công.

Lỗi thường gặp: thiếu import, sai dấu phẩy, data file sai thứ tự, hoặc cài package
vào `venv` trong khi server chạy `.venv`.

Ghi nhớ: `addons_path` tìm module; `depends` sắp dependency; sửa Python cần
restart, sửa schema/data cần upgrade. Bài tập: thêm `description` vào manifest.
