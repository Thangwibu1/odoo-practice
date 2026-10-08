# Luồng Odoo 19 từ số 0 đến database: khai báo app và tạo một Property

Tài liệu này dùng đúng module `estate` trong project và đúng màn hình Properties
đang thấy trên trình duyệt. Nó bắt đầu từ lúc **chưa có app Real Estate**, đi qua
toàn bộ phần khai báo module, cài app, tạo bảng, tạo menu/view, rồi mới lần theo
thao tác **New → nhập dữ liệu → Save → INSERT database**.

Mục tiêu là trả lời thật cụ thể:

- Vì sao chỉ cần tạo folder `estate` thì Odoo chưa coi đó là một app hoàn chỉnh?
- `odoo.conf`, `__manifest__.py` và hai file `__init__.py` nối với nhau thế nào?
- Khai báo `_name`, field, ACL, view, action và menu theo thứ tự nào?
- Khi bấm Install/Upgrade, khai báo nào biến thành bảng và metadata trong database?
- Khi bấm menu, Odoo đi qua file nào?
- Khi bấm **New**, dòng nào chạy?
- Default values xuất hiện từ đâu?
- Khi nhập Garden, onchange chạy lúc nào?
- Khi bấm **Save**, dòng nào thực sự gọi `create()`?
- ACL, ORM, constraints và PostgreSQL chạy theo thứ tự nào?
- Vì sao tạo Property không thấy method `create()` trong file custom?
- Tạo Offer khác Property ở đâu?

> Số dòng trong tài liệu khớp source ngày 08/10/2026. Sau này nếu thêm code làm
> số dòng thay đổi, hãy tìm bằng XML ID hoặc tên method được ghi trong mỗi bước.

## Cách đọc tài liệu này

Đừng bắt đầu từ giữa nếu bạn đang học lần đầu. Hãy đọc theo đúng thứ tự:

```text
Phần 0  Khai báo app từ folder trống và install vào Odoo
   ↓
Phần A  Đối chiếu kết quả với đúng màn hình trong ảnh
   ↓
Phần B  Hiểu XML, Python, browser, server và database khác nhau thế nào
   ↓
Phần C  Phóng to quá trình Odoo load module
   ↓
Phần D  User mở menu Properties
   ↓
Phần E  User bấm New
   ↓
Phần F  User nhập field, onchange và compute chạy
   ↓
Phần G  User bấm Save ở browser
   ↓
Phần H  Server chạy web_save/create/ORM/SQL
   ↓
Phần I  ID của record được trả về browser
```

Nếu câu hỏi của bạn là “khai báo app từ đầu ra sao?”, đọc **Phần 0**. Nếu câu
hỏi là “một cú Save chạy qua đâu?”, tiếp tục từ **Phần G đến Phần I**.

---

# Phần 0 — Từ folder trống đến app Real Estate xuất hiện trên Odoo

Đây là phần bắt đầu thật sự. Ta giả sử ban đầu project **chưa có** folder
`my_addons/estate` và muốn tạo app Real Estate từ con số 0.

## 0.1. Bức tranh tổng thể trước khi đi từng file

Một app Odoo không phải chỉ có một file Python. Nó là một chuỗi khai báo:

```text
odoo.conf
    │
    │ addons_path chứa my_addons
    ▼
my_addons/estate/__manifest__.py
    │
    ├── depends: module nào phải có trước?
    ├── data: nạp ACL/XML nào, theo thứ tự nào?
    └── application: có được coi là app không?
    │
    ▼
my_addons/estate/__init__.py
    │ import models
    ▼
my_addons/estate/models/__init__.py
    │ import estate_property
    ▼
my_addons/estate/models/estate_property.py
    │ khai báo model estate.property và các field
    ▼
Odoo Registry + PostgreSQL schema
    │ model/field đã tồn tại để XML có thể tham chiếu
    ▼
security/ir.model.access.csv
    │ ai được read/write/create/unlink?
    ▼
views/estate_property_views.xml
    │ list/form/search/kanban + window action
    ▼
views/estate_menus.xml
    │ menu gọi action
    ▼
App Real Estate xuất hiện trên giao diện
```

Hãy nhớ câu này:

> Python khai báo **dữ liệu và hành vi**; ACL khai báo **quyền**; view khai báo
> **cách nhìn**; action khai báo **mở model nào**; menu khai báo **đường để user
> đi đến action**.

Không có thành phần nào trong số đó tự thay thế được thành phần còn lại.

---

## 0.2. Bước 1 — Tạo đúng cấu trúc thư mục addon

Module đang dùng có cấu trúc rút gọn như sau:

```text
my_addons/
└── estate/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── estate_property.py
    │   ├── estate_property_offer.py
    │   ├── estate_property_tag.py
    │   ├── estate_property_type.py
    │   └── res_users.py
    ├── security/
    │   └── ir.model.access.csv
    ├── views/
    │   ├── estate_property_views.xml
    │   ├── estate_property_offer_views.xml
    │   ├── estate_property_tag_views.xml
    │   ├── estate_property_type_views.xml
    │   ├── res_users_views.xml
    │   └── estate_menus.xml
    └── tests/
        ├── __init__.py
        └── test_estate.py
```

Tên folder `estate` là **technical module name**. Tên này được dùng trong:

- external ID, ví dụ `estate.estate_property_action`;
- lệnh upgrade `-u estate`;
- bảng `ir_module_module`;
- dependency của module khác: `"depends": ["estate"]`.

Tên folder chưa quyết định tên hiển thị “Real Estate”. Tên hiển thị được lấy từ
`"name"` trong manifest.

### Nếu chỉ tạo folder thì sao?

Odoo chưa chắc nhìn thấy nó. Để được nhận diện là module, tối thiểu cần:

```text
estate/
├── __init__.py
└── __manifest__.py
```

`__manifest__.py` giúp Odoo nhận dạng module; `__init__.py` bắt đầu chuỗi import
Python của module.

---

## 0.3. Bước 2 — Cho Odoo biết nơi chứa custom addons

### File

`odoo.conf`, dòng 12:

```ini
addons_path = addons,my_addons
```

### Odoo hiểu gì?

```text
addons     → addon chuẩn đi kèm Odoo
my_addons  → addon tự viết của project
```

Khi server khởi động hoặc cập nhật Apps List, Odoo quét các thư mục trong
`addons_path` để tìm folder có `__manifest__.py`.

### Nếu thiếu `my_addons`

Chuỗi bị đứt ngay tại đây:

```text
Odoo không quét my_addons
→ không thấy estate/__manifest__.py
→ không có module estate trong Apps
→ không thể install
```

### Input và output của bước này

```text
Input:  đường dẫn addons trong odoo.conf
Output: danh sách vị trí Odoo được phép tìm module
Next:   Odoo phát hiện manifest của estate
```

---

## 0.4. Bước 3 — Manifest khai báo danh tính và “kế hoạch nạp” của app

### File

`my_addons/estate/__manifest__.py`

### Nội dung đang dùng

```python
{
    "name": "Real Estate",
    "version": "19.0.1.0.0",
    "summary": "Manage real estate properties and offers",
    "author": "Minh Lam",
    "license": "LGPL-3",
    "category": "Sales/Real Estate",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/estate_property_offer_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_views.xml",
        "views/res_users_views.xml",
        "views/estate_menus.xml",
    ],
    "installable": True,
    "application": True,
}
```

### Giải nghĩa từng nhóm

| Key | Vai trò | Nếu sai hoặc thiếu |
|---|---|---|
| `name` | Tên hiển thị trong Apps | App có tên khó nhận biết |
| `version` | Version của addon | Khó theo dõi release/migration |
| `depends` | Module phải load trước | Model/external ID phụ thuộc có thể không tồn tại |
| `data` | File dữ liệu phải import | ACL/view/menu sẽ không vào database |
| `installable` | Cho phép cài module | `False` thì không thể cài bình thường |
| `application` | Đánh dấu module là app | Có thể bị ẩn khi đang lọc Apps |

### Tại sao `depends` chỉ có `base`?

Model này dùng `res.users`, `res.partner`, `ir.ui.view`, menu, ACL và ORM cơ bản;
chúng đến từ `base`. Phần kế toán được tách sang module `estate_account`, vì vậy
`estate` không bắt buộc người dùng phải cài Accounting.

### Tại sao thứ tự `data` quan trọng?

Odoo load danh sách từ trên xuống. Trong project này:

```text
1. ACL
2. các view/action
3. estate_menus.xml ở cuối
```

Menu Properties có:

```xml
action="estate_property_action"
```

Do đó action phải được tạo trước khi file menu tham chiếu tới nó. Nếu menu load
trước action, XML ID chưa tồn tại và upgrade có thể thất bại.

### Manifest không làm gì?

Manifest **không tự import** `estate_property.py`. Việc import Python thuộc về
hai file `__init__.py` ở bước tiếp theo.

---

## 0.5. Bước 4 — Root `__init__.py` mở cửa vào code Python

