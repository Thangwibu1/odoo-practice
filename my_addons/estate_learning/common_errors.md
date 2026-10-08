# Lỗi thường gặp trong Odoo 19

Trạng thái: **ĐANG XÂY DỰNG THEO TỪNG CHAPTER**.

## Module không xuất hiện

- `addons_path` chưa chứa thư mục cha của addon.
- Chưa Update Apps List sau khi thêm module.
- Manifest sai cú pháp hoặc addon name không hợp lệ.
- Đang bật filter Apps nhưng manifest chưa có `application: True`.

## Python model không được đăng ký

- Thiếu import trong một trong hai `__init__.py`.
- Chưa restart server sau khi đổi Python.
- Chưa upgrade module sau khi đổi schema.

## XML ID không tìm thấy

- File tạo record chưa có trong manifest.
- Thứ tự data files sai: file tham chiếu được load trước file tạo XML ID.
- Gõ sai `module.xml_id` hoặc record đã bị đổi tên.

## Cài package nhưng Odoo vẫn báo thiếu

Project hiện có cả `.venv` và `venv`. Server đang dùng `.venv`; cài package vào
`venv` sẽ không làm package xuất hiện trong tiến trình Odoo hiện tại.

