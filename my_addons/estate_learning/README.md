# Odoo 19 Server Framework 101 - Estate Learning

Thư mục này là tài liệu học tập, **không phải Odoo addon**. Vì vậy nó không có
`__manifest__.py`, không được thêm vào `depends`, và Odoo không cần nạp thư mục
này để module `estate` hoạt động.

Nguồn chính: [Odoo 19 Server Framework 101](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101.html).
Nội dung bài tập đã được đối chiếu với source tài liệu nhánh `19.0` của Odoo
trước khi lập kế hoạch.

## Tài liệu theo luồng thực thi

- [`record_creation_flow.md`](record_creation_flow.md): lần theo đầy đủ quá trình
  tạo Property/Offer từ Menu, Action, Form và RPC đến ORM, constraints,
  PostgreSQL transaction và response trở lại browser.

## Môi trường đã kiểm kê ngày 08/10/2026

| Hạng mục | Kết quả |
|---|---|
| Odoo | Community 19.0 (`odoo/release.py` và `odoo-bin --version`) |
| Python đang chạy Odoo | `.venv/Scripts/python.exe`, Python 3.12.10 |
| Virtual environment khác | `venv/`, cũng là Python 3.12.10, nhưng không phải interpreter của tiến trình Odoo hiện tại |
| PostgreSQL | 17.10, máy chủ cấu hình từ `odoo.conf` |
| Database | `f_soft_test` |
| Addons path | `addons,my_addons` |
| Module đã cài | `base`, `account`, `estate` |
| Module chưa có/chưa cài | `estate_account` |
| Tiến trình Odoo | Đang chạy với `-c odoo.conf -d f_soft_test --addons-path=addons,my_addons` |
| Kiểm tra tĩnh hiện tại | Python parse OK, XML parse OK, manifest parse OK |

Mật khẩu quản trị và mật khẩu PostgreSQL trong `odoo.conf` không được sao chép
vào tài liệu hoặc source code.

## Tiến độ 15 chapter

Quy ước trạng thái: `CHƯA LÀM`, `ĐANG LÀM`, `HOÀN THÀNH`, `ĐÃ KIỂM THỬ`.
Một chapter chỉ được đánh dấu `ĐÃ KIỂM THỬ` sau khi các bài tập tương ứng thực sự
được chạy và xác nhận trên môi trường này.

| Chapter | Chủ đề | Trạng thái học tập | Hiện trạng code trước khóa học |
|---:|---|---|---|
| 1 | Architecture Overview | HOÀN THÀNH | Tài liệu kiến trúc hoàn tất |
| 2 | A New Application | ĐÃ KIỂM THỬ | Manifest/import/addons path hợp lệ |
| 3 | Models And Basic Fields | ĐÃ KIỂM THỬ | Model và fields đã upgrade |
| 4 | Security | ĐÃ KIỂM THỬ | ACL cho bốn model đã load |
| 5 | First UI | ĐÃ KIỂM THỬ | Action/menu/default/reserved fields đã load |
| 6 | Basic Views | ĐÃ KIỂM THỬ | List/form/search được server validate |
| 7 | Relations | ĐÃ KIỂM THỬ | Type/tag/offer và relations đã upgrade |
| 8 | Computed Fields/Onchanges | ĐÃ KIỂM THỬ | Compute/inverse có automated tests; onchange đã load |
| 9 | Actions | ĐÃ KIỂM THỬ | Offer/property workflow có automated tests |
| 10 | Constraints | ĐÃ KIỂM THỬ | SQL/Python constraints đã upgrade/test |
| 11 | Sprinkles | ĐÃ KIỂM THỬ | Widgets/order/attributes/stat action đã load |
| 12 | Inheritance | ĐÃ KIỂM THỬ | Model/view/CRUD inheritance đã load/test |
| 13 | Other Modules | ĐÃ KIỂM THỬ | `estate_account` installed; invoice test pass |
| 14 | QWeb/Kanban | ĐÃ KIỂM THỬ | Kanban/QWeb được server validate |
| 15 | Final Word | HOÀN THÀNH | Review và local automated tests hoàn tất |

Code tồn tại trước khóa học không đồng nghĩa chapter đã hoàn thành: mỗi chapter
còn phải được giải thích, đối chiếu đúng bài tập Odoo 19, kiểm tra và tổng kết.

