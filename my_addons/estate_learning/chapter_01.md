# Chapter 1 - Architecture Overview

Trạng thái: **HOÀN THÀNH** (chapter lý thuyết, không có bài tập code trong tài
liệu Odoo 19 chính thức).

## 1. Chapter này dạy gì?

Chapter 1 đặt nền móng để biết mỗi đoạn code Odoo đang chạy ở đâu:

- presentation tier: HTML5, CSS, JavaScript/Owl trong trình duyệt;
- logic tier: Python và Odoo framework trên server;
- data tier: PostgreSQL;
- module/addon là đơn vị đóng gói và mở rộng hệ thống;
- manifest, Python package và `addons_path` tạo nên cấu trúc module;
- Community và Enterprise khác nhau chủ yếu ở tập module bổ sung.

Nếu không có bản đồ này, người mới dễ đặt business rule trong UI, viết SQL trực
tiếp khi ORM đã giải quyết được, hoặc tưởng XML view là HTML tĩnh.

## 2. Vì sao Odoo cần tách tầng?

- **Thay đổi độc lập:** có thể cải thiện form mà không đổi table, hoặc thêm
  constraint mà không viết lại web client.
- **Tái sử dụng:** cùng model dùng được từ form, import, cron, RPC hay module khác.
- **Bảo mật nhất quán:** quyền được kiểm tra ở server thay vì tin vào nút ẩn trên UI.
- **Transaction:** nhiều thao tác nghiệp vụ được commit hoặc rollback cùng nhau.
- **Mở rộng bằng module:** addon có thể kế thừa model/view thay vì sửa core.

Chapter này là nền cho toàn bộ phần sau: Chapter 2 tạo module; Chapter 3 dùng ORM;
Chapter 4 thêm security; Chapter 5–6 nối model với action/menu/view; các chapter
còn lại bổ sung business logic và tích hợp module.

## 3. Ánh xạ vào project hiện tại

```text
my_addons/estate/
├── __init__.py                 # điểm vào Python package
├── __manifest__.py             # metadata, dependency, thứ tự data files
├── models/
│   ├── __init__.py             # import model files
│   └── estate_property.py      # logic tier: model và fields
├── security/
│   └── ir.model.access.csv     # data file tạo access rights
└── views/
    └── estate_property_views.xml # metadata cho UI/action/menu
```

`odoo.conf` đặt `addons_path = addons,my_addons`, nên Odoo tìm thấy `estate`.
Database `f_soft_test` đã cài module này. Trong database hiện chỉ có model nghiệp
vụ `estate.property`; các model của Chapter 7 chưa tồn tại.

## 4. XML view không phải HTML

Ví dụ `<field name="expected_price"/>` không tự tạo một thẻ `<input>` HTML theo
cách trình duyệt hiểu. Nó báo cho Odoo web client: "tại vị trí này hãy render
field `expected_price` bằng widget phù hợp với kiểu Float và quyền hiện tại".

HTML/JSX thường mô tả kết quả UI gần DOM hơn. Odoo XML view là khai báo có thể
được lưu database, kế thừa bằng XPath, kết hợp với metadata model rồi mới render.

## 5. Module và dependency

Manifest hiện khai báo `depends: ["base"]`. Điều này có nghĩa `base` phải được
load trước `estate`. Dependency là quan hệ kỹ thuật về module/data/model, không
phải Python package dependency cài bằng `pip`.

Thứ tự trong `data` cũng quan trọng. XML tham chiếu external ID phải được load
sau file tạo external ID đó. Đây là lý do menu tham chiếu action thường được nạp
sau action.

## 6. ORM đứng giữa Python và PostgreSQL

Khai báo:

```python
class EstateProperty(models.Model):
    _name = "estate.property"

    name = fields.Char(required=True)
```

cho ORM đủ metadata để quản lý model/table/column và API recordset. Ta không nên
hiểu đơn giản ORM chỉ là công cụ đổi Python thành SQL: trong Odoo nó còn tham gia
security, cache, context, computed fields, inheritance và lifecycle của module.

Khi module được upgrade, ORM so sánh metadata model để áp dụng thay đổi schema.
Khi user tạo record, `create()` kiểm tra quyền và business logic rồi mới ghi vào
PostgreSQL trong transaction.

## 7. Thứ tự thực thi khi user mở và lưu property

### Mở danh sách

1. User bấm menu.
2. Menu trỏ tới window action.
3. Action chỉ ra `res_model = estate.property` và view modes.
4. Web client lấy view architecture và gửi RPC đọc dữ liệu.
5. Server xác thực user, access rights và record rules.
6. ORM truy vấn PostgreSQL và trả recordset đã serialize.
7. Web client render list/form.

### Lưu form

1. Widget thu thập giá trị đã nhập.
2. Web client gọi RPC `create` hoặc `write`.
3. Server kiểm tra ACL/record rules và chạy model logic.
4. ORM chuyển đổi kiểu dữ liệu, flush thành SQL và chạy constraints.
5. Thành công thì transaction commit; lỗi thì rollback và client nhận exception.

## 8. Kiểm tra đã thực hiện

- Xác nhận source/CLI là Odoo Server 19.0.
- Xác nhận tiến trình đang dùng `.venv` Python 3.12.10.
- Xác nhận `addons_path` có `my_addons`.
- Kết nối PostgreSQL ở chế độ read-only và xác nhận database/module state.
- Parse toàn bộ Python của `estate`: OK.
- Parse XML bằng `lxml`: OK.
- Parse manifest bằng `ast.literal_eval`: OK.
- Không upgrade module và không ghi database trong Chapter 1.

Đây không phải functional test của các chapter nghiệp vụ. Vì Chapter 1 không có
code exercise, trạng thái là `HOÀN THÀNH`, chưa dùng nhãn `ĐÃ KIỂM THỬ` cho toàn
module.

## 9. Kiến thức cần nhớ

- Odoo 19 là ứng dụng nhiều tầng, cụ thể là kiến trúc ba tầng.
- Python model không chạy trong browser; XML view cũng không phải HTML trực tiếp.
- PostgreSQL lưu cả dữ liệu nghiệp vụ lẫn metadata kỹ thuật.
- Module là ranh giới đóng gói và dependency; App chỉ là module được đánh dấu để
  hiển thị như ứng dụng.
- ORM là lớp trung tâm nối model với database và nhiều dịch vụ framework.
- Không sửa core: dùng module dependency và inheritance để mở rộng.

## 10. Câu hỏi tự kiểm tra

1. Khi user bấm Save, những bước nào chạy ở browser, server và database?
2. Vì sao ẩn một button bằng XML không đủ để bảo vệ business rule?
3. `addons_path` khác `depends` như thế nào?
4. Vì sao XML view không nên được gọi đơn giản là "HTML của Odoo"?
5. ORM Odoo cung cấp thêm gì ngoài việc tránh viết SQL?

## 11. Bài tập nhỏ

Không sửa code. Hãy chọn field `expected_price` và tự vẽ đường đi của nó qua ba
tầng từ lúc mở form, nhập giá, bấm Save, cho đến khi dữ liệu nằm trong PostgreSQL.
Ghi rõ ở bước nào security và validation nên được thực thi.