### File

`my_addons/estate/__init__.py`

```python
from . import models
```

Khi Odoo load module Python `odoo.addons.estate`, dòng này yêu cầu Python import
package `models`.

### Nếu bỏ dòng này

```text
Odoo vẫn thấy manifest
→ module vẫn có tên trong Apps
→ nhưng package models không được import
→ class EstateProperty chưa bao giờ được Python thực thi
→ model estate.property không vào registry
→ ACL/XML tham chiếu model sẽ lỗi
```

Đây là khác biệt giữa:

```text
Odoo thấy module       ≠       Odoo đã đăng ký model
manifest tồn tại               file model đã được import
```

---

## 0.6. Bước 5 — `models/__init__.py` import từng file model

### File

`my_addons/estate/models/__init__.py`

```python
from . import estate_property
from . import estate_property_offer
from . import estate_property_tag
from . import estate_property_type
from . import res_users
```

Python không tự động chạy tất cả file `.py` nằm trong folder. Mỗi file model cần
được import rõ ràng ở đây.

Chuỗi hiện tại là:

```text
Odoo import odoo.addons.estate
→ estate/__init__.py
→ import estate.models
→ estate/models/__init__.py
→ import estate_property.py
→ Python thực thi thân class EstateProperty
→ metaclass của Odoo thu thập khai báo model
```

### Ví dụ lỗi thường gặp

Bạn tạo file:

```text
models/estate_property.py
```

nhưng quên thêm:

```python
from . import estate_property
```

Kết quả: file nằm trên ổ đĩa nhưng với Python/Odoo nó gần như không tồn tại.

---

## 0.7. Bước 6 — Khai báo model `estate.property`

### File

`my_addons/estate/models/estate_property.py`, dòng 9–21:

```python
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
```

### Từng dòng có nghĩa gì?

#### `class EstateProperty(models.Model)`

Đây là class Python kế thừa ORM base class. Nhờ `models.Model`, class có sẵn các
API như:

```text
create, write, unlink, search, browse, read, mapped, filtered, ...
```

#### `_name = "estate.property"`

Đây là tên kỹ thuật quan trọng nhất của model:

```text
Python/RPC model name: estate.property
Database table mặc định: estate_property
ACL model external ID: model_estate_property
```

Quy tắc table mặc định là thay dấu chấm bằng dấu gạch dưới:

```text
estate.property  →  estate_property
```

#### `_description`

Là nhãn mô tả model trong metadata và giao diện kỹ thuật. Nó không phải tên bảng.

#### `_order = "id desc"`

Khi `search()` không truyền `order`, record có ID mới hơn xuất hiện trước.

### Điều xảy ra trong Registry

Lúc Python import class, Odoo chưa INSERT một Property. Nó đăng ký “bản thiết kế”:

```text
registry["estate.property"] = model class đã được build
```

Sau khi registry hoàn tất, các lời gọi sau mới resolve được:

```python
self.env["estate.property"]
```

---

## 0.8. Bước 7 — Khai báo field của model

Ví dụ các field đầu tiên, dòng 27–40:

```python
name = fields.Char(string="Title", required=True)
description = fields.Text()
postcode = fields.Char()
date_availability = fields.Date(
    copy=False,
    default=lambda self: fields.Date.today() + relativedelta(months=3),
)
expected_price = fields.Float(required=True)
selling_price = fields.Float(copy=False, readonly=True)
bedrooms = fields.Integer(default=2)
```

### Một field đi qua ba lớp

Lấy `name` làm ví dụ:

```text
Python declaration
name = fields.Char(string="Title", required=True)
        │
        ├── Registry biết field tên name, kiểu char
        ├── ir.model.fields lưu metadata của field
        ├── PostgreSQL có column name
        └── View dùng <field name="name"/> để render widget
```

### Tách rõ tên Python, label và column

```python
name = fields.Char(string="Title", required=True)
```

| Thành phần | Giá trị |
|---|---|
| Tên attribute Python | `name` |
| Tên field ORM | `name` |
| Column mặc định | `name` |
| Label trên UI | `Title` |
| Kiểu Python/ORM | `Char` |
| Bắt buộc | Có |

Vì vậy list view khai báo `<field name="name"/>` nhưng header hiện **Title**.

### `required=True` đi đến đâu?

Nó phục vụ nhiều tầng:

```text
Model metadata → web client biết field bắt buộc
ORM            → không cho tạo nếu thiếu giá trị hợp lệ
Schema         → field stored thường có NOT NULL khi khả thi
```

Không nên chỉ đặt `required` ở XML view, vì import/RPC có thể bỏ qua view.

### Default chạy lúc nào?

```python
bedrooms = fields.Integer(default=2)
```

Default không tạo sẵn record. Nó được ORM dùng khi client gọi `default_get()`
hoặc `create()` thiếu key `bedrooms`.

Callable default:

```python
default=lambda self: fields.Date.today() + relativedelta(months=3)
```

được gọi tại thời điểm cần default, nên ngày được tính theo lúc tạo chứ không bị
đóng băng từ lúc server khởi động.

---

## 0.9. Bước 8 — Khai báo quan hệ giữa các model

Property đang có đủ ba loại quan hệ phổ biến.

### Many2one: Property thuộc một Type

```python
property_type_id = fields.Many2one(
    comodel_name="estate.property.type",
    string="Property Type",
)
```

Database lưu foreign key logic trên bảng Property:

```text
estate_property.property_type_id → estate_property_type.id
```

### One2many: Property có nhiều Offer

```python
offer_ids = fields.One2many(
    comodel_name="estate.property.offer",
    inverse_name="property_id",
    string="Offers",
)
```

`offer_ids` không phải column chứa một danh sách ID trên bảng Property. Odoo tìm
các Offer có:

```text
estate_property_offer.property_id = property hiện tại
```

### Many2many: Property có nhiều Tag và Tag thuộc nhiều Property

```python
tag_ids = fields.Many2many(
    comodel_name="estate.property.tag",
    string="Tags",
)
```

ORM dùng một relation table trung gian để lưu từng cặp Property–Tag.

### Điều kiện để relation hoạt động

Các model đích như `estate.property.type`, `estate.property.offer` và
`estate.property.tag` cũng phải được khai báo và import vào cùng registry. Đó là
lý do `models/__init__.py` import tất cả file model.

---

## 0.10. Bước 9 — Khai báo logic trên model

Ngoài field, class model còn chứa hành vi.

### Computed field

```python
total_area = fields.Integer(compute="_compute_total_area")

@api.depends("living_area", "garden_area")
def _compute_total_area(self):
    for property_record in self:
        property_record.total_area = (
            property_record.living_area + property_record.garden_area
        )
```

Khai báo này nối dependency graph:

```text
living_area ─┐
             ├── thay đổi → invalidate/recompute total_area
garden_area ─┘
```

### Onchange

```python
@api.onchange("garden")
def _onchange_garden(self):
    ...
```

Decorator nói với web client/server: khi field `garden` đổi trên form, chạy
method này trên pseudo-record để trả giá trị gợi ý. Nó chưa đồng nghĩa với INSERT.

### Constraint

```python
@api.constrains("selling_price", "expected_price")
def _check_selling_price(self):
    ...
```

Constraint chạy trong luồng ghi dữ liệu, không phụ thuộc người dùng tạo từ form,
import hay RPC.

### Button action

```python
def action_sold(self):
    ...
```

Method chỉ trở thành button UI khi XML form khai báo:

```xml
<button name="action_sold" type="object" string="Sold"/>
```

Python method không tự sinh button; XML button cũng không có logic nếu không có
method Python tương ứng.

---

## 0.11. Bước 10 — Install/upgrade biến khai báo model thành schema

Khi cài hoặc upgrade `estate`, Odoo build registry và đồng bộ model với database.

Về mặt khái niệm:

```text
_name = "estate.property"
        ↓
metadata ir.model cho estate.property
        ↓
fields.*
        ↓
metadata ir.model.fields
        ↓
table estate_property + các column stored
```

Table thực tế có cả field khai báo và automatic fields:

```text
estate_property
├── id
├── name
├── description
├── postcode
├── date_availability
├── expected_price
├── selling_price
├── bedrooms
├── ...
├── create_uid
├── create_date
├── write_uid
└── write_date
```

### Field nào không nhất thiết có column?

- `One2many` là quan hệ ngược, không tạo column list trên Property.
- computed field không có `store=True` như `total_area` thường không có column.
- `Many2many` dùng relation table.

### Install và upgrade khác nhau

```text
Install: module chưa được cài → tạo metadata/schema/data lần đầu
Upgrade: module đã cài → đọc lại Python/data và cập nhật thay đổi
Restart: nạp lại Python process, nhưng không thay thế việc upgrade XML/schema
```

Sau khi thêm field hoặc sửa XML, quy trình học tập an toàn thường là:

```text
1. Restart Odoo để Python mới được import.
2. Upgrade module estate để schema/XML data được cập nhật.
3. Hard refresh browser nếu cần để bỏ cache giao diện.
```

---

## 0.12. Bước 11 — Cấp quyền cho model

Model tồn tại không có nghĩa user được dùng nó.

### File

`my_addons/estate/security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_estate_property_staff,access_estate_property_staff,model_estate_property,base.group_user,1,1,1,1
```

### Giải nghĩa dòng Property

```text
model_estate_property → external ID tự sinh cho model estate.property
base.group_user       → nhóm Internal User
1,1,1,1               → read, write, create, unlink đều được phép
```

ACL không tạo menu và không tạo view. Nó chỉ trả lời:

```text
User thuộc group này có được gọi operation trên model không?
```

Khi bấm Save record mới, cột `perm_create` là quyền liên quan trực tiếp.

### Nếu có model nhưng thiếu ACL

Admin đặc biệt có thể làm bạn tưởng mọi thứ ổn, nhưng user thường sẽ gặp Access
Error. Vì vậy cần kiểm thử bằng user đúng nhóm, không chỉ bằng superuser.

---

## 0.13. Bước 12 — Khai báo List View

### File

`my_addons/estate/views/estate_property_views.xml`, dòng 8–34:

```xml
<record id="estate_property_view_list" model="ir.ui.view">
    <field name="name">estate.property.list</field>
    <field name="model">estate.property</field>
    <field name="arch" type="xml">
        <list string="Properties">
            <field name="name"/>
            <field name="postcode"/>
            <field name="property_type_id"/>
            <field name="bedrooms"/>
            <field name="living_area"/>
            <field name="expected_price"/>
            <field name="selling_price"/>
            <field name="tag_ids" widget="many2many_tags"/>
        </list>
    </field>
</record>
```

### Hai `model` khác nhau trong đoạn XML

Đây là chỗ rất dễ nhầm:

```xml
<record ... model="ir.ui.view">
```

nghĩa là **đang tạo một record thuộc model `ir.ui.view`**.

Còn:

```xml
<field name="model">estate.property</field>
```

nghĩa là view này **dùng để hiển thị record của `estate.property`**.

### `id` trong XML trở thành gì?

```xml
id="estate_property_view_list"
```

Kết hợp với technical module name `estate` thành external ID:

```text
estate.estate_property_view_list
```

Trong database hiện tại, external ID này trỏ tới một numeric database ID. Numeric
ID có thể đổi giữa database; external ID là thứ module khác nên tham chiếu.

### `<field name="name"/>` có khai báo field mới không?

Không. Field đã được khai báo ở Python. XML chỉ nói:

> Trong view này, hãy hiển thị field ORM có tên `name`.

Nếu Python không có field đó, validation view khi upgrade sẽ báo lỗi.

---

## 0.14. Bước 13 — Khai báo Form View

Form view cũng là một record `ir.ui.view`, nhưng root của `arch` là `<form>`:

```xml
<record id="estate_property_view_form" model="ir.ui.view">
    <field name="name">estate.property.form</field>
    <field name="model">estate.property</field>
    <field name="arch" type="xml">
        <form string="Property">
            <header>
                <button name="action_sold" type="object" string="Sold"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <field name="name"/>
                <field name="expected_price"/>
            </sheet>
        </form>
    </field>
</record>
```

Các mối nối quan trọng:

```text
<field name="name"/>
        └── registry["estate.property"]._fields["name"]

<button name="action_sold" type="object"/>
        └── registry["estate.property"].action_sold(recordset)
```

`type="object"` là lý do button gọi method Python. Nếu `type="action"`, tên sẽ
được hiểu theo một action khác thay vì method model.

---

## 0.15. Bước 14 — Khai báo Search View

```xml
<record id="estate_property_view_search" model="ir.ui.view">
    <field name="model">estate.property</field>
    <field name="arch" type="xml">
        <search string="Search Properties">
            <field name="name"/>
            <filter name="available" string="Available"
                    domain="[('state', 'in', ('new', 'offer_received'))]"/>
        </search>
    </field>
</record>
```

Search view không tự chạy domain mọi lúc. Filter `available` chỉ được áp dụng khi:

- user bấm filter; hoặc
- action truyền context kích hoạt `search_default_available`.

Mối nối này sẽ xuất hiện ở bước action ngay sau đây.

---

## 0.16. Bước 15 — Window Action nối giao diện với model

### File

`my_addons/estate/views/estate_property_views.xml`, dòng 214–220:

```xml
<record id="estate_property_action" model="ir.actions.act_window">
    <field name="name">Properties</field>
    <field name="res_model">estate.property</field>
    <field name="view_mode">list,kanban,form</field>
    <field name="context">{'search_default_available': True}</field>
</record>
```

### Giải nghĩa

| Field | Ý nghĩa |
|---|---|
| `res_model` | Model mà action sẽ đọc/tạo/sửa |
| `view_mode` | Các kiểu view và thứ tự ưu tiên |
| `context` | Dữ liệu bổ sung gửi theo action |

Action chính là cầu nối còn thiếu giữa menu và model:

```text
Menu → Window Action → estate.property → các view phù hợp
```

Context:

```python
{"search_default_available": True}
```

được web client ghép với filter có:

```xml
<filter name="available" .../>
```

Do đó ảnh của bạn có chip **Available** ngay khi vừa mở màn hình.

---

## 0.17. Bước 16 — Menu đưa app và action lên thanh điều hướng

### File

`my_addons/estate/views/estate_menus.xml`

```xml
<menuitem id="estate_menu_root" name="Real Estate" sequence="10"/>

<menuitem id="estate_menu_properties"
          name="Advertisements"
          parent="estate_menu_root"/>

<menuitem id="estate_menu_property_list"
          name="Properties"
          parent="estate_menu_properties"
          action="estate_property_action"/>
```

### Ba cấp trong ảnh

```text
Real Estate                         ← root menu / app
└── Advertisements                 ← menu container
    └── Properties                 ← menu có action
        └── estate_property_action ← mở model estate.property
```

Root menu không cần tự chứa model. Menu lá `Properties` có thuộc tính `action`,
và chính thuộc tính này bắt đầu luồng mở màn hình.

### Vì sao file menu được load cuối?

Menu lá tham chiếu external ID `estate_property_action`. Action phải tồn tại trước
thì reference mới resolve được.

---

## 0.18. Bước 17 — Đưa các file ACL/XML vào manifest

Viết file XML chưa đủ. File phải có mặt trong `data` của manifest:

```python
"data": [
    "security/ir.model.access.csv",
    "views/estate_property_views.xml",
    "views/estate_menus.xml",
]
```

Nếu quên một file:

```text
File vẫn tồn tại trên ổ đĩa
→ nhưng loader không được yêu cầu đọc file đó
→ record XML/CSV không được tạo trong database
```

Ví dụ:

- quên ACL → model tồn tại nhưng user thiếu quyền;
- quên property views → model tồn tại nhưng chưa có UI mong muốn;
- quên menus → action tồn tại nhưng không có đường menu để mở;
- quên action nhưng menu vẫn tham chiếu → upgrade báo external ID not found.

---

## 0.19. Bước 18 — Cập nhật Apps List và Install module

Sau khi source đã đầy đủ, Odoo cần thực hiện hai việc khác nhau.

### Update Apps List

Mục đích: quét manifest để Odoo biết module `estate` tồn tại hoặc metadata manifest
đã đổi.

### Install

Mục đích: thực sự load dependency, import Python, đồng bộ schema, ACL và XML data.

Luồng install rút gọn:

```text
User bấm Install estate
→ Odoo đọc depends=["base"]
→ bảo đảm base đã cài
→ import estate/__init__.py
→ import models/__init__.py
→ đăng ký các model/field vào registry
→ đồng bộ tables/columns/constraints
→ load ir.model.access.csv
→ load từng XML view/action theo manifest
→ load estate_menus.xml
→ đánh dấu estate là installed
→ commit transaction
```

Nếu một bước lỗi, transaction install/upgrade bị rollback; không nên hiểu rằng
“các file trước chắc chắn đã được cài một nửa”.

### Lệnh tương đương trong project

Khi chạy bằng command line, ý nghĩa thường là:

```powershell
.\venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf -d f_soft_test -i estate --stop-after-init
```

cho lần cài đầu, hoặc:

```powershell
.\venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf -d f_soft_test -u estate --stop-after-init
```

cho lần upgrade. Không chạy `-i` lặp lại để thay thế cho `-u`.

---

## 0.20. Bước 19 — Những gì đã được lưu sau khi install

Sau khi cài thành công, có hai loại trạng thái cần phân biệt.

### Trong Python process / Registry

```text
estate.property model class
field definitions
method definitions
decorators/dependency graph
model inheritance/MRO
```

### Trong PostgreSQL