## Audit code `estate` hiện tại

### Phần đang đúng hoặc có thể tái sử dụng

- Addon nằm đúng dưới `my_addons/estate` và được tìm thấy qua `addons_path`.
- Chuỗi import `estate/__init__.py` → `models/__init__.py` →
  `estate_property.py` đang đúng.
- `_name = "estate.property"` và `_description` đã có.
- Các basic fields của Chapter 3 đã hiện diện; `name` và `expected_price` đang
  `required=True`.
- Manifest đã nạp security CSV và XML view; module đang được đánh dấu là App.
- List, form, search, action và ba cấp menu đã tồn tại trong database.
- Các file Python, XML và manifest đều parse thành công tại thời điểm audit.

### Vấn đề hoặc phần thiếu cần xử lý ở các chapter sau

- `summary` trong manifest đang là chuỗi tạm `sadsfasdfadf`; sẽ sửa ở Chapter 2.
- Version manifest `1.0` hoạt động nhưng nên theo convention của Odoo addon;
  sẽ giải thích và chuẩn hóa ở Chapter 2/15.
- Chapter 4 chính thức yêu cầu `base.group_user` có read/write/create/unlink.
  File hiện tại chỉ cho nhóm này read; quyền CRUD đầy đủ lại gán cho
  `base.group_system`.
- Chapter 5 chính thức yêu cầu menu ở `views/estate_menus.xml`; code hiện tại
  đặt menu chung trong `estate_property_views.xml`.
- Các field `active`, `state`, default/copy/readonly của Chapter 5 chưa có.
- Filter "Available" hiện so sánh ngày, trong khi bài Chapter 6 yêu cầu state là
  `new` hoặc `offer_received`.
- Chưa có model type, tag, offer; chưa có relational fields, computed fields,
  onchange, action methods, constraints, inheritance, kanban và link module.
- Có hai virtual environment giống phiên bản. Nên tiếp tục dùng `.venv` vì đó
  là interpreter của server hiện tại, tránh cài package nhầm vào `venv`.
- Working tree đã bẩn trước khi bắt đầu: manifest và XML view có thay đổi của
  người học; nhiều file trong `venv` cũng thay đổi. Không được reset/xóa các
  thay đổi này.

## File còn thiếu theo đích cuối khóa học

Danh sách sẽ được tạo dần đúng chapter, không tạo code nghiệp vụ trước bài học:

- `estate/views/estate_menus.xml`
- Model/view/access cho `estate.property.type`, `estate.property.tag`,
  `estate.property.offer`
- File inheritance cho `res.users` và view kế thừa
- Tests cho business rules quan trọng
- Toàn bộ addon `my_addons/estate_account/` ở Chapter 13

## Kế hoạch triển khai

1. Chapter 1: hiểu ba tầng, module, ORM, luồng request; ánh xạ vào project thật.
2. Chapter 2–6: chuẩn hóa nền addon, model cơ bản, ACL, action/menu và ba view.
3. Chapter 7–8: thêm mô hình quan hệ, computed/inverse fields và onchange.
4. Chapter 9–10: thêm state transitions, buttons và constraints.
5. Chapter 11–12: hoàn thiện UX, ordering/widgets và inheritance đúng chuẩn.
6. Chapter 13: tạo addon độc lập `estate_account`, sinh customer invoice.
7. Chapter 14: thêm kanban QWeb.
8. Chapter 15: lint, review convention/security/dependency và chạy bộ kiểm thử
   cuối cùng; Runbot chỉ được giải thích, không tuyên bố đã chạy local project.

## Kết quả kiểm thử cuối

Lệnh test local đã upgrade `estate,estate_account` với test tags của hai module.
Kết quả: **5 test methods, 0 failed, 0 errors**. Phạm vi gồm computed fields,
deadline/inverse, offer workflow, offer thấp hơn, constraint 90%, bảo vệ unlink,
và customer invoice hai dòng 6% + 100.

Odoo đã validate/load toàn bộ Python models, CSV ACL và XML views/actions/menus.
Browser đã tới được trang đăng nhập Odoo; smoke test thao tác sau đăng nhập là
**NOT TESTED** vì phiên browser kiểm thử không có thông tin/session đăng nhập.
Runbot: **NOT TESTED** vì đây là project local, không phải branch/PR trên Runbot.
