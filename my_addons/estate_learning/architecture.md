# Kiến trúc Odoo 19 trong dự án Estate

## Bức tranh ba tầng

```text
Trình duyệt
HTML + CSS + JavaScript/Owl
        │  HTTP/RPC: action, domain, context, dữ liệu form
        ▼
Odoo Server (Python)
Registry + Models + ORM + Security + Business Logic
        │  SQL được ORM sinh ra, trong cùng transaction
        ▼
PostgreSQL
Tables + Rows + Indexes + Constraints
```

### 1. Presentation tier

Đây là phần người dùng nhìn và tương tác. Odoo web client là một ứng dụng web,
dùng HTML5, CSS, JavaScript và Owl. XML view của addon không phải một trang HTML
hoàn chỉnh; nó là **khai báo kiến trúc view** để server lưu trong `ir.ui.view`,
sau đó web client đọc và render bằng component/widget phù hợp.

Trong project hiện tại, `views/estate_property_views.xml` khai báo list, form,
search, action và menu. XML mô tả *cần hiển thị gì*; code web chuẩn của Odoo đảm
nhiệm phần lớn việc render và gửi RPC.

### 2. Logic tier

Tầng này chạy trong Odoo server bằng Python. Model, field, method, security,
computed field, constraint và state transition đều thuộc tầng logic.

`models/estate_property.py` khai báo model `estate.property`. Khi Odoo load
registry của database, class Python được framework đăng ký. ORM cung cấp API
recordset như `search`, `create`, `write`, `unlink`, đồng thời áp dụng access
rights, record rules, cache và transaction.

### 3. Data tier

Odoo 19 dùng PostgreSQL. ORM ánh xạ tên model có dấu chấm sang table dùng dấu
gạch dưới: `estate.property` → `estate_property`. Các stored fields thường trở
thành column; relational field có thể trở thành foreign key hoặc relation table.

Không phải mọi field đều là column. Computed field không `store=True` được tính
khi đọc. Dữ liệu view/action/menu lại nằm trong các table kỹ thuật như
`ir_ui_view`, `ir_actions_act_window`, `ir_ui_menu`.

## Luồng tương tác điển hình

```text
User bấm menu Real Estate
  → web client đọc menu/action
  → action yêu cầu model estate.property và các view list/form
  → web client gửi RPC search/read
  → Odoo xác thực user và ACL/record rules
  → ORM lập truy vấn PostgreSQL
  → recordset được serialize về client
  → list view render dữ liệu
```

Khi user nhấn Save, hướng ngược lại diễn ra: form gom giá trị, RPC gọi
`create()` hoặc `write()`, business rules/constraints chạy, ORM ghi database và
transaction chỉ commit nếu toàn bộ thao tác thành công.

## Module là đơn vị đóng gói

Một Odoo module có thể chứa:

- business objects: Python model;
- object views: XML kiến trúc UI;
- data files: XML/CSV cho action, menu, security, configuration, demo data;
- web controllers: endpoint HTTP;
- static assets: JavaScript, CSS, image và template.

Không thành phần nào ngoài manifest là bắt buộc cho mọi module. `estate` hiện có
model, view và data/security. `__manifest__.py` khai báo metadata, dependency và
thứ tự data files. `__init__.py` tạo chuỗi import Python. `addons_path` cho Odoo
biết phải tìm module ở những thư mục nào; trong môi trường này là
`addons,my_addons`.

## So sánh với web development quen thuộc

| Odoo | Khái niệm gần trong web stack | Giống | Khác quan trọng |
|---|---|---|---|
| XML view | HTML/JSX | Đều mô tả UI theo cây | XML view là metadata được server lưu/ghép và web client diễn giải; không phải DOM/JSX component trực tiếp |
| Window action | Route/navigation config | Chọn màn hình và resource cần mở | Action mang model, view modes, domain, context; không chỉ đổi URL và không tương đương `onClick()` |
| Odoo model | TypeORM entity + service | Mô tả dữ liệu và thao tác persistence | Model đồng thời là recordset API, gắn registry/env/security/inheritance của Odoo |
| ORM | TypeORM/Prisma | Giảm SQL thủ công, ánh xạ object-record | Odoo ORM còn tích hợp ACL, record rules, computed fields, context, cache và module inheritance |
| `self.env` | Dependency injection container | Cấp quyền truy cập dịch vụ/model theo context | `env` còn mang cursor, user, company, context và cache của transaction; không chỉ resolve dependency |
| PostgreSQL | PostgreSQL trong NestJS | Cùng là RDBMS | Odoo yêu cầu PostgreSQL và quản lý schema chủ yếu qua model/module upgrade |

## Community và Enterprise

Odoo Community là nền mã nguồn mở đang có trong workspace. Enterprise về mặt kỹ
thuật là các module bổ sung được cài trên nền Community, kèm giấy phép và dịch vụ
khác. Vì khóa học yêu cầu Community, code không được phụ thuộc module chỉ có ở
Enterprise.