```text
estate_property table và columns
ir_model / ir_model_fields metadata
ir_ui_view records
ir_actions_act_window record
ir_ui_menu records
ir_model_access records
ir_model_data external-ID mappings
ir_module_module trạng thái installed
```

XML không được browser đọc trực tiếp từ file mỗi lần mở trang. Khi install/upgrade,
XML đã được convert thành record database. Runtime sau đó đọc các record này.

Đây là lý do sửa XML trên ổ đĩa nhưng chưa upgrade thì UI thường vẫn là bản cũ.

---

## 0.21. Bước 20 — App đã sẵn sàng; runtime bắt đầu ở đâu?

Đến đây **luồng khai báo/cài đặt** kết thúc:

```text
Source files
→ module discovery
→ Python registry
→ database schema + metadata
→ app/menu/action/view đã sẵn sàng
```

Từ lúc user vào trình duyệt và bấm menu, ta chuyển sang **luồng runtime**:

```text
User bấm Properties
→ menu record đã lưu trong DB
→ action record đã lưu trong DB
→ web client lấy view metadata
→ ORM search_read estate.property
→ PostgreSQL SELECT estate_property
```

Khi user bấm **New**:

```text
Form + default_get
→ record tạm trên browser
```

Khi user bấm **Save**:

```text
web_save
→ estate.property.create(vals)
→ ACL/defaults/constraints
→ SQL INSERT estate_property
→ trả ID về browser
```

Các phần tiếp theo sẽ phóng to từng mũi tên runtime này.

---

# Phần A — Đọc ảnh giao diện hiện tại

Ảnh hiện tại là màn hình danh sách Properties:

```text
URL: http://localhost:8069/odoo/action-320

Real Estate
└── Advertisements
    └── Properties

[New]  Properties
       [Available] [Search...]

Title | Postcode | Property Type | Bedrooms | ...
Test  |          |               | 1        | ...
```

Thông tin thực tế trong database hiện tại:

| Thành phần | Giá trị |
|---|---|
| External ID của action | `estate.estate_property_action` |
| Database ID của action | `320` |
| Vì vậy URL có | `/odoo/action-320` |
| Model của action | `estate.property` |
| View modes | `list,kanban,form` |
| Default search context | `{'search_default_available': True}` |
| List view database ID | `951` |
| Form view database ID | `952` |
| Search view database ID | `953` |
| Kanban view database ID | `960` |
| Record đang thấy | ID `1`, Title `Test`, state `new` |

Các database ID như `320`, `951` có thể khác ở database khác. External ID như
`estate.estate_property_action` mới là định danh ổn định để code tham chiếu.

---

# Phần B — Bốn ý phải hiểu trước khi lần flow

## B1. XML khai báo, Python thực thi

Ví dụ:

```xml
<field name="expected_price"/>
```

không phải một dòng Python được “chạy”. Nó là metadata nói với Odoo web client:

> Hãy lấy metadata của field `expected_price` từ model và render widget phù hợp.

Ngược lại:

```python
self.env["estate.property"].create(vals)
```

là lời gọi Python thực sự tạo record qua ORM.

## B2. Có hai thời điểm hoàn toàn khác nhau

### Thời điểm install/upgrade module

Odoo đọc manifest, import Python, tạo registry, load ACL/XML và cập nhật schema.

### Thời điểm user thao tác trên UI

Odoo không đọc lại XML file từ ổ đĩa cho mỗi click. Nó dùng view/action/menu đã
được load vào database và registry khi install/upgrade.

Vì vậy sau khi sửa XML hoặc model, thường cần:

```text
restart server + upgrade module
```

## B3. Ba nơi cùng tham gia

```text
Browser                   Odoo Server                 PostgreSQL
-------                   -----------                 ----------
Hiển thị view             Business logic             Lưu rows
Giữ record tạm            ORM/security               CHECK/UNIQUE
Gửi JSON-RPC       →      create/write        →      INSERT/UPDATE
Nhận response      ←      serialize record     ←      RETURNING id
```

## B4. `self` là recordset

Trong Odoo:

```python
self
```

không mặc định là một object duy nhất. Nó là recordset có thể chứa:

- 0 record;
- 1 record;
- nhiều record.

Điều này đặc biệt quan trọng trong `web_save()`:

- `self` rỗng → tạo mới;
- `self` có record → cập nhật.

---

# Phần C — Phóng to loader: Odoo load module như thế nào

Phần 0 đã mô tả cách ta viết app. Phần này phóng to đúng thời điểm Odoo đọc các
khai báo đó trong quá trình khởi động/install/upgrade, trước khi user nhìn thấy
màn hình.

## Bước 0.1 — Odoo tìm thấy addon

### Cấu hình liên quan

```ini
addons_path = addons,my_addons
```

Odoo quét các thư mục trong `addons_path`, thấy:

```text
my_addons/estate/__manifest__.py
```

### Kết quả

Odoo biết có một module kỹ thuật tên `estate`.

## Bước 0.2 — Odoo đọc manifest

### File

```text
my_addons/estate/__manifest__.py
```

### Phần quan trọng

```python
"depends": ["base"],
"data": [
    "security/ir.model.access.csv",
    "views/estate_property_offer_views.xml",
    "views/estate_property_type_views.xml",
    "views/estate_property_tag_views.xml",
    "views/estate_property_views.xml",
    "views/res_users_views.xml",
    "views/estate_menus.xml",
],
```

### Ý nghĩa

- `base` phải load trước `estate`.
- Data files load theo đúng thứ tự từ trên xuống.
- `estate_menus.xml` ở cuối vì menu tham chiếu action được tạo trong view files.

### Kết quả chuyển sang bước kế tiếp

Odoo biết phải import Python package và load những data files nào.

## Bước 0.3 — Chuỗi import đăng ký model

### File 1

```text
my_addons/estate/__init__.py
```

```python
from . import models
```

### File 2

```text
my_addons/estate/models/__init__.py
```

```python
from . import estate_property
from . import estate_property_offer
from . import estate_property_tag
from . import estate_property_type
from . import res_users
```

### File 3

```text
my_addons/estate/models/estate_property.py
```

```python
class EstateProperty(models.Model):
    _name = "estate.property"
```

### Điều gì thực sự xảy ra?

1. Python import class `EstateProperty`.
2. Metaclass/framework Odoo thu thập `_name`, fields, constraints và methods.
3. Model definition được đưa vào registry của database `f_soft_test`.
4. `_name = "estate.property"` mặc định ánh xạ tới table `estate_property`.

### Nếu thiếu import thì sao?

Nếu quên:

```python
from . import estate_property
```

class không được import, model không vào registry, XML/ACL tham chiếu model sẽ lỗi.

## Bước 0.4 — Odoo load ACL

### File

```text
my_addons/estate/security/ir.model.access.csv
```

### Dòng Property

```csv
access_estate_property_staff,access_estate_property_staff,model_estate_property,base.group_user,1,1,1,1
```

### Ý nghĩa bốn số cuối

```text
read   = 1
write  = 1
create = 1
unlink = 1
```

ACL được lưu thành record `ir.model.access` trong PostgreSQL.

## Bước 0.5 — Odoo load views và action

### File

```text
my_addons/estate/views/estate_property_views.xml
```

Odoo tạo các record `ir.ui.view` và `ir.actions.act_window` trong database.

Ví dụ:

```xml
<record id="estate_property_action" model="ir.actions.act_window">
```

tạo external ID:

```text
estate.estate_property_action
```

## Bước 0.6 — Odoo load menus

### File

```text
my_addons/estate/views/estate_menus.xml
```

Odoo tạo các record `ir.ui.menu`. Menu cuối trỏ tới action đã tồn tại.

### Kết thúc giai đoạn 0

Sau install/upgrade:

- model nằm trong registry;
- table/columns/constraints tồn tại;
- ACL nằm trong database;
- views/actions/menus nằm trong database;
- browser có thể bắt đầu sử dụng ứng dụng.

---

# Phần D — Giai đoạn 1: mở màn hình Properties như ảnh

## Bước 1 — User bấm Real Estate

### Bạn làm gì?

Bấm ứng dụng **Real Estate**.

### File khai báo

```text
my_addons/estate/views/estate_menus.xml
```

```xml
<menuitem id="estate_menu_root" name="Real Estate" sequence="10"/>
```

### Điều Odoo làm

Web client đã tải menu tree của user. Nó hiển thị root menu nếu user nhìn thấy ít
nhất một menu con/action phù hợp quyền.

### Kết quả

Thanh menu hiện `Advertisements` và `Configuration`.

## Bước 2 — User bấm Advertisements → Properties

### Bạn làm gì?

Bấm menu **Properties**.

### File và dòng

`estate_menus.xml`, dòng 9–10:

```xml
<menuitem id="estate_menu_property_list" name="Properties"
          parent="estate_menu_properties" action="estate_property_action"/>
```

### Dòng kích hoạt quan trọng

```xml
action="estate_property_action"
```

### Input

```text
Menu external ID: estate.estate_menu_property_list
```

### Output

```text
Action external ID: estate.estate_property_action
```

### Bước tiếp theo

Web client yêu cầu thông tin window action.

## Bước 3 — Odoo resolve Window Action

### File và dòng

`estate_property_views.xml`, dòng 214–218:

```xml
<record id="estate_property_action" model="ir.actions.act_window">
    <field name="name">Properties</field>
    <field name="res_model">estate.property</field>
    <field name="view_mode">list,kanban,form</field>
    <field name="context">{'search_default_available': True}</field>
</record>
```

### Input

```text
estate.estate_property_action
```

### Odoo đọc được

```text
res_model  = estate.property
view_mode  = list,kanban,form
context    = {'search_default_available': True}
```

### Output

Web client biết:

1. Cần thao tác với model `estate.property`.
2. View đầu tiên là list.
3. Có thể chuyển sang kanban/form.
4. Phải bật search filter tên `available`.

### Liên hệ với URL trong ảnh

Action này có database ID `320`, nên URL là:

```text
/odoo/action-320
```

Không hardcode `320` vào XML/Python vì ID này phụ thuộc database.

## Bước 4 — Web client lấy List View

### File

```text
my_addons/estate/views/estate_property_views.xml
```

### Record view

```xml
<record id="estate_property_view_list" model="ir.ui.view">
    <field name="model">estate.property</field>
    <field name="arch" type="xml">
        <list string="Properties">
            ...
        </list>
    </field>
</record>
```

### Những cột trong ảnh đến từ đâu?

```xml
<field name="name"/>
<field name="postcode"/>
<field name="property_type_id"/>
<field name="bedrooms"/>
<field name="living_area"/>
<field name="expected_price"/>
<field name="selling_price"/>
<field name="tag_ids" .../>
```

Mapping:

| XML field | Cột trong ảnh |
|---|---|
| `name` | Title |
| `postcode` | Postcode |
| `property_type_id` | Property Type |
| `bedrooms` | Bedrooms |
| `living_area` | Living Area |
| `expected_price` | Expected Price |
| `selling_price` | Selling Price |
| `tag_ids` | Tags |

### Kết quả

Web client biết cần yêu cầu server đọc những field nào.

## Bước 5 — Search View bật filter Available

### Vì sao ảnh có chip `Available`?

Action gửi context:

```python
{"search_default_available": True}
```

Prefix:

```text
search_default_ + available
```

trỏ tới filter có `name="available"`:

```xml
<filter name="available"
        string="Available"
        domain="[('state', 'in', ('new', 'offer_received'))]"/>
```

### Domain gửi tới ORM

```python
[("state", "in", ("new", "offer_received"))]
```

### Kết quả

Record state `offer_accepted`, `sold`, `canceled` không xuất hiện trong list mặc
định của action này.

## Bước 6 — Web client yêu cầu dữ liệu Property

Web client gọi RPC đọc danh sách với các thông tin dạng:

```text
model  = estate.property
domain = [('state', 'in', ('new', 'offer_received'))]
fields = [name, postcode, property_type_id, bedrooms, ...]
order  = id desc
```

ORM thực hiện logic tương đương:

```python
properties = self.env["estate.property"].search(domain, order="id desc")
values = properties.read(fields)
```

ORM sinh SQL `SELECT`, PostgreSQL trả record ID `1`, Title `Test`, state `new`.

### Kết quả trên ảnh

```text
1-1 / 1
Test | ... | Expected Price 10.00 | Selling Price 9.00
```

Đây là điểm kết thúc luồng **mở list**. Chưa có record mới được tạo.

---

# Phần E — Giai đoạn 2: user bấm New

## Bước 7 — Nút New đến từ đâu?

Bạn không khai báo:

```xml
<button string="New"/>
```

Web client chuẩn tự hiển thị nút **New** vì:

- action có quyền mở model;
- list/form không đặt `create="false"`;
- user có ACL `perm_create=1`.

## Bước 8 — User bấm New

### Bạn làm gì?

Bấm nút **New** trong ảnh.

### Browser làm gì?

Browser tạo một client-side record chưa có `resId`:

```text
resModel = estate.property
resId    = false
```

### Quan trọng

Tại bước này:

```text
PostgreSQL chưa có INSERT.
```

Nếu đóng form mà chưa Save, record tạm biến mất.

## Bước 9 — Web client chọn Form View

### File và dòng

`estate_property_views.xml`, dòng 37:

```xml
<record id="estate_property_view_form" model="ir.ui.view">
```

Dòng 41:

```xml
<form string="Property">
```

### Kết quả

Web client render form theo `sheet`, `group`, `notebook`, `page` và các `<field>`.

## Bước 10 — Browser yêu cầu default values

Web client cần biết giá trị ban đầu nên gọi method core:

```text
odoo/orm/models.py:1271 → default_get(fields)
```

### Default lấy từ code custom

`estate_property.py`:

```python
date_availability = fields.Date(
    copy=False,
    default=lambda self: fields.Date.today() + relativedelta(months=3),
)

bedrooms = fields.Integer(default=2)
active = fields.Boolean(default=True)
state = fields.Selection(..., default="new")

user_id = fields.Many2one(
    comodel_name="res.users",
    default=lambda self: self.env.user,
)
```

### Ví dụ output của default_get

```python
{
    "date_availability": date(2027, 1, 8),
    "bedrooms": 2,
    "active": True,
    "state": "new",
    "user_id": 2,
}
```

Giá trị thực phụ thuộc ngày hiện tại và user đăng nhập.

## Bước 11 — Browser ghép defaults vào record tạm

Sau bước này browser có object logic tương tự:

```javascript
{
    resModel: "estate.property",
    resId: false,
    data: {
        name: false,
        expected_price: 0,
        bedrooms: 2,
        state: "new",
        active: true,
        user_id: currentUserId,
        date_availability: "2027-01-08"
    }
}
```

Đây vẫn không phải row PostgreSQL.

---

# Phần F — Giai đoạn 3: user nhập dữ liệu

Giả sử user nhập:

```text
Title            = House A
Expected Price   = 100000
Bedrooms         = 3
Living Area      = 80
Garden           = bật
```

## Bước 12 — User nhập Title

### XML field

`estate_property_views.xml`, dòng 60:

```xml
<field name="name" placeholder="Property title"/>
```

### Python field

`estate_property.py`:

```python
name = fields.Char(string="Title", required=True)
```

### Browser state thay đổi

```javascript
changes.name = "House A"
```

Chưa gọi `create()`.

## Bước 13 — User nhập Expected Price

### XML field

`estate_property_views.xml`, dòng 73:

```xml
<field name="expected_price"/>
```

### Python field

```python
expected_price = fields.Float(required=True)
```

### Browser state

```javascript
changes.expected_price = 100000
```

## Bước 14 — User bật Garden

### Trigger đăng ký ở Python

`estate_property.py`, dòng 146–147:

```python
@api.onchange("garden")
def _onchange_garden(self):
```

### Payload logic gửi lên server

```python
{
    "garden": True,
    "garden_area": 0,
    "garden_orientation": False,
    ...các giá trị form liên quan...
}
```

### Server dựng pseudo-record

Pseudo-record có giá trị form nhưng chưa nằm trong database.

### Method chạy

```python
if self.garden:
    self.garden_area = 10
    self.garden_orientation = "north"
```

### Output trả về browser

```python
{
    "garden_area": 10,
    "garden_orientation": "north",
}
```

### Browser cập nhật form

User thấy Garden Area = 10 và Orientation = North.

### Điều không xảy ra

```text
Không INSERT.
Không COMMIT.
Không bảo đảm onchange chạy nếu create từ import/code.
```

## Bước 15 — Computed Total Area hiển thị

Field:

```python
total_area = fields.Integer(compute="_compute_total_area")
```

Dependency:

```python
@api.depends("living_area", "garden_area")
```

Compute:

```python
property_record.total_area = (
    property_record.living_area + property_record.garden_area
)
```

Với dữ liệu ví dụ:

```text
living_area = 80
garden_area = 10
total_area = 90
```

`total_area` không `store=True`, nên không có column lưu giá trị này; ORM tính khi
cần đọc/hiển thị và cache trong Environment.

---

# Phần G — Giai đoạn 4: user bấm Save

Đây mới là giai đoạn tạo record thực sự.

## Bước 16 — Form Controller yêu cầu record Save

Nút Save chuẩn của Odoo gọi logic web client. Cuối cùng record model chạy:

```text
addons/web/static/src/model/relational_model/record.js:1083
```

```javascript
async _save({ reload = true, onError, nextId } = {}) {
```

Bạn không cần sửa file core này; ta chỉ đọc để hiểu flow.

## Bước 17 — Client xác định Create hay Write

`record.js`, dòng 1087:

```javascript
const creation = !this.resId;
```

### Trường hợp hiện tại

```text
this.resId = false
creation   = true
```

### Nếu đang sửa record ID 1

```text
this.resId = 1
creation   = false
```

## Bước 18 — Client validation cơ bản

Web client kiểm tra form:

```javascript
if (!this._checkValidity({ displayNotification: true })) {
    return false;
}
```

Nó có thể phát hiện required field chưa nhập trước khi gửi RPC.

### Nhưng cần nhớ

Client validation không thay server validation. RPC client khác có thể không dùng
web form, nên server vẫn kiểm tra required/constraints.

## Bước 19 — Client thu thập changes

`record.js`, dòng 1104:

```javascript
const changes = this._getChanges();
```

Ví dụ `changes`:

```javascript
{
    name: "House A",
    expected_price: 100000,
    bedrooms: 3,
    living_area: 80,
    garden: true,
    garden_area: 10,
    garden_orientation: "north",
    date_availability: "2027-01-08",
    state: "new",
    active: true,
    user_id: 2
}
```

Computed field `total_area` không được client gửi như một field người dùng nhập.

## Bước 20 — Client gọi ORM service

`record.js`, dòng 1179:

```javascript
records = await this.model.orm.webSave(
    this.resModel,
    this.resId ? [this.resId] : [],
    changes,
    kwargs
);
```

Giá trị thực tế:

```text
this.resModel = "estate.property"
this.resId    = false
ids           = []
changes       = {...}
```

## Bước 21 — Request đi qua HTTP/JSON-RPC

Request logic tương đương:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "model": "estate.property",
    "method": "web_save",
    "args": [[], {
      "name": "House A",
      "expected_price": 100000,
      "bedrooms": 3
    }],
    "kwargs": {
      "context": {},
      "specification": {}
    }
  }
}
```

Đây chỉ là dạng minh họa; payload thật còn chứa context và field specification.

---

# Phần H — Giai đoạn 5: Odoo server xử lý Save

## Bước 22 — RPC dispatcher tìm model

Server dùng registry hiện tại:

```python
env["estate.property"]
```

Registry trả model class tổng hợp từ tất cả inheritance đang cài.

Nếu model name sai:

```text
KeyError / model not found
```

## Bước 23 — Server gọi `web_save()`

### File core

```text
addons/web/models/models.py:90
```

### Code

```python
def web_save(self, vals, specification, next_id=None):
    if self:
        self.write(vals)
    else:
        self = self.create(vals)
    if next_id:
        self = self.browse(next_id)
    return self.with_context(bin_size=True).web_read(specification)
```

## Bước 24 — `web_save()` phân nhánh

### Record mới

RPC gửi `ids=[]`, nên recordset `self` rỗng:

```python
bool(self) is False
```

Odoo chạy:

```python
self = self.create(vals)
```

### Record đã tồn tại

Nếu RPC gửi `ids=[1]`, recordset có ID 1:

```python
bool(self) is True
```

Odoo chạy:

```python
self.write(vals)
```

### Dòng trực tiếp kích hoạt tạo record

```python
self = self.create(vals)
```

Đây là câu trả lời ngắn nhất cho câu hỏi “dòng nào tạo record khi bấm Save?”.

## Bước 25 — Python tìm implementation của `create()`

`EstateProperty` khai báo:

```python
class EstateProperty(models.Model):
```

Nhưng file không có:

```python
def create(...):
```

Python tìm method theo MRO:

```text
EstateProperty
→ models.Model
→ BaseModel
```

Vì vậy nó dùng core method:

```text
odoo/orm/models.py:4617
```

```python
@api.model_create_multi
def create(self, vals_list):
```

Property vẫn có đầy đủ `create`, `write`, `unlink`, `search`, `browse` nhờ kế
thừa ORM.

## Bước 26 — Decorator chuẩn hóa input

Web save có thể gọi:

```python
self.create(vals)
```

với một dict. `@api.model_create_multi` chuẩn hóa để implementation nhận:

```python
vals_list = [vals]
```

Nhờ đó cùng method hỗ trợ tạo một hoặc nhiều record.

## Bước 27 — ORM kiểm tra quyền Create

Core `Model.create()` gọi:

```python
self.check_access("create")
```

Odoo tìm ACL của model và group user.

ACL module:

```csv
model_estate_property,base.group_user,1,1,1,1
```

### Nếu được phép

Flow tiếp tục.

### Nếu không được phép

Odoo raise `AccessError`:

```text
Không INSERT
Không chạy custom constraint phía sau
Transaction rollback
Browser hiển thị Access Error
```

## Bước 28 — ORM kiểm tra field access và tên field

Odoo thu thập keys trong `vals`:

```python
field_names = {
    "name",
    "expected_price",
    "bedrooms",
    ...
}
```

Mỗi tên được đối chiếu với:

```python
self._fields
```

Nếu gửi:

```python
{"not_a_real_field": 123}
```

ORM raise:

```text
ValueError: Invalid field 'not_a_real_field' in 'estate.property'
```

## Bước 29 — ORM chuẩn bị create values

Core gọi:

```text
odoo/orm/models.py:4775
```

```python
_prepare_create_values(vals_list)
```

Nhiệm vụ:

1. Bổ sung defaults còn thiếu.
2. Xử lý context `default_*`.
3. Chuyển Python value sang kiểu field phù hợp.
4. Phân loại stored/computed/inverse/inherited fields.
5. Chuẩn bị relational commands.
6. Xử lý required/precomputed fields.

### Input ví dụ

```python
{
    "name": "House A",
    "expected_price": 100000,
    "garden": True,
}
```

### Output logic sau defaults

```python
{
    "name": "House A",
    "expected_price": 100000.0,
    "garden": True,
    "bedrooms": 2,
    "active": True,
    "state": "new",
    "user_id": 2,
    "date_availability": date(...),
}
```

## Bước 30 — ORM gọi `_create()`

Core `create()` gọi tại:

```text
odoo/orm/models.py:4717
```

```python
records = self._create(data_list)
```

Implementation thấp hơn:

```text
odoo/orm/models.py:4856
```

```python
def _create(self, data_list):
```

Đây là tầng rất gần SQL. Custom addon thông thường không override `_create()`.

## Bước 31 — ORM sinh SQL INSERT

ORM ánh xạ:

```text
Model: estate.property
Table: estate_property
```

SQL có ý nghĩa tương tự:

```sql
INSERT INTO estate_property (
    name,
    expected_price,
    bedrooms,
    living_area,
    garden,
    garden_area,
    garden_orientation,
    active,
    state,
    user_id,
    date_availability,
    create_uid,
    create_date,
    write_uid,
    write_date
)
VALUES (...)
RETURNING id;
```

SQL thật do Odoo sinh có thể khác thứ tự column và cách batch values.

## Bước 32 — Automatic fields được điền

Odoo tự quản lý:

```text
id
create_uid
create_date
write_uid
write_date
```

Bạn không cần khai báo chúng trong model.

Ví dụ PostgreSQL trả:

```text
id = 2
```

ORM tạo recordset:

```python
estate.property(2,)
```

## Bước 33 — PostgreSQL kiểm tra SQL constraints

Model khai báo:

```python
_expected_price_positive = models.Constraint(
    "CHECK(expected_price > 0)",
    "The expected price must be strictly positive.",
)

_selling_price_positive = models.Constraint(
    "CHECK(selling_price >= 0)",
    "The selling price must be positive.",
)
```

### Trường hợp hợp lệ

```text
expected_price = 100000 > 0 → pass
selling_price  = 0 >= 0     → pass
```

### Trường hợp sai

```text
expected_price = -1
```

PostgreSQL từ chối row và Odoo rollback transaction.

## Bước 34 — Odoo chạy Python constraints

Decorator:

```python
@api.constrains("selling_price", "expected_price")
def _check_selling_price(self):
```

Method chạy khi create/write có field liên quan.

Property mới thường có:

```text
selling_price = 0
```

nên code:

```python
if not property_record.selling_price:
    continue
```

bỏ qua kiểm tra 90% cho đến khi accept offer.

Nếu có giá bán:

```python
minimum_price = expected_price * 0.9
```

và `selling_price < minimum_price`, method raise `ValidationError`, toàn bộ create
hoặc write rollback.

## Bước 35 — Computed fields được invalidated/recomputed

`total_area` phụ thuộc:

```python
@api.depends("living_area", "garden_area")
```

`best_price` phụ thuộc:

```python
@api.depends("offer_ids.price")
```

Khi dependency thay đổi, ORM đánh dấu cache liên quan cần tính lại. Vì hai field
không `store=True`, giá trị được tính khi read thay vì tạo column lưu riêng.

## Bước 36 — Transaction chưa chắc đã commit ngay tại `create()`

`create()` trả record không đồng nghĩa transaction đã commit độc lập.

Request còn có thể làm tiếp:

- chạy business logic khác;
- tạo related records;
- serialize response;
- gặp exception.

Odoo quản lý transaction theo request. Chỉ khi toàn request thành công mới commit.

Không tự gọi `cr.commit()` trong business method thông thường.

---

# Phần I — Giai đoạn 6: trả record về browser

## Bước 37 — `web_save()` đọc lại record

Sau `create()`:

```python
self = self.create(vals)
```

`self` không còn rỗng. Nó là recordset mới, ví dụ:

```python
estate.property(2,)
```

Cuối `web_save()`:

```python
return self.with_context(bin_size=True).web_read(specification)
```

`web_read()` đọc những field web client cần để render lại form.

## Bước 38 — Server trả JSON response

Response logic tương tự:

```json
[
  {
    "id": 2,
    "name": "House A",
    "expected_price": 100000.0,
    "bedrooms": 3,
    "state": "new",
    "total_area": 90
  }
]
```

## Bước 39 — Browser gắn ID cho record

Web client lấy:

```javascript
const resId = records[0].id;
```

Trước Save:

```text
resId = false
```

Sau Save:

```text
resId = 2
```

Từ đây record không còn là record mới.

## Bước 40 — Lần Save tiếp theo dùng `write()`

Vì record có `resId=2`, lần sau `web_save()` nhận recordset có ID:

```python
if self:
    self.write(vals)
```

Luồng cập nhật:

```text
Save
→ web_save
→ write(vals)
→ ACL write + record rules
→ UPDATE estate_property
→ SQL/Python constraints
→ COMMIT
→ web_read
→ cập nhật form
```

---

# Phần J — Luồng lỗi cụ thể

## J1. Thiếu Title

```text
User để trống Title
→ client thấy required field
→ _checkValidity() fail
→ không gửi RPC
→ form báo field bắt buộc
```

Nếu RPC client cố tình gửi thiếu, server/database vẫn kiểm tra required.

## J2. User không có quyền Create

```text
Save
→ web_save
→ create
→ check_access('create')
→ ACL từ chối
→ AccessError
→ rollback
→ không INSERT
```

## J3. Expected Price âm

```text
Save
→ web_save
→ create
→ _create
→ INSERT
→ CHECK(expected_price > 0) fail
→ PostgreSQL error được Odoo ánh xạ thành validation message
→ rollback
→ browser hiện lỗi
```

## J4. Python constraint thất bại

```text
write selling_price
→ UPDATE/flush
→ _check_selling_price
→ float_compare(...) < 0
→ ValidationError
→ rollback toàn request
```

## J5. Tại sao rollback quan trọng?

Nếu request tạo nhiều record liên quan:

```text
Tạo A thành công
Tạo B lỗi
```

transaction rollback bảo đảm:

```text
A cũng không bị lưu dở dang.
```

---

# Phần K — Tạo Offer: flow có custom `create()`

Property dùng core `create()` trực tiếp. Offer có override, nên đây là ví dụ tốt
để hiểu custom business logic chen vào ORM lifecycle.

## Bước K1 — User thêm dòng trong tab Offers

Form Property có:

```xml
<field name="offer_ids">
    <list editable="bottom">
        <field name="price"/>
        <field name="partner_id"/>
        ...
    </list>
</field>
```

`offer_ids` là One2many tới:

```text
estate.property.offer
```

Inverse field là:

```python
property_id = fields.Many2one("estate.property", ...)
```

## Bước K2 — Browser chuẩn bị values

Ví dụ:

```python
{
    "price": 95000,
    "partner_id": 15,
    "property_id": 2,
    "validity": 7,
}
```

Many2one values trong ORM create dict là integer ID, không phải recordset.

## Bước K3 — `web_save()` gọi create

Giống Property:

```text
addons/web/models/models.py:web_save()
```

Recordset Offer mới rỗng nên:

```python
self.create(vals)
```

## Bước K4 — Python tìm thấy custom create trước

File:

```text
my_addons/estate/models/estate_property_offer.py
```

Dòng 84–85:

```python
@api.model_create_multi
def create(self, vals_list):
```

MRO lần này:

```text
EstatePropertyOffer.create
→ super().create
→ models.Model.create
```

## Bước K5 — Kiểm tra batch trước INSERT

Method duyệt từng `values`:

```python
for values in vals_list:
```

Lấy property recordset từ integer ID:

```python
property_record = self.env["estate.property"].browse(
    values.get("property_id")
)
```

Lấy giá cao nhất hiện tại:

```python
current_best = batch_best_prices.get(
    property_record.id,
    property_record.best_price,
)
```

So sánh offer mới:

```python
if current_best and float_compare(
    offer_price,
    current_best,
    precision_digits=2,
) < 0:
    raise UserError(...)
```

Nếu offer thấp hơn, method dừng trước `super()` nên chưa INSERT.

## Bước K6 — Custom method gọi ORM chuẩn

Dòng 119:

```python
offers = super().create(vals_list)
```

Đây là điểm cực kỳ quan trọng.

`super().create()` thực hiện:

```text
ACL
→ defaults
→ conversions
→ INSERT estate_property_offer
→ CHECK(price > 0)
→ trả recordset offers
```

Nếu bỏ `super().create()`:

- không có INSERT;
- không có ID;
- không có recordset thật để return;
- ORM lifecycle bị phá.

## Bước K7 — SQL constraint Offer chạy

```python
_price_positive = models.Constraint(
    "CHECK(price > 0)",
    "The offer price must be strictly positive.",
)
```

Giá 0 hoặc âm bị PostgreSQL từ chối.

## Bước K8 — Cập nhật Property state

Sau khi Offer tồn tại:

```python
offers.property_id.filtered(
    lambda property_record: property_record.state == "new"
).state = "offer_received"
```

Từng phần:

```text
offers.property_id
```

lấy tất cả Property cha của batch Offers.

```text
.filtered(lambda ... state == "new")
```

chỉ giữ Property đang New.

```text
.state = "offer_received"
```

ORM ghi state mới, tương đương `write({"state": "offer_received"})`.

## Bước K9 — Best Price được invalidated

Property khai báo:

```python
@api.depends("offer_ids.price")
def _compute_best_price(self):
```

Offer mới làm dependency `offer_ids.price` đổi. ORM invalidates cache;
`best_price` được tính lại khi đọc:

```python
max(property_record.offer_ids.mapped("price"), default=0.0)
```

## Bước K10 — Một transaction duy nhất

Tạo Offer và đổi Property state cùng transaction:

```text
Offer INSERT thành công
Property state update lỗi
→ toàn bộ transaction rollback
→ Offer cũng không còn
```

## Bước K11 — Return recordset

```python
return offers
```

`web_save()` dùng recordset này để `web_read()` và trả ID Offer cho browser.

---

# Phần L — So sánh Property và Offer

| Bước | Tạo Property | Tạo Offer |
|---|---|---|
| UI bắt đầu | Nút New của list | Dòng mới trong One2many |
| Server entry | `web_save()` | `web_save()` |
| Recordset ban đầu | Rỗng | Rỗng |
| Method được gọi | `create(vals)` | `create(vals)` |
| Custom override | Không | Có |
| Method đầu tiên | `models.Model.create()` | `EstatePropertyOffer.create()` |
| Check custom trước INSERT | Không | Không thấp hơn best offer |
| Core INSERT | Tự qua inheritance | Qua `super().create()` |
| SQL constraint | Giá kỳ vọng/bán | Offer price > 0 |
| Side effect | Không có custom | Property → Offer Received |
| Return | Property recordset | Offer recordset |

---

# Phần M — Tạo record bằng Python, không qua UI

Code khác có thể gọi trực tiếp:

```python
property_record = self.env["estate.property"].create(
    {
        "name": "House A",
        "expected_price": 100_000,
    }
)
```

Flow lúc này:

```text
Python code
→ env["estate.property"]
→ Model.create
→ ACL/security
→ defaults/conversions
→ INSERT
→ constraints
→ transaction
```

Những bước bị bỏ qua:

```text
Menu
Action
View
JavaScript
web_save
onchange
```

Điều vẫn luôn chạy:

```text
ORM create
ACL
required fields
SQL constraints
Python constraints
```

Đây là lý do không đặt business rule bắt buộc trong XML hoặc onchange.

---

# Phần N — Sơ đồ tuần tự đầy đủ

```text
USER             WEB CLIENT           ODOO SERVER             POSTGRESQL
 │                    │                     │                       │
 │ Click Properties   │                     │                       │
 ├───────────────────►│                     │                       │
 │                    │ load action 320     │                       │
 │                    ├────────────────────►│ read ir.actions...    │
 │                    │                     ├──────────────────────►│
 │                    │                     │◄──────────────────────┤
 │                    │◄────────────────────┤ action metadata       │
 │                    │                     │                       │
 │                    │ load list/search    │                       │
 │                    ├────────────────────►│ search/read property  │
 │                    │                     ├──────────────────────►│ SELECT
 │                    │                     │◄──────────────────────┤ rows
 │  Show list         │◄────────────────────┤                       │
 │◄───────────────────┤                     │                       │
 │                    │                     │                       │
 │ Click New          │                     │                       │
 ├───────────────────►│ default_get         │                       │
 │                    ├────────────────────►│                       │
 │                    │◄────────────────────┤ defaults              │
 │  Show empty form   │                     │                       │
 │◄───────────────────┤                     │                       │
 │                    │                     │                       │
 │ Toggle Garden      │ onchange            │                       │
 ├───────────────────►├────────────────────►│ _onchange_garden      │
 │                    │◄────────────────────┤ garden_area=10        │
 │  Form updates      │                     │                       │
 │◄───────────────────┤                     │                       │
 │                    │                     │                       │
 │ Click Save         │                     │                       │
 ├───────────────────►│ _save()             │                       │
 │                    │ webSave/web_save    │                       │
 │                    ├────────────────────►│ self.create(vals)     │
 │                    │                     │ check_access(create)  │
 │                    │                     │ prepare values        │
 │                    │                     │ _create               │
 │                    │                     ├──────────────────────►│ INSERT
 │                    │                     │                       │ CHECK constraints
 │                    │                     │◄──────────────────────┤ RETURNING id
 │                    │                     │ Python constraints    │
 │                    │                     │ web_read              │
 │                    │                     │ COMMIT                 │
 │                    │◄────────────────────┤ record + id           │
 │  Show saved form   │                     │                       │
 │◄───────────────────┤                     │                       │
```

---

# Phần O — Bảng “file nào gọi file nào?”

## Khi mở màn hình

| Thứ tự | File/record | Vai trò |
|---:|---|---|
| 1 | `estate_menus.xml` | Menu trỏ tới action |
| 2 | `estate_property_action` | Chọn model và view modes |
| 3 | `estate_property_view_list` | Chọn columns |
| 4 | `estate_property_view_search` | Tạo filter/domain |
| 5 | Odoo web client | Gửi RPC search/read |
| 6 | ORM `estate.property` | Security + query |
| 7 | PostgreSQL | SELECT rows |
| 8 | Web client | Render list như ảnh |

## Khi tạo mới

| Thứ tự | File/method | Vai trò |
|---:|---|---|
| 1 | Web client nút New | Tạo record tạm |
| 2 | `estate_property_view_form` | Render form |
| 3 | `Model.default_get()` | Lấy default values |
| 4 | `_onchange_garden()` | Hỗ trợ form nếu Garden đổi |
| 5 | `record.js:_save()` | Thu thập changes |
| 6 | ORM service `webSave()` | Gửi RPC |
| 7 | `web/models/models.py:web_save()` | Chọn create/write |
| 8 | `Model.create()` | ACL + prepare values |
| 9 | `Model._create()` | Sinh INSERT |
| 10 | PostgreSQL | Lưu row + SQL constraints |
| 11 | `_check_selling_price()` | Python validation |
| 12 | `web_read()` | Đọc record trả về |
| 13 | Web client | Gắn `resId` và render |

---

# Phần P — Breakpoint để tự nhìn flow

## Debug Property Create

Đặt breakpoint theo thứ tự:

### Breakpoint 1

```text
addons/web/models/models.py:90
method: web_save
```

Quan sát:

```text
self
vals
bool(self)
```

Expected khi tạo mới:

```text
self = estate.property()
bool(self) = False
```

### Breakpoint 2

```text
odoo/orm/models.py:4617
method: create
```

Quan sát:

```text
self._name
vals_list
self.env.user
self.env.context
```

Expected:

```text
self._name = "estate.property"
```

### Breakpoint 3

```text
odoo/orm/models.py:4717
records = self._create(data_list)
```

Quan sát values đã được ORM chuẩn hóa.

### Breakpoint 4

```text
my_addons/estate/models/estate_property.py:161
method: _check_selling_price
```

Quan sát:

```text
property_record.id
property_record.expected_price
property_record.selling_price
```

## Debug Offer Create

Thêm breakpoint đầu tiên tại:

```text
my_addons/estate/models/estate_property_offer.py:85
method: create
```

Quan sát:

```text
vals_list
values["property_id"]
property_record
property_record.best_price
```

Sau đó Step Into:

```python
offers = super().create(vals_list)
```

Quan sát trước và sau dòng này:

```text
Trước: chưa có offer ID
Sau: offers là recordset có ID
```

---

# Phần Q — Các nhầm lẫn phổ biến

## “Bấm New là đã create chưa?”

Chưa. New chỉ tạo record tạm và lấy defaults. Save mới gọi `web_save → create`.

## “XML field có gọi Python field không?”

Không theo kiểu gọi function. XML dùng tên field để web client đọc metadata model,
render widget và thu thập giá trị.

## “Tại sao Property không có def create mà vẫn tạo được?”

Vì kế thừa `models.Model.create()`.

## “Onchange có lưu database không?”

Không trực tiếp. Nó cập nhật pseudo-record/form state. Save sau đó mới ghi values.

## “Required ở form có đủ an toàn không?”

Không. Server/ORM/database vẫn phải kiểm tra vì request có thể không đến từ form.

## “SQL constraint và Python constraint chạy cái nào trước?”

Phụ thuộc flush/lifecycle cụ thể, nhưng không nên viết business logic dựa vào giả
định thứ tự giữa hai loại. Cả hai đều có thể làm transaction rollback.

## “create trả record hay ID?”

ORM `create()` trả recordset. Dùng `.id` khi cần integer ID.

## “self.env giống DI container không?”

Chỉ giống ở chỗ truy cập model/service. `env` còn chứa cursor, user, company,
context, registry và cache của transaction.

## “Có nên gọi SQL INSERT trực tiếp?”

Không cho CRUD thông thường. SQL trực tiếp dễ bỏ qua ACL, record rules, cache,
computed fields, constraints và inheritance hooks.

---

# Phần R — Checklist đọc một flow Odoo bất kỳ

Khi gặp một tính năng mới, lần theo theo thứ tự:

1. Menu XML ID nào?
2. Menu trỏ tới action nào?
3. Action có `res_model` gì?
4. View modes và context/domain là gì?
5. View hiển thị những field/button nào?
6. Button là `type="object"` hay `type="action"`?
7. Nếu Save, model có override `create/write` không?
8. Nếu có override, `super()` nằm ở đâu?
9. ACL/record rule nào áp dụng?
10. SQL constraints nào áp dụng?
11. `@api.constrains` nào áp dụng?
12. Computed fields nào bị invalidate?
13. Tất cả có nằm trong cùng transaction không?
14. Response/action nào quay về client?

---

# Phần S — Bài tập tự thực hành

## Bài 1: theo dõi Property Create

1. Đặt breakpoint ở `web_save()`.
2. Mở Properties.
3. Bấm New.
4. Xác nhận breakpoint chưa dừng chỉ vì bấm New.
5. Nhập Title và Expected Price.
6. Bấm Save.
7. Kiểm tra `self` rỗng và `vals` có dữ liệu form.
8. Step Into `self.create(vals)`.
9. Theo dõi `Model.create()` và `_create()`.
10. Kiểm tra ID trả về.

## Bài 2: phân biệt Create và Write

1. Sau khi lưu record mới, giữ breakpoint ở `web_save()`.
2. Sửa Bedrooms.
3. Bấm Save lần nữa.
4. Xác nhận `self` có ID.
5. Xác nhận code đi vào `self.write(vals)`, không vào nhánh create.

## Bài 3: xem rollback

1. Tạo Property với Expected Price âm.
2. Theo dõi SQL constraint báo lỗi.
3. Quay lại list.
4. Xác nhận không có record lỗi trong database.

## Bài 4: theo dõi Offer override

1. Tạo một Property giá kỳ vọng 100,000.
2. Tạo Offer 95,000.
3. Dừng ở `EstatePropertyOffer.create()`.
4. Theo dõi `vals_list`, `property_id`, `best_price`.
5. Step qua `super().create()`.
6. Quan sát Offer có ID.
7. Quan sát Property đổi `new → offer_received`.
8. Thử tạo Offer 90,000 và quan sát rollback trước INSERT.

---

# Phần T — Tóm tắt bằng một câu cho mỗi tầng

```text
Menu      chọn Action.
Action    chọn Model và View.
View      mô tả UI và field cần dùng.
Browser   giữ record tạm, chạy onchange và gửi web_save.
web_save  chọn create cho record mới, write cho record có ID.
Model     chứa business logic dùng chung cho mọi client.
ORM       kiểm tra security, defaults, fields và sinh SQL.
Database  lưu row, kiểm tra CHECK/UNIQUE và tham gia transaction.
Server    đọc record mới và trả response.
Browser   nhận ID rồi hiển thị record đã lưu.
```

Điểm kích hoạt tạo record quan trọng nhất là:

```python
# addons/web/models/models.py: khi self là recordset rỗng
self = self.create(vals)
```

Property đi thẳng tới core ORM vì không override `create()`. Offer đi qua custom
`EstatePropertyOffer.create()` trước, rồi quay về core ORM bằng:

```python
offers = super().create(vals_list)
```
