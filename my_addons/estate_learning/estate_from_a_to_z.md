# Xây dựng module Estate Odoo 19 từ A đến Z

Tài liệu này hướng dẫn dựng lại toàn bộ ứng dụng Real Estate từ một thư mục
trống. Mỗi phần đều trả lời bốn câu hỏi:

1. Tạo file nào?
2. Viết code gì?
3. Vì sao cần đoạn code đó?
4. Chạy và kiểm tra kết quả như thế nào?

Code trong tài liệu là một phiên bản hoàn chỉnh, tương ứng với hai module:

```text
estate          → nghiệp vụ bất động sản
estate_account  → kết nối Estate với Accounting để tạo hóa đơn
```

> Tài liệu dùng cú pháp Odoo 19. Đặc biệt, list view dùng thẻ `<list>` và SQL
> constraints dùng `models.Constraint`.

---

# 0. Cách học theo tài liệu này

## 0.1. Tài liệu dành cho người bắt đầu từ đâu?

Bạn chỉ cần biết Python cơ bản:

```text
biến, class, method, list, dict, vòng lặp và exception
```

Bạn chưa cần biết trước ORM, Registry, XML ID, Recordset hay RPC. Những khái niệm
đó sẽ được giải thích đúng lúc chúng xuất hiện.

## 0.2. Công thức đọc mỗi phần

Mỗi lần tạo một file, hãy đi theo thứ tự:

```text
1. Mục tiêu: file này giải quyết vấn đề gì?
2. Code: tự gõ lại code hoàn chỉnh.
3. Giải thích: hiểu từng nhóm dòng.
4. Kết nối: file này nối với file/model nào?
5. Chạy: restart hay upgrade?
6. Kiểm tra: nhìn UI/log/database thấy gì?
7. Cố tình làm sai: quan sát lỗi để hiểu cơ chế.
```

Đừng tạo toàn bộ file rồi mới chạy. Khi sai một dấu XML hoặc quên một import,
bạn sẽ không biết lỗi bắt đầu từ checkpoint nào.

### Chọn đúng cách đọc

Tài liệu có hai chế độ:

```text
Bạn đang tự code lần đầu
→ bắt đầu ở Phần 30
→ làm Bước 1
→ quay về phần được chỉ dẫn để đọc code/giải thích
→ chạy kiểm tra
→ chỉ khi Đạt mới sang bước kế tiếp

Bạn đã có module và cần tra cứu
→ dùng Phần 3.1 để tìm thứ tự file
→ mở thẳng phần của model/view/action cần xem
```

Không nên đọc từ Phần 4 rồi copy toàn bộ tới Phần 18 trong một lượt. Các phần đó
là **bản code cuối để đối chiếu**; Phần 30 mới là đường học dành cho người tự gõ.

## 0.3. Ba ký hiệu tư duy xuyên suốt

### Khai báo

```python
name = fields.Char(required=True)
```

Đây là metadata để ORM build field/schema, không phải một câu INSERT record.

### Thực thi

```python
self.env["estate.property"].create(values)
```

Đây là lời gọi thực sự đi qua ORM và có thể sinh SQL INSERT.

### Liên kết

```xml
<field name="name"/>
```

XML không tạo lại field. Nó tham chiếu field `name` đã được Python đăng ký.

## 0.4. Bốn tầng phải luôn tách riêng

```text
Python model    → dữ liệu và business logic
Security        → ai được làm gì
XML view/action → nhìn thấy và điều hướng thế nào
PostgreSQL      → rows, columns, constraints và transaction
```

Ví dụ `required=True` trên Python bảo vệ model; dấu bắt buộc trên Form chỉ là UX.
Nếu chỉ sửa XML, import/API vẫn có thể bỏ qua giao diện.

## 0.5. “Chạy lại” nghĩa là gì?

| Bạn vừa sửa | Cần làm |
|---|---|
| Method Python | Restart server |
| Thêm/sửa field Python | Restart + upgrade module |
| XML view/action/menu | Upgrade module |
| ACL/record rule CSV/XML | Upgrade module |
| Manifest `data`/dependency | Upgrade module |
| Chỉ dữ liệu trên Form | Không restart/upgrade |

Restart chỉ tạo Python process mới. Upgrade mới đọc lại data files và đồng bộ
schema/metadata vào database.

## 0.6. Quy tắc “không hiểu thì lần ngược”

Khi thấy một thành phần trên UI, lần ngược:

```text
Nút Sold
→ XML button name="action_sold", type="object"
→ model của Form là estate.property
→ Registry tìm estate.property.action_sold
→ estate_account có override không?
→ super gọi method nào?
→ method ghi field/table nào?
```

Khi thấy một field:

```text
Buyer trên Form
→ <field name="buyer_id"/>
→ estate.property._fields["buyer_id"]
→ Many2one comodel res.partner
→ column estate_property.buyer_id
→ foreign record res_partner.id
```

---

# 1. Kết quả cuối cùng chúng ta sẽ xây dựng

## 1.1. Các model

```text
estate.property
├── thông tin bất động sản
├── workflow New → Offer Received → Offer Accepted → Sold
├── computed Total Area và Best Price
├── onchange Garden
└── kiểm tra giá bán tối thiểu 90%

estate.property.offer
├── giá đề nghị và người đề nghị
├── validity/deadline
├── Accept/Refuse
└── không cho Offer mới thấp hơn Best Offer

estate.property.type
├── danh mục Apartment/House/Villa
└── stat button đếm Offer

estate.property.tag
└── nhãn màu Many2many

res.users (mở rộng)
└── danh sách Property mà Salesperson phụ trách
```

## 1.2. Giao diện

```text
Real Estate
├── Advertisements
│   └── Properties
└── Configuration
    ├── Property Types
    └── Property Tags
```

Property có List, Form, Search và Kanban view. Form có ba tab:

```text
Description | Offers | Other Info
```

## 1.3. Luồng nghiệp vụ

```text
Tạo Property
→ tạo Offer
→ Accept Offer
→ Buyer và Selling Price được cập nhật
→ bấm Sold
→ estate_account tạo Draft Customer Invoice
```

---

# 2. Chuẩn bị môi trường

## 2.1. Cấu hình addons path

File `odoo.conf` phải chứa custom addons:

```ini
[options]
addons_path = odoo/addons,my_addons
http_port = 8069
```

Đường dẫn chuẩn có thể khác theo cấu trúc source:

```text
Nếu project có project-root/odoo/addons → dùng odoo/addons,my_addons
Nếu project có project-root/addons      → dùng addons,my_addons
Nếu đã có nhiều addons paths            → giữ nguyên và thêm my_addons vào cuối
```

Không thay mù quáng đường dẫn đang chạy tốt. Khi start server, log `addons paths`
phải chứa đường dẫn tuyệt đối tới `my_addons`.

Các thiết lập database phụ thuộc máy của bạn. Tìm nhanh trong PowerShell:

```powershell
Select-String -Path .\odoo.conf -Pattern '^db_name|^db_host|^db_port|^addons_path'
```

Nếu `db_name` trống hoặc không đúng database đang mở trên web, xem log server hoặc
database selector. Mọi lệnh `-i/-u/shell/test` phải dùng đúng database đó.

## 2.2. Môi trường Python đúng

Project này dùng `.venv`, có dấu chấm ở đầu:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf
```

Không dùng nhầm folder `venv` cũ.

Kiểm tra interpreter:

```powershell
.\.venv\Scripts\python.exe --version
```

Nếu project mới chưa có `.venv`, đừng copy đường dẫn này một cách máy móc. Hãy
chọn đúng Python environment đã cài dependencies của Odoo.

## 2.3. Ba lệnh cần nhớ

Chạy server:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf
```

Nếu source distribution không có file `odoo-bin` ở root nhưng có package
`odoo/__main__.py`, dùng:

```powershell
.\.venv\Scripts\python.exe -m odoo -c .\odoo.conf
```

Trong toàn bộ tài liệu, lệnh dùng `odoo-bin`. Nếu project của bạn dùng
`python -m odoo`, chỉ thay phần `.\odoo-bin` bằng `-m odoo`; các option
phía sau giữ nguyên.

Cài module lần đầu, thay `DATABASE_NAME` bằng database của bạn:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -i estate --stop-after-init --no-http
```

Upgrade sau khi sửa code/XML:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -u estate --stop-after-init --no-http
```

Trong PowerShell, hãy copy nguyên một dòng như trên. Đừng tự thêm dấu `\` ở cuối
dòng; đó là cách xuống dòng của shell Linux, không phải PowerShell.

Quy tắc thực hành:

```text
Sửa Python → restart server; nếu có field/schema mới thì upgrade
Sửa XML    → upgrade module
Sửa CSV    → upgrade module
Sửa manifest/data → upgrade module
```

---

# 3. Tạo cấu trúc thư mục

Tạo cấu trúc:

```text
my_addons/
└── estate/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── constants.py
    │   ├── estate_property.py
    │   ├── estate_property_offer.py
    │   ├── estate_property_tag.py
    │   ├── estate_property_type.py
    │   └── res_users.py
    ├── security/
    │   └── ir.model.access.csv
    ├── views/
    │   ├── estate_property_offer_views.xml
    │   ├── estate_property_type_views.xml
    │   ├── estate_property_tag_views.xml
    │   ├── estate_property_views.xml
    │   ├── res_users_views.xml
    │   └── estate_menus.xml
    └── tests/
        ├── __init__.py
        └── test_estate.py
```

Tên folder `estate` là technical module name. Nó xuất hiện trong:

```text
-u estate
estate.estate_property_action
depends=["estate"]
```

## 3.1. Thứ tự tạo file tuyệt đối

Nếu đang code lại từ đầu, hãy tạo file đúng thứ tự dưới đây. Không nhảy thẳng tới
view hoặc menu khi model/action mà chúng tham chiếu chưa tồn tại.

| Thứ tự | File | Lý do làm ở thời điểm này |
|---:|---|---|
| 1 | `estate/__manifest__.py` bản tối thiểu | Giúp Odoo nhận diện module |
| 2 | `estate/__init__.py` | Mở chuỗi import Python |
| 3 | `estate/models/__init__.py` rỗng | Chuẩn bị package models |
| 4 | `estate/models/constants.py` | Khai báo state/status/default dùng chung trước khi model tham chiếu |
| 5 | `estate/models/estate_property.py` bản tối thiểu | Tạo model trung tâm trước |
| 6 | cập nhật `models/__init__.py` | Đăng ký Property vào Registry |
| 7 | `security/ir.model.access.csv` dòng Property | Cho Internal User dùng model |
| 8 | `views/estate_property_views.xml` bản tối thiểu | Tạo List, Form và Action |
| 9 | `views/estate_menus.xml` bản tối thiểu | Menu chỉ tạo sau khi Action có mặt |
| 10 | cập nhật `__manifest__.py` | Load ACL → View/Action → Menu đúng thứ tự |
| 11 | thêm scalar fields/compute/onchange vào Property | Chưa thêm relation tới custom model chưa tồn tại |
| 12 | `estate_property_type.py` bản tối thiểu | Tạo model đích trước khi nối Many2one |
| 13 | `estate_property_tag.py` | Tạo model đích trước khi nối Many2many |
| 14 | import + ACL Type/Tag | Đưa model vào Registry và cấp quyền |
| 15 | thêm `property_type_id`/`tag_ids` vào Property | Chỉ nối quan hệ sau khi comodel tồn tại |
| 16 | Type/Tag view/action/menu tối thiểu | Tạo màn hình Configuration, chưa có stat button Offer |
| 17 | cập nhật manifest | Load action trước menu |
| 18 | `estate_property_offer.py` bản tối thiểu | Tạo model Offer trước khi nối One2many |
| 19 | import Offer + thêm ACL | Registry và security biết Offer |
| 20 | thêm `offer_ids` và tab Offers tối thiểu | Nối Property với Offer sau khi cả hai tồn tại |
| 21 | hoàn thiện Offer/Property business logic | Deadline, Best Price, workflow và constraints |
| 22 | `estate_property_offer_views.xml` | Tạo Offer action trước stat button Type |
| 23 | hoàn thiện Type model/view | Thêm Offer count và stat button sau Offer action |
| 24 | `res_users.py` + inherited view | Mở rộng model/view chuẩn sau core nghiệp vụ |
| 25 | hoàn thiện Search/Kanban Property | Hoàn thiện trải nghiệm UI |
| 26 | `tests/__init__.py` và `test_estate.py` | Khóa hành vi Estate bằng tests |
| 27 | `estate_account` manifest/init/model | Bắt đầu link module sau khi Estate ổn định |
| 28 | tests của `estate_account` | Kiểm tra tích hợp Accounting |

## 3.2. Manifest ban đầu và manifest cuối khác nhau

Khi mới bắt đầu, nhiều file XML/CSV chưa tồn tại. Manifest ban đầu phải dùng:

```python
{
    "name": "Real Estate",
    "version": "19.0.1.0.0",
    "depends": ["base"],
    "data": [],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
```

Nếu copy manifest cuối ngay lập tức rồi bấm Install, Odoo sẽ cố đọc:

```text
security/ir.model.access.csv
views/estate_property_offer_views.xml
...
```

trong khi chúng chưa được tạo và báo `File not found`.

Mỗi khi tạo xong một data file, mới thêm nó vào `data`. Luôn bảo đảm thứ tự:

```text
Security
→ Views và Actions
→ Menus tham chiếu Actions
```

Phần 4 hiển thị **manifest cuối cùng** để làm đáp án đối chiếu. Phần 30 hướng dẫn
manifest tối thiểu và cách mở rộng qua từng checkpoint.

---

# 4. Khai báo module Estate

## 4.1. `estate/__manifest__.py`

Code hoàn chỉnh:

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

Giải thích:

| Key | Ý nghĩa |
|---|---|
| `name` | Tên hiển thị trong Apps |
| `version` | Version của custom module |
| `depends` | `base` phải load trước Estate |
| `data` | Danh sách CSV/XML được load từ trên xuống |
| `installable` | Cho phép cài module |
| `application` | Hiển thị như một app |

Tại sao menu nằm cuối? Menu tham chiếu các action bằng XML ID, nên action phải
được load trước menu.

## 4.2. `estate/__init__.py`

```python
from . import models
```

Manifest giúp Odoo nhìn thấy module; `__init__.py` mới bắt đầu chuỗi import code
Python. Nếu thiếu dòng trên, model không được đưa vào Registry.

## 4.3. `estate/models/__init__.py`

```python
from . import estate_property
from . import estate_property_offer
from . import estate_property_tag
from . import estate_property_type
from . import res_users
```

Python không tự chạy mọi file trong folder `models`. File nào không được import ở
đây sẽ không được Odoo đăng ký.

---

# 5. Model Property Type

## 5.1. Tạo `models/estate_property_type.py`

```python
from odoo import api, fields, models


class EstatePropertyType(models.Model):
    """Danh mục loại bất động sản, ví dụ Apartment hoặc House."""

    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    # sequence hỗ trợ drag handle; số nhỏ đứng trước do _order.
    sequence = fields.Integer(default=10)
    # Hai One2many đều đọc qua inverse fields ở model property/offer.
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="property_type_id",
        string="Properties",
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_type_id",
        string="Offers",
    )
    # Giá trị dùng cho stat button; không cần store vì chỉ hiển thị khi đọc form.
    offer_count = fields.Integer(compute="_compute_offer_count")

    # UNIQUE chạy ở PostgreSQL, tránh race condition tốt hơn kiểm tra search rồi create.
    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "A property type name must be unique.",
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        """Đếm offer liên quan cho từng property type.

        Odoo gọi hàm khi tập ``offer_ids`` thay đổi theo ``@api.depends``. Kết
        quả được dùng bởi stat button Offers trên form Property Type.

        Side effects:
            Gán ``offer_count`` cho mọi record trong ``self``.
        """
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)
```

## 5.2. Ý nghĩa

```text
Model: estate.property.type
Table: estate_property_type
```

`sequence` phục vụ kéo thả thứ tự trong list. `_order` nói rằng số sequence nhỏ
đứng trước, nếu bằng nhau thì sắp theo name.

Hai `One2many` không tạo column danh sách ID. Chúng đọc quan hệ ngược:

```text
property_ids ← estate.property.property_type_id
offer_ids    ← estate.property.offer.property_type_id
```

`offer_count` là computed field dùng cho stat button. Constraint UNIQUE chạy ở
PostgreSQL nên ngăn tên trùng kể cả dữ liệu được tạo từ import hoặc RPC.

---

# 6. Model Property Tag

## 6.1. Tạo `models/estate_property_tag.py`

```python
from odoo import fields, models


class EstatePropertyTag(models.Model):
    """Nhãn màu gắn Many2many lên property để phân loại mềm."""

    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    # Widget many2many_tags/color_picker diễn giải integer này thành palette màu.
    color = fields.Integer()

    # Tên tag unique giúp tránh hai tag nhìn giống nhau trong giao diện.
    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "A property tag name must be unique.",
    )
```

## 6.2. Ý nghĩa

```text
Model: estate.property.tag
Table: estate_property_tag
```

`color` lưu một số nguyên; widget `color_picker` và `many2many_tags` diễn giải số
này thành màu. Tag sẽ được nối với Property bằng Many2many.

---

## 6.3. Tạo `models/constants.py` trước khi viết Property và Offer

File này gom các key trạng thái, hướng vườn và tham số nghiệp vụ dùng lại nhiều
lần. Đây là lựa chọn phù hợp hơn `enum.Enum` trong Odoo vì ORM, domain và XML
đều làm việc trực tiếp với chuỗi như `"sold"` hoặc `"accepted"`.

Code hoàn chỉnh:

```python
"""Các hằng số nghiệp vụ dùng chung trong module ``estate``.

Odoo lưu giá trị của ``fields.Selection`` dưới dạng chuỗi trong PostgreSQL.
Ta dùng hằng số chuỗi thay vì ``enum.Enum`` để các giá trị vẫn tương thích trực
tiếp với ORM, domain và XML, đồng thời tránh gõ lặp những chuỗi kỹ thuật dễ sai.

Chỉ đặt tại đây các giá trị kỹ thuật hoặc tham số nghiệp vụ được dùng lại. Nhãn
của Selection đi cùng key để toàn bộ mapping nằm một chỗ; các thông báo lỗi vẫn
để gần hàm sử dụng chúng để người đọc không phải nhảy file chỉ để hiểu một lỗi.
"""

# ---------------------------------------------------------------------------
# Vòng đời của bất động sản
# ---------------------------------------------------------------------------
PROPERTY_STATE_NEW = "new"
PROPERTY_STATE_OFFER_RECEIVED = "offer_received"
PROPERTY_STATE_OFFER_ACCEPTED = "offer_accepted"
PROPERTY_STATE_SOLD = "sold"
PROPERTY_STATE_CANCELED = "canceled"

PROPERTY_STATE_SELECTION = [
    (PROPERTY_STATE_NEW, "New"),
    (PROPERTY_STATE_OFFER_RECEIVED, "Offer Received"),
    (PROPERTY_STATE_OFFER_ACCEPTED, "Offer Accepted"),
    (PROPERTY_STATE_SOLD, "Sold"),
    (PROPERTY_STATE_CANCELED, "Canceled"),
]

# Chỉ property ở một trong hai trạng thái này mới được phép xóa.
PROPERTY_DELETABLE_STATES = frozenset(
    {
        PROPERTY_STATE_NEW,
        PROPERTY_STATE_CANCELED,
    }
)

# Property đã đóng thì không nhận thêm quyết định Accept Offer.
PROPERTY_CLOSED_STATES = frozenset(
    {
        PROPERTY_STATE_SOLD,
        PROPERTY_STATE_CANCELED,
    }
)

# ---------------------------------------------------------------------------
# Hướng của khu vườn
# ---------------------------------------------------------------------------
GARDEN_ORIENTATION_NORTH = "north"
GARDEN_ORIENTATION_SOUTH = "south"
GARDEN_ORIENTATION_EAST = "east"
GARDEN_ORIENTATION_WEST = "west"

GARDEN_ORIENTATION_SELECTION = [
    (GARDEN_ORIENTATION_NORTH, "North"),
    (GARDEN_ORIENTATION_SOUTH, "South"),
    (GARDEN_ORIENTATION_EAST, "East"),
    (GARDEN_ORIENTATION_WEST, "West"),
]

# ---------------------------------------------------------------------------
# Trạng thái của offer
# ---------------------------------------------------------------------------
OFFER_STATUS_ACCEPTED = "accepted"
OFFER_STATUS_REFUSED = "refused"

OFFER_STATUS_SELECTION = [
    (OFFER_STATUS_ACCEPTED, "Accepted"),
    (OFFER_STATUS_REFUSED, "Refused"),
]

# ---------------------------------------------------------------------------
# Tham số nghiệp vụ mặc định
# ---------------------------------------------------------------------------
DEFAULT_AVAILABILITY_MONTHS = 3
DEFAULT_GARDEN_AREA = 10
DEFAULT_OFFER_VALIDITY_DAYS = 7
MINIMUM_SELLING_PRICE_PERCENT = 90
MINIMUM_SELLING_PRICE_RATIO = MINIMUM_SELLING_PRICE_PERCENT / 100
```

Quy tắc maintain:

- Python phải tham chiếu `constants.PROPERTY_STATE_SOLD`, không gõ lại `"sold"`.
- Nhãn Selection được ghép với key một lần trong file này.
- Thông báo lỗi để cạnh hàm phát sinh lỗi để đọc luồng không phải nhảy file.
- XML không thể import Python constant, nên expression trong XML vẫn phải dùng
  chuỗi kỹ thuật; test sẽ giúp phát hiện khi đổi key mà quên cập nhật XML.
- Mỗi hàm default/compute/onchange/action dùng tên rõ nghĩa và docstring; không
  dùng `lambda` cho logic mà người học cần lần theo.

---

# 7. Model Property – model trung tâm

## 7.1. Tạo `models/estate_property.py`

Code hoàn chỉnh:

```python
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import _
from odoo.tools.float_utils import float_compare

from . import constants


class EstateProperty(models.Model):
    """Model trung tâm quản lý tin đăng và vòng đời của bất động sản.

    ``self`` trong Odoo luôn là recordset 0..n record, không mặc định là một
    object đơn. Vì vậy compute, constraint và action phải xử lý nhiều record.
    """

    # Tên kỹ thuật ORM/RPC; mặc định ánh xạ sang table ``estate_property``.
    _name = "estate.property"
    # Nhãn dễ đọc dùng trong metadata/log và màn hình kỹ thuật.
    _description = "Real Estate Property"
    # Search không truyền order sẽ đưa property mới nhất lên trước.
    _order = "id desc"

    def _default_date_availability(self):
        """Trả về ngày có thể giao nhà mặc định cho một property mới.

        Odoo gọi hàm này trong quá trình ``default_get/create`` khi client không
        truyền ``date_availability``. Việc dùng callable có tên giúp ngày được
        tính tại đúng thời điểm tạo record và dễ đọc hơn một ``lambda`` ẩn ngay
        trong khai báo field.

        Returns:
            date: Ngày hiện tại cộng số tháng mặc định trong ``constants``.
        """
        return fields.Date.today() + relativedelta(
            months=constants.DEFAULT_AVAILABILITY_MONTHS
        )

    def _default_salesperson(self):
        """Trả về user đang đăng nhập để làm salesperson mặc định.

        Odoo gọi hàm này khi khởi tạo form/record nếu ``user_id`` chưa được
        truyền. ``self.env.user`` là record ``res.users`` của request hiện tại.

        Returns:
            res.users: User hiện tại trong Odoo Environment.
        """
        return self.env.user

    # ------------------------------------------------------------------
    # Thông tin cơ bản
    # ------------------------------------------------------------------
    # required=True được ORM kiểm tra và tương ứng NOT NULL trong PostgreSQL.
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    # copy=False: Duplicate không mang ngày cũ. Callable có tên được gọi tại
    # thời điểm create, tránh ngày bị cố định từ lúc server import module.
    date_availability = fields.Date(
        copy=False,
        default=_default_date_availability,
    )
    expected_price = fields.Float(required=True)
    # User không nhập trực tiếp; Accept Offer sẽ ghi selling_price bằng ORM.
    # readonly là UX, còn invariant thật nằm trong action/constraint server.
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    # PostgreSQL lưu key (north...), còn label (North...) dành cho giao diện.
    garden_orientation = fields.Selection(
        selection=constants.GARDEN_ORIENTATION_SELECTION,
    )
    # Reserved field: active=False làm record bị loại khỏi search mặc định
    # (archive) nhưng dữ liệu vẫn tồn tại trong database.
    active = fields.Boolean(default=True)
    # State điều khiển workflow, statusbar và visibility của buttons.
    state = fields.Selection(
        selection=constants.PROPERTY_STATE_SELECTION,
        required=True,
        copy=False,
        default=constants.PROPERTY_STATE_NEW,
    )

    # ------------------------------------------------------------------
    # Quan hệ giữa các model
    # ------------------------------------------------------------------
    # Many2one lưu foreign key trên table estate_property.
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
    )
    # Many2many được ORM lưu trong relation table trung gian.
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag",
        string="Tags",
    )
    # One2many là quan hệ ảo đọc qua inverse offer.property_id; nó không tạo
    # một column danh sách ID trên table estate_property.
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Offers",
    )
    # Environment cung cấp user đang đăng nhập làm salesperson mặc định.
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        default=_default_salesperson,
    )
    # Buyer chỉ có sau khi accept offer và không được copy sang tin mới.
    buyer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        copy=False,
    )

    # Computed fields không store: ORM tính khi đọc và cache trong Environment.
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    # ------------------------------------------------------------------
    # SQL constraints của Odoo 19
    # ------------------------------------------------------------------
    # Chạy tại PostgreSQL nên bảo vệ mọi đường ghi: UI, RPC, import và code.
    _expected_price_positive = models.Constraint(
        "CHECK(expected_price > 0)",
        "The expected price must be strictly positive.",
    )
    _selling_price_positive = models.Constraint(
        "CHECK(selling_price >= 0)",
        "The selling price must be positive.",
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        """Tính living area + garden area cho từng record.

        Odoo gọi lại hàm khi ``living_area`` hoặc ``garden_area`` thay đổi vì
        chúng được khai báo trong ``@api.depends``. Compute method không nhận
        tham số ngoài ``self`` và bắt buộc gán ``total_area`` cho mọi record.

        Side effects:
            Gán field computed ``total_area`` trong cache ORM; field này không
            có ``store=True`` nên không tạo cột lưu kết quả trong PostgreSQL.
        """
        for property_record in self:
            property_record.total_area = (
                property_record.living_area + property_record.garden_area
            )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        """Lấy giá offer lớn nhất hoặc 0 nếu chưa có offer.

        Odoo gọi hàm khi giá của offer liên quan thay đổi. ``mapped("price")``
        biến recordset offer thành danh sách giá; ``default=0.0`` ngăn ``max``
        báo lỗi khi property chưa có offer.

        Side effects:
            Gán field computed ``best_price`` cho từng property trong ``self``.
        """
        for property_record in self:
            property_record.best_price = max(
                property_record.offer_ids.mapped("price"), default=0.0
            )

    @api.onchange("garden")
    def _onchange_garden(self):
        """Gợi ý giá trị garden trên form, không phải business invariant.

        Onchange chạy với pseudo-record khi user sửa form. Nếu bật Garden, form
        được gợi ý diện tích và hướng mặc định; nếu tắt, hai giá trị được xóa.
        Import/RPC có thể không chạy onchange, vì vậy đây chỉ là hỗ trợ nhập liệu
        chứ không phải validation bảo vệ dữ liệu.

        Side effects:
            Chỉ thay đổi giá trị tạm trên form cho đến khi user bấm Save.
        """
        if self.garden:
            self.garden_area = constants.DEFAULT_GARDEN_AREA
            self.garden_orientation = constants.GARDEN_ORIENTATION_NORTH
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        """Chặn giá bán dưới 90% giá kỳ vọng bằng so sánh float an toàn.

        Odoo gọi constraint sau ``create/write`` khi một trong hai field khai báo
        thay đổi. Giá 0 nghĩa là chưa accept offer nên được bỏ qua. So sánh qua
        ``float_compare`` để tránh sai số số thực.

        Raises:
            ValidationError: Nếu giá bán khác 0 nhưng thấp hơn tỷ lệ tối thiểu.
        """
        for property_record in self:
            if not property_record.selling_price:
                continue
            minimum_price = (
                property_record.expected_price
                * constants.MINIMUM_SELLING_PRICE_RATIO
            )
            if float_compare(
                property_record.selling_price,
                minimum_price,
                precision_digits=2,
            ) < 0:
                raise ValidationError(
                    _(
                        "The selling price cannot be lower than "
                        "%(minimum_percentage)s%% of the expected price.",
                        minimum_percentage=(
                            constants.MINIMUM_SELLING_PRICE_PERCENT
                        ),
                    )
                )

    def action_sold(self):
        """Đánh dấu Sold sau khi kiểm tra transition và buyer.

        Button Sold gọi method qua RPC, nhưng module khác cũng có thể gọi trực
        tiếp. Vì vậy mọi kiểm tra phải nằm ở server. Hàm xử lý được nhiều record
        và chỉ bán property đã có buyer từ một offer được chấp nhận.

        Raises:
            UserError: Nếu property đã hủy, đã bán hoặc chưa có buyer.

        Returns:
            bool: ``True`` sau khi toàn bộ record chuyển trạng thái thành công.
        """
        for property_record in self:
            if property_record.state == constants.PROPERTY_STATE_CANCELED:
                raise UserError(_("A canceled property cannot be sold."))
            if property_record.state == constants.PROPERTY_STATE_SOLD:
                raise UserError(_("This property is already sold."))
            if not property_record.buyer_id:
                raise UserError(
                    _("Accept an offer before marking the property as sold.")
                )
            property_record.state = constants.PROPERTY_STATE_SOLD
        return True

    def action_cancel(self):
        """Chuyển các property được chọn sang trạng thái Canceled.

        Hàm được button Cancel gọi bằng RPC. Nó xử lý toàn bộ record trong
        ``self``, từ chối property đã bán và trả ``True`` khi hoàn tất.

        Raises:
            UserError: Nếu một property trong recordset đã ở trạng thái Sold.

        Returns:
            bool: ``True`` để báo action server đã thực thi thành công.
        """
        for property_record in self:
            if property_record.state == constants.PROPERTY_STATE_SOLD:
                raise UserError(_("A sold property cannot be canceled."))
            property_record.state = constants.PROPERTY_STATE_CANCELED
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        """Chỉ cho xóa New/Canceled trong hoạt động bình thường.

        Odoo gọi hook ngay trước ``unlink``. ``at_uninstall=False`` cho phép bỏ
        qua rule khi uninstall module để dữ liệu nghiệp vụ không cản việc gỡ.

        Raises:
            UserError: Nếu có property không ở trạng thái New hoặc Canceled.
        """
        for property_record in self:
            if property_record.state not in constants.PROPERTY_DELETABLE_STATES:
                raise UserError(
                    _("Only new or canceled properties can be deleted.")
                )
```

## 7.2. Model, table và recordset

```text
_name = estate.property
table = estate_property
```

`self` luôn là recordset 0..n record, nên action, compute và constraint đều lặp:

```python
for property_record in self:
    ...
```

## 7.3. Field thường và default

```python
bedrooms = fields.Integer(default=2)
```

Nếu client không gửi `bedrooms`, ORM dùng `2`. Với ngày:

```python
def _default_date_availability(self):
    return fields.Date.today() + relativedelta(
        months=constants.DEFAULT_AVAILABILITY_MONTHS
    )

date_availability = fields.Date(
    copy=False,
    default=_default_date_availability,
)
```

Odoo truyền recordset vào callable khi lấy default. Hàm có tên giúp bạn đặt
breakpoint, viết docstring và đọc được mục đích ngay lập tức; ngày vẫn được tính
đúng lúc tạo record thay vì bị cố định khi server import module.

`copy=False` nghĩa là Duplicate record sẽ không mang giá trị cũ sang.

## 7.4. Quan hệ

```text
Many2one property_type_id → column estate_property.property_type_id
Many2many tag_ids         → relation table trung gian
One2many offer_ids        → đọc estate_property_offer.property_id
Many2one user_id          → res_users.id
Many2one buyer_id         → res_partner.id
```

`res.partner` là model chuẩn từ module `base`, table `res_partner`.

## 7.5. Compute

Dependency graph:

```text
living_area ─┐
             ├── total_area
garden_area ─┘

offer_ids.price ── best_price
```

`@api.depends` giúp ORM biết khi nào phải invalidate cache và tính lại.

## 7.6. Onchange không phải save

`_onchange_garden()` chạy trên pseudo-record khi người dùng sửa form:

```text
Garden=True  → area=10, orientation=north
Garden=False → area=0, orientation=False
```

Nó chỉ cập nhật form tạm. Database chỉ thay đổi khi `web_save()` gọi `create()`
hoặc `write()`.

## 7.7. Hai tầng constraint

SQL constraint bảo vệ dữ liệu tại PostgreSQL:

```text
expected_price > 0
selling_price >= 0
```

Python constraint bảo vệ business rule cần đọc nhiều field:

```text
selling_price >= expected_price × 90%
```

Giá bán `0` nghĩa là chưa Accept Offer nên được bỏ qua.

## 7.8. Button actions

`action_sold()` và `action_cancel()` không tự xuất hiện thành nút. View XML phải
khai báo button `type="object"` cùng tên. Method vẫn tự kiểm tra nghiệp vụ vì RPC
hoặc module khác có thể gọi nó mà không qua giao diện.

---

# 8. Model Offer

## 8.1. Tạo `models/estate_property_offer.py`

```python
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import _
from odoo.tools.float_utils import float_compare

from . import constants


class EstatePropertyOffer(models.Model):
    """Một đề nghị mua dành cho một property và một partner cụ thể."""

    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    # Giá cao nhất đứng đầu trong list/recordset mặc định.
    _order = "price desc"

    # Giá là required ở ORM và còn được bảo vệ > 0 bởi SQL constraint phía dưới.
    price = fields.Float(required=True)
    # False nghĩa là offer chưa xử lý; accepted/refused là trạng thái cuối.
    status = fields.Selection(
        selection=constants.OFFER_STATUS_SELECTION,
        copy=False,
    )
    # Người đưa ra offer. res.partner dùng chung cho cá nhân/doanh nghiệp.
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
    )
    # Foreign key tới property. cascade bảo đảm offer con bị xóa cùng property,
    # tránh record mồ côi không còn tin đăng cha.
    property_id = fields.Many2one(
        comodel_name="estate.property",
        string="Property",
        required=True,
        ondelete="cascade",
    )
    # Số ngày offer còn hiệu lực; user có thể sửa validity hoặc deadline.
    validity = fields.Integer(default=constants.DEFAULT_OFFER_VALIDITY_DAYS)
    # inverse làm computed field có thể nhập ngược: đổi deadline sẽ tính validity.
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )
    # Related field đi theo property.type. store=True tạo column thực để action
    # stat button có thể search/domain/group hiệu quả theo property type.
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        store=True,
    )

    # Database luôn từ chối offer 0 hoặc âm, bất kể nguồn ghi dữ liệu.
    _price_positive = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be strictly positive.",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        """Tính deadline từ ngày tạo và số ngày validity.

        Odoo gọi hàm khi ``create_date`` hoặc ``validity`` thay đổi. Khi form
        đang tạo record, ``create_date`` chưa tồn tại vì chưa INSERT; ngày hiện
        tại theo context/timezone của user là fallback an toàn.

        Side effects:
            Gán ``date_deadline`` cho từng offer trong ``self``.
        """
        for offer in self:
            creation_date = fields.Date.to_date(offer.create_date)
            if not creation_date:
                creation_date = fields.Date.context_today(offer)
            offer.date_deadline = creation_date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        """Tính ngược validity khi user trực tiếp thay đổi deadline.

        Odoo gọi inverse lúc lưu một ``date_deadline`` do user nhập. Số ngày
        được tính từ ngày tạo; offer mới chưa có ``create_date`` nên dùng ngày
        hiện tại theo context làm mốc.

        Side effects:
            Gán lại ``validity`` cho từng offer có deadline.
        """
        for offer in self:
            if not offer.date_deadline:
                continue
            creation_date = fields.Date.to_date(offer.create_date)
            if not creation_date:
                creation_date = fields.Date.context_today(offer)
            offer.validity = (offer.date_deadline - creation_date).days

    @api.model_create_multi
    def create(self, vals_list):
        """Tạo một batch offer và cập nhật state của property.

        Odoo gọi override này cho cả form, import và RPC. ``vals_list`` là danh
        sách dict vì decorator hỗ trợ tạo nhiều offer trong một lệnh. Validation
        chạy trước ``super`` để không INSERT offer thấp hơn giá tốt nhất; sau
        ``super`` mới có recordset thật để đổi trạng thái property.

        Args:
            vals_list (list[dict]): Các giá trị thô dùng để tạo offer.

        Raises:
            UserError: Nếu giá mới thấp hơn best price hiện có hoặc trước đó
                trong cùng batch.

        Returns:
            estate.property.offer: Recordset các offer vừa được ORM tạo.
        """

        # Cache giá cao nhất theo property trong chính batch. Nếu batch chứa hai
        # offer cho cùng property, offer sau còn phải so với offer trước dù offer
        # trước chưa được INSERT vào database.
        batch_best_prices = {}
        for values in vals_list:
            # Many2one trong vals là integer ID, vì vậy dùng browse để lấy recordset.
            property_record = self.env["estate.property"].browse(
                values.get("property_id")
            )
            # Giữ create linh hoạt nếu ORM gọi với vals chưa có property; required
            # field/SQL sẽ đưa lỗi chuẩn ở bước super().create().
            if not property_record:
                continue
            current_best = batch_best_prices.get(
                property_record.id, property_record.best_price
            )
            offer_price = values.get("price", 0.0)
            if current_best and float_compare(
                offer_price, current_best, precision_digits=2
            ) < 0:
                raise UserError(
                    _("An offer cannot be lower than the existing best offer.")
                )
            batch_best_prices[property_record.id] = max(current_best, offer_price)

        # super thực hiện security checks, conversion, INSERT và constraints.
        offers = super().create(vals_list)
        # Dùng vòng lặp tường minh thay cho lambda để người mới có thể lần theo
        # từng property. Chỉ chuyển New -> Offer Received, không ghi đè state sau.
        for property_record in offers.property_id:
            if property_record.state == constants.PROPERTY_STATE_NEW:
                property_record.state = constants.PROPERTY_STATE_OFFER_RECEIVED
        return offers

    def _has_another_accepted_offer(self):
        """Kiểm tra property đã có một offer khác được chấp nhận hay chưa.

        Đây là helper nội bộ được ``action_accept`` gọi cho từng offer. Vòng lặp
        có tên biến rõ ràng được dùng thay cho ``filtered(lambda ...)`` để dễ
        debug và giúp quy tắc “mỗi property chỉ có một offer accepted” lộ rõ.

        Returns:
            bool: ``True`` nếu tồn tại sibling offer có trạng thái Accepted.
        """
        self.ensure_one()
        for candidate_offer in self.property_id.offer_ids:
            is_current_offer = candidate_offer == self
            is_accepted = (
                candidate_offer.status == constants.OFFER_STATUS_ACCEPTED
            )
            if not is_current_offer and is_accepted:
                return True
        return False

    def action_accept(self):
        """Chấp nhận offer và đồng bộ dữ liệu sang property.

        Button dấu tick gọi method này. Mỗi offer phải chưa được xử lý, property
        phải còn mở và không được có offer khác Accepted. Nếu hợp lệ, hàm ghi
        buyer, selling price và state lên property trong cùng transaction.

        Raises:
            UserError: Nếu offer đã xử lý, property đã đóng hoặc đã có offer
                khác được chấp nhận.

        Returns:
            bool: ``True`` khi tất cả offer trong ``self`` được chấp nhận.
        """
        for offer in self:
            if offer.status:
                raise UserError(_("A processed offer cannot be accepted again."))
            property_record = offer.property_id
            property_is_closed = (
                property_record.state in constants.PROPERTY_CLOSED_STATES
            )
            if offer._has_another_accepted_offer() or property_is_closed:
                raise UserError(
                    _("Only one offer can be accepted for an available property.")
                )
            offer.status = constants.OFFER_STATUS_ACCEPTED
            # write một dict giúp ba field thay đổi trong cùng transaction.
            property_record.write(
                {
                    "buyer_id": offer.partner_id.id,
                    "selling_price": offer.price,
                    "state": constants.PROPERTY_STATE_OFFER_ACCEPTED,
                }
            )
        return True

    def action_refuse(self):
        """Từ chối toàn bộ offer chưa xử lý trong ``self``.

        Button dấu X gọi method này. Kiểm tra cả recordset trước rồi mới ``write``
        một lần để tránh trạng thái nửa thành công khi chọn nhiều record.

        Raises:
            UserError: Nếu ít nhất một offer đã Accepted hoặc Refused.

        Returns:
            bool: ``True`` sau khi cập nhật trạng thái thành công.
        """
        if self.filtered("status"):
            raise UserError(_("A processed offer cannot be refused again."))
        self.write({"status": constants.OFFER_STATUS_REFUSED})
        return True
```

## 8.2. Deadline có inverse

```text
validity thay đổi → compute date_deadline
date_deadline thay đổi → inverse tính lại validity
```

Fallback `fields.Date.context_today(offer)` cần thiết vì record mới chưa có
`create_date` trước khi INSERT.

## 8.3. Override `create()`

Decorator `@api.model_create_multi` nghĩa là input luôn được chuẩn hóa thành:

```python
[
    {"price": 95_000, "property_id": 1, "partner_id": 3},
    {"price": 100_000, "property_id": 2, "partner_id": 4},
]
```

Thứ tự xử lý:

```text
Kiểm tra Offer mới không thấp hơn Best Price
→ super().create(vals_list)
→ ORM kiểm tra ACL/field/constraint và INSERT
→ Property New chuyển thành Offer Received
→ return recordset Offer
```

Không được quên `return offers` vì caller cần recordset đã tạo.

## 8.4. Accept Offer

```text
Offer.partner_id → Property.buyer_id
Offer.price      → Property.selling_price
                  Property.state = offer_accepted
```

Khi ghi `selling_price`, constraint 90% trên Property tự chạy. Nếu thất bại, toàn
bộ thao tác Accept rollback, kể cả `offer.status = accepted`.

## 8.5. Refuse Offer

Offer đã có `status` là trạng thái cuối nên không cho xử lý lại. `write()` trên
recordset giúp Refuse nhiều Offer trong cùng một lệnh.

---

# 9. Mở rộng model Users

## 9.1. Tạo `models/res_users.py`

```python
from odoo import fields, models

from . import constants


class ResUsers(models.Model):
    """Mở rộng user chuẩn bằng danh sách property phụ trách.

    Chỉ có _inherit và không có _name, nên class này mở rộng cùng model/table
    ``res.users`` thay vì tạo một model mới.
    """

    _inherit = "res.users"

    # Inverse của estate.property.user_id. Domain chỉ ảnh hưởng những property
    # được chọn/hiển thị qua field này, không phải một record rule bảo mật.
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="user_id",
        string="Real Estate Properties",
        domain=[
            (
                "state",
                "in",
                [
                    constants.PROPERTY_STATE_NEW,
                    constants.PROPERTY_STATE_OFFER_RECEIVED,
                ],
            )
        ],
    )
```

Chỉ có `_inherit`, không có `_name`, nên không tạo model/table mới. Ta thêm field
vào model `res.users` chuẩn.

`property_ids` là inverse của:

```python
estate.property.user_id
```

Domain ở field chỉ lọc nội dung hiển thị; nó không phải record rule bảo mật.

---

# 10. Kiểm tra Registry trước khi viết giao diện

Đến đây có thể tạm thời để `data` trong manifest chỉ chứa ACL sau khi tạo ACL ở
phần kế tiếp, rồi install/upgrade. Một kiểm tra nhanh bằng Odoo Shell:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin shell -c .\odoo.conf -d DATABASE_NAME
```

Trong Shell:

```python
env["estate.property"]
env["estate.property.offer"]
env["estate.property.type"]
env["estate.property.tag"]
```

Nếu nhận được recordset rỗng thay vì `KeyError`, model đã vào Registry.

---

# 11. Phân quyền truy cập model

## 11.1. Tạo `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_estate_property_manager,access_estate_property_manager,model_estate_property,base.group_system,1,1,1,1
access_estate_property_staff,access_estate_property_staff,model_estate_property,base.group_user,1,1,1,1
access_estate_property_type_staff,access_estate_property_type_staff,model_estate_property_type,base.group_user,1,1,1,1
access_estate_property_tag_staff,access_estate_property_tag_staff,model_estate_property_tag,base.group_user,1,1,1,1
access_estate_property_offer_staff,access_estate_property_offer_staff,model_estate_property_offer,base.group_user,1,1,1,1
```

## 11.2. Cấu trúc một dòng ACL

```text
model_id:id          model_estate_property
group_id:id          base.group_user
perm_read            1
perm_write           1
perm_create          1
perm_unlink          1
```

Khi khai báo `_name = "estate.property"`, Odoo tạo external ID model:

```text
model_estate_property
```

ACL trả lời “nhóm này có được gọi operation trên model không?”. ACL chưa giới hạn
record cụ thể. Muốn Agent chỉ xem Property của mình, phải thêm Record Rule.

> Phiên bản học tập này cấp quyền rộng cho mọi Internal User. Production nên tạo
> group Estate Agent/Manager và record rules riêng.

## 11.3. Thứ tự kiểm tra khi ghi

```text
ACL
→ Record Rule
→ field access
→ ORM conversion/default
→ SQL constraints
→ Python constraints
→ commit hoặc rollback
```

---

# 12. View cho Offer

## 12.1. Tạo `views/estate_property_offer_views.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="estate_property_offer_view_list" model="ir.ui.view">
        <field name="name">estate.property.offer.list</field>
        <field name="model">estate.property.offer</field>
        <field name="arch" type="xml">
            <list string="Offers"
                  editable="bottom"
                  decoration-danger="status == 'refused'"
                  decoration-success="status == 'accepted'">
                <field name="price"/>
                <field name="partner_id"/>
                <field name="property_id"/>
                <field name="property_type_id"/>
                <field name="validity"/>
                <field name="date_deadline"/>
                <field name="status" column_invisible="True"/>
            </list>
        </field>
    </record>

    <record id="estate_property_offer_view_form" model="ir.ui.view">
        <field name="name">estate.property.offer.form</field>
        <field name="model">estate.property.offer</field>
        <field name="arch" type="xml">
            <form string="Offer">
                <header>
                    <button name="action_accept"
                            type="object"
                            string="Accept"
                            class="btn-primary"
                            invisible="status != False"/>
                    <button name="action_refuse"
                            type="object"
                            string="Refuse"
                            invisible="status != False"/>
                </header>
                <sheet>
                    <group>
                        <field name="price"/>
                        <field name="partner_id"/>
                        <field name="property_id"/>
                        <field name="property_type_id" readonly="True"/>
                        <field name="validity"/>
                        <field name="date_deadline"/>
                        <field name="status"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="estate_property_offer_action" model="ir.actions.act_window">
        <field name="name">Offers</field>
        <field name="res_model">estate.property.offer</field>
        <field name="view_mode">list,form</field>
        <field name="domain">
            [('property_type_id', '=', active_id)]
        </field>
    </record>
</odoo>
```

## 12.2. Điều cần hiểu

```xml
<record ... model="ir.ui.view">
```

nghĩa là tạo một record cấu hình View. Còn:

```xml
<field name="model">estate.property.offer</field>
```

nghĩa là view hiển thị record của model Offer.

`editable="bottom"` cho phép thêm dòng ngay cuối list. `type="object"` trên button
gọi method Python cùng tên:

```text
name="action_accept" → offer.action_accept()
name="action_refuse" → offer.action_refuse()
```

Action Offer không có menu riêng; stat button của Property Type gọi action này và
`active_id` là ID của Type đang mở.

---

# 13. View cho Property Type

## 13.1. Tạo `views/estate_property_type_views.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="estate_property_type_view_list" model="ir.ui.view">
        <field name="name">estate.property.type.list</field>
        <field name="model">estate.property.type</field>
        <field name="arch" type="xml">
            <list string="Property Types">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="estate_property_type_view_form" model="ir.ui.view">
        <field name="name">estate.property.type.form</field>
        <field name="model">estate.property.type</field>
        <field name="arch" type="xml">
            <form string="Property Type">
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="%(estate_property_offer_action)d"
                                type="action"
                                class="oe_stat_button"
                                icon="fa-money">
                            <field name="offer_count"
                                   widget="statinfo"
                                   string="Offers"/>
                        </button>
                    </div>

                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name"/>
                        </h1>
                    </div>

                    <field name="property_ids">
                        <list>
                            <field name="name"/>
                            <field name="expected_price"/>
                            <field name="state"/>
                        </list>
                    </field>
                </sheet>
            </form>
        </field>
    </record>

    <record id="estate_property_type_action" model="ir.actions.act_window">
        <field name="name">Property Types</field>
        <field name="res_model">estate.property.type</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

## 13.2. `type="action"` khác `type="object"`

```text
type="object" → name là tên method Python
type="action" → name resolve tới Window Action
```

Cú pháp:

```xml
name="%(estate_property_offer_action)d"
```

được XML loader thay bằng database ID của action Offer. Stat button hiển thị
`offer_count`, rồi action dùng `active_id` để lọc Offer theo Type.

---

# 14. View cho Property Tag

## 14.1. Tạo `views/estate_property_tag_views.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="estate_property_tag_view_list" model="ir.ui.view">
        <field name="name">estate.property.tag.list</field>
        <field name="model">estate.property.tag</field>
        <field name="arch" type="xml">
            <list string="Property Tags" editable="bottom">
                <field name="name"/>
                <field name="color" widget="color_picker"/>
            </list>
        </field>
    </record>

    <record id="estate_property_tag_view_form" model="ir.ui.view">
        <field name="name">estate.property.tag.form</field>
        <field name="model">estate.property.tag</field>
        <field name="arch" type="xml">
            <form string="Property Tag">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="color" widget="color_picker"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="estate_property_tag_action" model="ir.actions.act_window">
        <field name="name">Property Tags</field>
        <field name="res_model">estate.property.tag</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

Widget chỉ thay cách hiển thị; database vẫn lưu `color` dưới dạng integer.

---

# 15. View hoàn chỉnh cho Property

## 15.1. Tạo `views/estate_property_views.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- LIST VIEW -->
    <record id="estate_property_view_list" model="ir.ui.view">
        <field name="name">estate.property.list</field>
        <field name="model">estate.property</field>
        <field name="arch" type="xml">
            <list string="Properties"
                  decoration-success="state in ('offer_received', 'offer_accepted')"
                  decoration-bf="state == 'offer_accepted'"
                  decoration-muted="state == 'sold'">
                <field name="state" column_invisible="True"/>
                <field name="name"/>
                <field name="postcode"/>
                <field name="property_type_id"/>
                <field name="bedrooms"/>
                <field name="living_area"/>
                <field name="expected_price"/>
                <field name="selling_price"/>
                <field name="date_availability" optional="hide"/>
                <field name="tag_ids"
                       widget="many2many_tags"
                       options="{'color_field': 'color'}"/>
            </list>
        </field>
    </record>

    <!-- FORM VIEW -->
    <record id="estate_property_view_form" model="ir.ui.view">
        <field name="name">estate.property.form</field>
        <field name="model">estate.property</field>
        <field name="arch" type="xml">
            <form string="Property">
                <header>
                    <button name="action_sold"
                            type="object"
                            string="Sold"
                            class="btn-primary"
                            invisible="state in ('sold', 'canceled')"/>
                    <button name="action_cancel"
                            type="object"
                            string="Cancel"
                            invisible="state in ('sold', 'canceled')"/>
                    <field name="state"
                           widget="statusbar"
                           statusbar_visible="new,offer_received,offer_accepted,sold"/>
                </header>

                <sheet>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name" placeholder="Property title"/>
                        </h1>
                    </div>

                    <group>
                        <group>
                            <field name="property_type_id"
                                   options="{'no_create': True, 'no_open': True}"/>
                            <field name="postcode"/>
                            <field name="date_availability"/>
                        </group>
                        <group>
                            <field name="expected_price"/>
                            <field name="best_price"/>
                            <field name="selling_price"/>
                        </group>
                    </group>

                    <notebook>
                        <page string="Description" name="description">
                            <group>
                                <field name="description"/>
                            </group>
                            <group>
                                <group>
                                    <field name="bedrooms"/>
                                    <field name="living_area"/>
                                    <field name="facades"/>
                                    <field name="garage"/>
                                </group>
                                <group>
                                    <field name="garden"/>
                                    <field name="garden_area"
                                           invisible="not garden"/>
                                    <field name="garden_orientation"
                                           invisible="not garden"/>
                                    <field name="total_area"/>
                                </group>
                            </group>
                        </page>

                        <page string="Offers" name="offers">
                            <field name="offer_ids"
                                   readonly="state in ('offer_accepted', 'sold', 'canceled')">
                                <list editable="bottom"
                                      decoration-danger="status == 'refused'"
                                      decoration-success="status == 'accepted'">
                                    <field name="price"/>
                                    <field name="partner_id"/>
                                    <field name="validity"/>
                                    <field name="date_deadline"/>
                                    <field name="status"
                                           column_invisible="True"/>
                                    <button name="action_accept"
                                            type="object"
                                            icon="fa-check"
                                            title="Accept"
                                            invisible="status != False"/>
                                    <button name="action_refuse"
                                            type="object"
                                            icon="fa-times"
                                            title="Refuse"
                                            invisible="status != False"/>
                                </list>
                            </field>
                        </page>

                        <page string="Other Info" name="other_info">
                            <group>
                                <field name="user_id"/>
                                <field name="buyer_id"/>
                                <field name="tag_ids"
                                       widget="many2many_tags"
                                       options="{'color_field': 'color'}"/>
                                <field name="active" invisible="True"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- SEARCH VIEW -->
    <record id="estate_property_view_search" model="ir.ui.view">
        <field name="name">estate.property.search</field>
        <field name="model">estate.property</field>
        <field name="arch" type="xml">
            <search string="Search Properties">
                <field name="name"/>
                <field name="postcode"/>
                <field name="property_type_id"/>
                <field name="expected_price"/>
                <field name="bedrooms"/>
                <field name="living_area"
                       filter_domain="[('living_area', '&gt;=', self)]"/>

                <separator/>

                <filter name="available"
                        string="Available"
                        domain="[('state', 'in', ('new', 'offer_received'))]"/>
                <filter name="with_garden"
                        string="Has Garden"
                        domain="[('garden', '=', True)]"/>

                <separator/>

                <filter name="group_postcode"
                        string="Postcode"
                        context="{'group_by': 'postcode'}"/>
                <filter name="group_property_type"
                        string="Property Type"
                        context="{'group_by': 'property_type_id'}"/>
            </search>
        </field>
    </record>

    <!-- KANBAN VIEW -->
    <record id="estate_property_view_kanban" model="ir.ui.view">
        <field name="name">estate.property.kanban</field>
        <field name="model">estate.property</field>
        <field name="arch" type="xml">
            <kanban default_group_by="property_type_id"
                    records_draggable="false">
                <field name="state"/>
                <field name="property_type_id"/>
                <field name="expected_price"/>
                <field name="best_price"/>
                <field name="selling_price"/>
                <field name="tag_ids"/>

                <templates>
                    <t t-name="card">
                        <div class="d-flex flex-column gap-1">
                            <strong class="fs-5">
                                <field name="name"/>
                            </strong>
                            <span>
                                Expected: <field name="expected_price"/>
                            </span>
                            <span t-if="record.state.raw_value in ['offer_received', 'offer_accepted', 'sold']">
                                Best offer: <field name="best_price"/>
                            </span>
                            <span t-if="record.state.raw_value in ['offer_accepted', 'sold']">
                                Selling price: <field name="selling_price"/>
                            </span>
                            <field name="tag_ids"
                                   widget="many2many_tags"
                                   options="{'color_field': 'color'}"/>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- WINDOW ACTION -->
    <record id="estate_property_action" model="ir.actions.act_window">
        <field name="name">Properties</field>
        <field name="res_model">estate.property</field>
        <field name="view_mode">list,kanban,form</field>
        <field name="context">
            {'search_default_available': True}
        </field>
    </record>
</odoo>
```

## 15.2. List View

List hiển thị nhiều record. `state` bị ẩn nhưng vẫn phải có trong view để các
expression `decoration-*` đọc được. `optional="hide"` cho phép người dùng bật cột
Date Availability khi cần.

## 15.3. Form View

Header chứa workflow buttons và statusbar. Khi bấm:

```xml
<button name="action_sold" type="object"/>
```

web client gửi RPC tương đương:

```python
env["estate.property"].browse(active_id).action_sold()
```

Tab Offers là One2many inline. `property_id` không cần hiện vì ORM tự nối Offer
mới với Property hiện tại qua `inverse_name="property_id"`.

## 15.4. Search View

Search View định nghĩa search fields, filters và group-by. Domain:

```python
[("state", "in", ("new", "offer_received"))]
```

được ORM chuyển thành SQL `WHERE` có tham số.

## 15.5. Kanban View

Những field dùng trong template/condition phải được khai báo trong `<kanban>` để
web client yêu cầu chúng khi đọc. Dùng `raw_value` để so sánh technical state,
không dùng label đã dịch.

## 15.6. Window Action

```text
res_model = estate.property
view_mode = list,kanban,form
```

`list` đứng đầu nên menu mở List mặc định. Bấm một record hoặc New thì mở Form;
người dùng có thể chuyển sang Kanban.

Context:

```python
{"search_default_available": True}
```

tự bật filter có `name="available"`.

---

# 16. Kế thừa Form Users

## 16.1. Tạo `views/res_users_views.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="res_users_view_form_inherit_estate" model="ir.ui.view">
        <field name="name">res.users.form.inherit.estate</field>
        <field name="model">res.users</field>
        <field name="inherit_id" ref="base.view_users_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook" position="inside">
                <page string="Real Estate Properties"
                      name="estate_properties">
                    <field name="property_ids"/>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

Không sao chép toàn bộ view gốc. `inherit_id` chọn view cha và XPath chèn một tab
mới vào notebook. Model Python đã thêm `property_ids`, còn XML quyết định nơi hiển
thị field đó.

---

# 17. Menu ứng dụng

## 17.1. Tạo `views/estate_menus.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <menuitem id="estate_menu_root"
              name="Real Estate"
              sequence="10"/>

    <menuitem id="estate_menu_properties"
              name="Advertisements"
              parent="estate_menu_root"
              sequence="10"/>

    <menuitem id="estate_menu_property_list"
              name="Properties"
              parent="estate_menu_properties"
              action="estate_property_action"
              sequence="10"/>

    <menuitem id="estate_menu_configuration"
              name="Configuration"
              parent="estate_menu_root"
              sequence="20"/>

    <menuitem id="estate_menu_property_types"
              name="Property Types"
              parent="estate_menu_configuration"
              action="estate_property_type_action"
              sequence="10"/>

    <menuitem id="estate_menu_property_tags"
              name="Property Tags"
              parent="estate_menu_configuration"
              action="estate_property_tag_action"
              sequence="20"/>
</odoo>
```

## 17.2. Menu không “mở file XML”

Sau install/upgrade, XML đã trở thành record database:

```text
ir.ui.menu
→ action_id trỏ ir.actions.act_window
→ action.res_model chỉ estate.property
→ web client tìm ir.ui.view phù hợp
```

Luồng menu Properties:

```text
estate_menu_property_list
→ action="estate_property_action"
→ res_model="estate.property"
→ view_mode="list,kanban,form"
→ mở List View
```

Nếu sửa tên menu, phải upgrade module; restart hoặc refresh đơn thuần không import
lại XML vào database.

---

# 18. Kiểm tra manifest lần cuối

Đảm bảo danh sách `data` đúng thứ tự:

```python
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

Viết file trên ổ đĩa nhưng quên đưa vào `data` nghĩa là Odoo không load file đó.

---

# 19. Cài Estate và kiểm tra thủ công

## 19.1. Cài module

Thay `DATABASE_NAME` bằng database đang chạy:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -i estate --stop-after-init --no-http
```

Sau đó khởi động server:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf
```

Truy cập:

```text
http://localhost:8069
```

## 19.2. Checklist UI

1. Mở **Real Estate → Advertisements → Properties**.
2. Kiểm tra filter `Available` được bật.
3. Bấm New.
4. Nhập Title và Expected Price.
5. Bật Garden; Area phải thành `10`, Orientation thành `North`.
6. Lưu Property.
7. Vào tab Offers và thêm Offer.
8. Property phải chuyển sang `Offer Received`.
9. Best Price phải bằng Offer cao nhất.
10. Accept Offer hợp lệ; Buyer/Selling Price phải được cập nhật.
11. Bấm Sold; Property phải chuyển `Sold`.

## 19.3. Dữ liệu thử

```text
Property
Title: Test House
Expected Price: 100000
Living Area: 80
Garden Area: 20

Offer
Price: 95000
Partner: chọn một Contact
Validity: 7
```

Không dùng Offer `85000`, vì:

```text
100000 × 90% = 90000
85000 < 90000
```

Offer vẫn có thể được tạo, nhưng Accept sẽ bị constraint 90% từ chối.

---

# 20. Tests cho Estate

## 20.1. Tạo `tests/__init__.py`

```python
from . import test_estate
```

Không import test file thì test class không được discovery.

## 20.2. Tạo `tests/test_estate.py`

```python
from datetime import timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

from odoo.addons.estate.models import constants


@tagged("post_install", "-at_install")
class TestEstate(TransactionCase):
    """Integration tests chạy trong transaction và rollback sau từng test.

    post_install giúp test chạy sau khi module/registry đã load đầy đủ. Việc dùng
    TransactionCase cho phép kiểm tra ORM, SQL constraints và relational fields
    trên PostgreSQL thật mà không giữ lại dữ liệu test.
    """

    @classmethod
    def setUpClass(cls):
        """Tạo fixture dùng chung một lần để test chạy nhanh và nhất quán."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Estate Buyer"})
        cls.property_type = cls.env["estate.property.type"].create(
            {"name": "Test Apartment 19"}
        )
        cls.property = cls.env["estate.property"].create(
            {
                "name": "Test Property",
                "expected_price": 100_000,
                "living_area": 80,
                "garden_area": 20,
                "property_type_id": cls.property_type.id,
            }
        )

    def test_computed_fields_and_offer_flow(self):
        """Kiểm tra happy path từ property mới đến Sold."""
        # Compute không store vẫn được ORM tính khi đọc field.
        self.assertEqual(self.property.total_area, 100)

        # create offer phải đổi state property và cập nhật best_price.
        offer = self.env["estate.property.offer"].create(
            {
                "price": 95_000,
                "partner_id": self.partner.id,
                "property_id": self.property.id,
            }
        )
        self.assertEqual(
            self.property.state,
            constants.PROPERTY_STATE_OFFER_RECEIVED,
        )
        self.assertEqual(self.property.best_price, 95_000)
        self.assertEqual(
            offer.date_deadline,
            offer.create_date.date() + timedelta(days=offer.validity),
        )

        # Accept đồng bộ dữ liệu từ offer sang property trong một transaction.
        offer.action_accept()
        self.assertEqual(
            self.property.state,
            constants.PROPERTY_STATE_OFFER_ACCEPTED,
        )
        self.assertEqual(self.property.buyer_id, self.partner)
        self.assertEqual(self.property.selling_price, 95_000)

        # Chỉ property đã có buyer mới được chuyển sang Sold.
        self.property.action_sold()
        self.assertEqual(self.property.state, constants.PROPERTY_STATE_SOLD)

    def test_lower_offer_is_rejected(self):
        """Business create override phải chặn offer thấp hơn giá cao nhất."""
        self.env["estate.property.offer"].create(
            {
                "price": 95_000,
                "partner_id": self.partner.id,
                "property_id": self.property.id,
            }
        )
        with self.assertRaises(UserError):
            self.env["estate.property.offer"].create(
                {
                    "price": 90_000,
                    "partner_id": self.partner.id,
                    "property_id": self.property.id,
                }
            )

    def test_selling_price_constraint(self):
        """@api.constrains phải rollback giá bán dưới ngưỡng 90%."""
        with self.assertRaises(ValidationError):
            self.property.selling_price = 80_000

    def test_delete_business_rule(self):
        """@api.ondelete không cho xóa property đang có offer."""
        self.property.state = constants.PROPERTY_STATE_OFFER_RECEIVED
        with self.assertRaises(UserError):
            self.property.unlink()
```

## 20.3. Ý nghĩa của test

`TransactionCase` chạy ORM/PostgreSQL thật và rollback dữ liệu test. Test suite
bao phủ:

```text
compute Total Area
create Offer → state/best price/deadline
Accept → buyer/selling price/state
Sold
không cho Offer thấp hơn Best Offer
constraint 90%
quy tắc xóa
```

## 20.4. Chạy test

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -u estate --test-enable --test-tags /estate --stop-after-init --no-http
```

Kết quả mong đợi:

```text
0 failed, 0 error(s)
```

---

# 21. Tạo link module Estate Accounting

Không thêm dependency `account` trực tiếp vào `estate`. Ta tạo module đứng giữa:

```text
my_addons/
├── estate/
└── estate_account/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── constants.py
    │   └── estate_property.py
    └── tests/
        ├── __init__.py
        └── test_estate_account.py
```

Lợi ích:

```text
estate chạy độc lập không cần Accounting
estate_account chỉ được cài khi doanh nghiệp cần hóa đơn
```

## 21.1. `estate_account/__manifest__.py`

```python
{
    "name": "Real Estate Accounting",
    "version": "19.0.1.0.0",
    "summary": "Create customer invoices when real estate properties are sold",
    "author": "Minh Lam",
    "license": "LGPL-3",
    "category": "Sales/Real Estate",
    "depends": ["estate", "account"],
    "data": [],
    "installable": True,
    "application": False,
}
```

`application=False` vì đây không phải app có menu riêng. Nó âm thầm nối hai model:

```text
estate.property + account.move
```

## 21.2. `estate_account/__init__.py`

```python
from . import models
```

## 21.3. `estate_account/models/__init__.py`

```python
from . import estate_property
```

## 21.4. `estate_account/models/constants.py`

Những key và con số chỉ thuộc tích hợp kế toán được tách khỏi module Estate:

```python
"""Các hằng số nghiệp vụ riêng của phần tích hợp Estate–Accounting."""

# ``account.move.move_type`` dùng key này cho hóa đơn bán hàng của khách hàng.
CUSTOMER_INVOICE_MOVE_TYPE = "out_invoice"

# Các tham số tạo dòng hóa đơn khi property được đánh dấu Sold.
COMMISSION_PERCENT = 6
COMMISSION_RATE = COMMISSION_PERCENT / 100
COMMISSION_LINE_NAME = f"Real estate commission ({COMMISSION_PERCENT}%)"
ADMINISTRATIVE_FEE_LINE_NAME = "Administrative fees"
ADMINISTRATIVE_FEE_AMOUNT = 100.0
```

Nhờ vậy, khi doanh nghiệp đổi tỷ lệ hoa hồng hoặc phí hành chính, người maintain
chỉ sửa một nơi; model và test cùng dùng đúng một nguồn giá trị.

## 21.5. `estate_account/models/estate_property.py`

```python
from odoo import Command, models

from . import constants


class EstateProperty(models.Model):
    """Bổ sung việc tạo customer invoice vào workflow bán property."""

    # Không khai báo _name: ta mở rộng đúng model estate.property có sẵn.
    _inherit = "estate.property"

    def action_sold(self):
        """Gọi nghiệp vụ gốc, sau đó tạo một invoice cho mỗi property.

        Toàn bộ chạy trong cùng PostgreSQL transaction. Nếu invoice create lỗi,
        thay đổi state do super() cũng rollback; nhờ vậy không có property Sold
        nhưng thiếu invoice. Không dùng sudo nên ACL của user vẫn được tôn trọng.

        Returns:
            bool: Kết quả nguyên bản từ ``estate.property.action_sold``.

        Raises:
            UserError/AccessError/ValidationError: Được truyền nguyên từ logic
                gốc hoặc từ việc tạo invoice để transaction có thể rollback.
        """
        # super kiểm tra canceled/already sold/buyer và đổi state trước. Luôn giữ
        # super để không phá logic của estate hoặc module khác trong MRO.
        result = super().action_sold()
        for property_record in self:
            # self.env lấy account.move trong cùng cursor/user/context/cache.
            self.env["account.move"].create(
                {
                    # out_invoice là Customer Invoice, không phải vendor bill.
                    "move_type": constants.CUSTOMER_INVOICE_MOVE_TYPE,
                    # Many2one create value phải là integer ID, không phải recordset.
                    "partner_id": property_record.buyer_id.id,
                    # One2many nhận danh sách Commands. Hai line được tạo và liên
                    # kết với invoice trong cùng lệnh create/transaction.
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": constants.COMMISSION_LINE_NAME,
                                "quantity": 1,
                                # 6% giá bán đã được Accept Offer ghi lên property.
                                "price_unit": (
                                    property_record.selling_price
                                    * constants.COMMISSION_RATE
                                ),
                            }
                        ),
                        Command.create(
                            {
                                "name": constants.ADMINISTRATIVE_FEE_LINE_NAME,
                                "quantity": 1,
                                # account.move dùng currency của company/journal;
                                # 100.0 được hiểu theo đơn vị tiền tệ đó.
                                "price_unit": constants.ADMINISTRATIVE_FEE_AMOUNT,
                            }
                        ),
                    ],
                }
            )
        # Trả đúng kết quả action gốc để bảo toàn API contract/chaining.
        return result
```

## 21.5. Giải thích inheritance chain

Chỉ có `_inherit`, không `_name`, nên đây là override cùng model:

```text
User bấm Sold
→ estate.property.action_sold()
→ implementation của estate_account chạy
→ super().action_sold()
→ implementation gốc của estate chạy
→ kiểm tra buyer/state và chuyển Sold
→ quay lại estate_account
→ account.move.create()
```

Luôn gọi `super()` để giữ business logic gốc và các module khác trong MRO.

## 21.6. Hóa đơn được tạo

```text
move_type = out_invoice  → Customer Invoice
partner_id = buyer_id    → hóa đơn của Buyer
line 1 = 6% Selling Price
line 2 = Administrative fee 100
```

Hóa đơn mới ở trạng thái Draft vì code chưa gọi `action_post()`.

Không dùng `sudo()`, vì vậy người bấm Sold phải có quyền tạo `account.move`. Nếu
tạo Invoice lỗi, cùng transaction rollback cả state `Sold`.

## 21.7. Cài link module

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -i estate_account --stop-after-init --no-http
```

Odoo tự bảo đảm `estate` và `account` đã được cài trước.

---

# 22. Tests cho Estate Accounting

## 22.1. `estate_account/tests/__init__.py`

```python
from . import test_estate_account
```

## 22.2. `estate_account/tests/test_estate_account.py`

```python
from odoo.tests import TransactionCase, tagged

from odoo.addons.estate_account.models import constants


@tagged("post_install", "-at_install")
class TestEstateAccount(TransactionCase):
    """Kiểm tra contract giữa Estate workflow và Accounting ORM."""

    def test_sold_property_creates_customer_invoice(self):
        """Sold phải tạo đúng một customer invoice gồm đúng hai dòng phí."""
        # Chuẩn bị buyer, property và offer giống thao tác thực tế trên UI.
        partner = self.env["res.partner"].create({"name": "Invoice Buyer"})
        property_record = self.env["estate.property"].create(
            {"name": "Invoiced Property", "expected_price": 100_000}
        )
        offer = self.env["estate.property.offer"].create(
            {
                "price": 100_000,
                "partner_id": partner.id,
                "property_id": property_record.id,
            }
        )
        offer.action_accept()

        # Ghi nhận số invoice trước action để assertion không phụ thuộc dữ liệu
        # có sẵn trong database chạy test.
        invoice_count = self.env["account.move"].search_count(
            [
                ("move_type", "=", constants.CUSTOMER_INVOICE_MOVE_TYPE),
                ("partner_id", "=", partner.id),
            ]
        )
        # Đây là method đã được estate_account override; super đổi state trước,
        # sau đó extension tạo account.move trong cùng transaction.
        property_record.action_sold()
        invoice = self.env["account.move"].search(
            [
                ("move_type", "=", constants.CUSTOMER_INVOICE_MOVE_TYPE),
                ("partner_id", "=", partner.id),
            ],
            order="id desc",
            limit=1,
        )

        self.assertEqual(
            self.env["account.move"].search_count(
                [
                    ("move_type", "=", constants.CUSTOMER_INVOICE_MOVE_TYPE),
                    ("partner_id", "=", partner.id),
                ]
            ),
            invoice_count + 1,
        )
        # Một dòng commission 6% của 100,000 và một dòng admin fee 100.
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        self.assertEqual(
            sorted(invoice.invoice_line_ids.mapped("price_unit")),
            sorted(
                [
                    constants.ADMINISTRATIVE_FEE_AMOUNT,
                    100_000 * constants.COMMISSION_RATE,
                ]
            ),
        )
```

## 22.3. Chạy test cả hai module

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -u estate,estate_account --test-enable --test-tags /estate,/estate_account --stop-after-init --no-http
```

---

# 23. Flow runtime đầy đủ

## 23.1. Mở menu Properties

```text
User bấm menu Properties
→ ir.ui.menu: estate_menu_property_list
→ action: estate_property_action
→ res_model: estate.property
→ view_mode: list,kanban,form
→ context bật Available
→ web client load List/Search View
→ ORM search/read
→ PostgreSQL SELECT estate_property
```

## 23.2. Tạo Property

```text
Bấm New
→ web client gọi default_get()
→ record tạm chưa có ID
→ nhập field/onchange
→ rời form hoặc bấm button
→ FormController gọi record.save()
→ RPC estate.property.web_save([], vals)
→ web_save gọi create(vals)
→ ORM ACL/default/conversion/constraints
→ INSERT estate_property
→ trả ID về browser
```

## 23.3. Tạo Offer trong One2many

```text
Nhập Price + Partner tại Add a line
→ browser giữ x2many command
→ save Property
→ ORM tạo estate.property.offer
→ Offer.create(vals_list)
→ kiểm tra Best Price
→ super().create()
→ INSERT estate_property_offer
→ property_id tự nối Property cha
→ Property state = offer_received
→ best_price được recompute
```

## 23.4. Accept Offer

```text
Bấm icon check
→ XML button type=object, name=action_accept
→ RPC offer.action_accept()
→ status=accepted
→ Property.write({buyer_id, selling_price, state})
→ constraint 90% chạy
├── hợp lệ: commit toàn bộ
└── không hợp lệ: rollback toàn bộ
```

## 23.5. Sold và Invoice

```text
Bấm Sold
→ XML gọi estate.property.action_sold()
→ estate_account override chạy
→ super() gọi estate action gốc
→ kiểm tra buyer/state, đổi Sold
→ account.move.create()
→ tạo Draft Invoice và hai Invoice Lines
→ commit
```

---

# 24. Debug từng tầng

## 24.1. Breakpoint quan trọng

Đặt breakpoint tại:

```text
estate_property_offer.py:create
estate_property_offer.py:action_accept
estate_property.py:_check_selling_price
estate_property.py:action_sold
estate_account/estate_property.py:action_sold
```

Quan sát:

```python
self
self.env.user
self.env.context
vals_list
offer.partner_id
property_record.buyer_id
property_record.selling_price
```

## 24.2. Odoo Shell

Mở terminal thứ hai:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin shell -c .\odoo.conf -d DATABASE_NAME
```

Thử tạo dữ liệu:

```python
partner = env["res.partner"].create({"name": "Shell Buyer"})

property_record = env["estate.property"].create({
    "name": "Shell House",
    "expected_price": 100_000,
})

offer = env["estate.property.offer"].create({
    "price": 95_000,
    "partner_id": partner.id,
    "property_id": property_record.id,
})

offer.action_accept()
property_record.action_sold()
env.cr.commit()
```

Trong Shell, nhớ `env.cr.commit()` nếu muốn giữ dữ liệu sau khi thoát.

## 24.3. Kiểm tra model/table

```text
estate.property       → estate_property
estate.property.offer → estate_property_offer
estate.property.type  → estate_property_type
estate.property.tag   → estate_property_tag
res.partner           → res_partner
res.users             → res_users
account.move          → account_move
```

---

# 25. Các lỗi thường gặp

## 25.1. Module không xuất hiện

Kiểm tra:

```text
addons_path có my_addons
folder có __manifest__.py
installable=True
đã Update Apps List
```

## 25.2. Model không tồn tại

Kiểm tra chuỗi import:

```text
estate/__init__.py → from . import models
models/__init__.py → import đúng file model
```

## 25.3. Sửa XML nhưng UI không đổi

XML đã được lưu thành record database. Chạy:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -u estate --stop-after-init --no-http
```

Sau đó restart server và `Ctrl+F5`.

## 25.4. Access Error

Kiểm tra:

```text
ir.model.access.csv đã nằm trong manifest
model_id đúng
user thuộc đúng group
record rule có chặn record không
```

## 25.5. IDE không tìm thấy import Odoo

Chọn interpreter:

```text
D:\code\Python\odoo-v19-practice\.venv\Scripts\python.exe
```

Runtime đúng quan trọng hơn inspection của IDE.

## 25.6. `action_sold()` dường như không được gọi

Nó được gọi động từ XML:

```xml
<button name="action_sold" type="object"/>
```

IDE không luôn tìm được dynamic RPC usage. Nếu `estate_account` đã cài, Registry
gọi bản override trước, rồi `super()` mới gọi bản gốc.

## 25.7. Offer lưu được nhưng Accept báo 90%

Hai rule khác nhau:

```text
Create Offer → price > 0 và không thấp hơn Best Offer
Accept Offer → Selling Price không thấp hơn 90% Expected Price
```

Offer thấp có thể được ghi nhận như một đề nghị, nhưng người bán không được Accept.

## 25.8. Upgrade rất lâu

Odoo update module list, build Registry, kiểm tra schema và load lại XML. Database
từ xa làm hàng trăm truy vấn chậm hơn. Không bấm Upgrade nhiều lần hoặc chạy hai
tiến trình `-u` cùng lúc.

---

# 26. Cách tự code lại mà không bị ngợp

Không viết tất cả một lần. Làm theo các checkpoint sau.

## Checkpoint 1 – Module rỗng cài được

```text
estate/__manifest__.py
estate/__init__.py
estate/models/__init__.py
```

Mục tiêu: module xuất hiện và cài không lỗi.

## Checkpoint 2 – Property cơ bản

Chỉ viết:

```python
_name = "estate.property"
name = fields.Char(required=True)
expected_price = fields.Float(required=True)
```

Thêm ACL, List/Form, Action và Menu. Mục tiêu: tạo được Property.

## Checkpoint 3 – Đầy đủ field và view

Thêm các field còn lại, default, state, List/Form/Search/Kanban.

## Checkpoint 4 – Compute và onchange

Thêm:

```text
total_area
garden onchange
```

Tự kiểm tra trên form.

## Checkpoint 5 – Type và Tag

Thêm hai model danh mục, quan hệ Many2one/Many2many, menu Configuration.

## Checkpoint 6 – Offer

Thêm Offer model, One2many, deadline, Best Price và create override.

## Checkpoint 7 – Workflow

Thêm Accept/Refuse/Sold/Cancel và constraints. Kiểm tra rollback.

## Checkpoint 8 – Inheritance

Mở rộng `res.users`, thêm tab Real Estate Properties.

## Checkpoint 9 – Automated tests

Viết test happy path trước, sau đó test lỗi.

## Checkpoint 10 – Link module

Tạo `estate_account`, override `action_sold()` và test Invoice.

Sau mỗi checkpoint:

```text
restart nếu sửa Python
upgrade nếu sửa schema/XML/CSV
đọc log
test đúng một flow nhỏ
commit code nếu dùng Git
```

---

# 27. Bài tập tự luyện

## Bài 1

Thêm field `furnished` vào Property, đưa vào Form và filter “Furnished”.

## Bài 2

Thêm constraint `garden_area >= 0`.

## Bài 3

Thêm nút stat button trên Property để mở tất cả Offer của Property đó.

## Bài 4

Tạo group `Estate Agent` và `Estate Manager`; chỉ Manager được bấm Sold.

## Bài 5

Tạo Portal Buyer:

```text
Public xem Property Available
Portal tạo Offer với partner_id=user.partner_id
Portal chỉ xem Offer của mình
Manager Accept/Refuse
```

## Bài 6

Thêm field liên kết Invoice vào Property và stat button mở Invoice.

---

# 28. Bản đồ file cuối cùng

| File | Trách nhiệm |
|---|---|
| `estate/__manifest__.py` | metadata, dependency, data load order |
| `estate/__init__.py` | bắt đầu import Python |
| `models/__init__.py` | import từng model file |
| `estate_property.py` | model trung tâm, workflow, constraints |
| `estate_property_offer.py` | Offer, deadline, Accept/Refuse |
| `estate_property_type.py` | danh mục Type, offer count |
| `estate_property_tag.py` | danh mục Tag màu |
| `res_users.py` | mở rộng user bằng property list |
| `ir.model.access.csv` | model-level access |
| `estate_property_views.xml` | Property views và action |
| `estate_property_offer_views.xml` | Offer views và action |
| `estate_property_type_views.xml` | Type views/stat button/action |
| `estate_property_tag_views.xml` | Tag views/action |
| `res_users_views.xml` | inherited Users form |
| `estate_menus.xml` | menu tree |
| `tests/test_estate.py` | test nghiệp vụ Estate |
| `estate_account/__manifest__.py` | link dependencies |
| `estate_account/models/estate_property.py` | tạo Invoice khi Sold |
| `estate_account/tests/test_estate_account.py` | test tích hợp Accounting |

---

# 29. Vì sao code được thiết kế như vậy?

Phần này gom các câu hỏi “tại sao không làm cách đơn giản hơn?” để bạn hiểu thiết
kế, thay vì chỉ thuộc code.

## 29.1. Tại sao tách Property, Offer, Type và Tag thành model riêng?

Nếu nhét mọi thứ vào một table Property:

```text
offer_1_price, offer_1_partner,
offer_2_price, offer_2_partner, ...
```

ta không biết trước một Property có bao nhiêu Offer và rất khó query. Tách Offer
thành model con tạo quan hệ một-nhiều không giới hạn:

```text
Property 1 ── n Offer
```

Type là master data có cấu trúc “một Property thuộc một Type”; Tag là phân loại
mềm “một Property có nhiều Tag và một Tag dùng cho nhiều Property”. Vì vậy:

```text
Type → Many2one
Tag  → Many2many
Offer → One2many/Many2one
```

## 29.2. Tại sao Buyer dùng `res.partner`, không dùng `res.users`?

`res.partner` đại diện cá nhân/công ty; không phải Buyer nào cũng có tài khoản
đăng nhập. `res.users` đại diện credentials và quyền truy cập, đồng thời trỏ tới
một Partner:

```text
res.users.partner_id → res.partner
```

Hóa đơn, đơn hàng và Offer nên đứng tên Partner. Login chỉ cần khi khách sử dụng
Portal.

## 29.3. Tại sao Salesperson lại dùng `res.users`?

Salesperson là nhân viên thao tác trong backend, cần danh tính user để áp dụng
quyền, record rules và `env.user`. Vì vậy Property dùng:

```python
user_id = fields.Many2one("res.users")
```

## 29.4. Tại sao `offer_ids` là One2many nhưng table Property không có column đó?

Foreign key nằm ở phía “nhiều”:

```text
estate_property_offer.property_id
```

Khi đọc `property.offer_ids`, ORM tìm các Offer có `property_id` bằng Property
hiện tại. Lưu một array ID trong Property sẽ phá chuẩn quan hệ và khó bảo đảm tính
toàn vẹn.

## 29.5. Tại sao `best_price` là compute, không cập nhật thủ công?

Best Price là dữ liệu có thể suy ra:

```text
max(offer_ids.price)
```

Nếu vừa lưu `best_price` vừa lưu Offer, hai nguồn có thể lệch nhau. Compute làm
Offer trở thành source of truth. Bản hiện tại không `store=True` vì dataset học
tập nhỏ; production có thể cân nhắc store/aggregate query khi dữ liệu lớn.

## 29.6. Tại sao Total Area cũng là compute?

```text
total_area = living_area + garden_area
```

Người dùng không nên tự nhập một giá trị có thể mâu thuẫn với hai thành phần.
`@api.depends` giúp ORM tự tính lại khi dependency đổi.

## 29.7. Tại sao Garden dùng onchange thay vì compute?

Garden Area vẫn là dữ liệu người dùng có thể sửa. Onchange chỉ đưa giá trị gợi ý
ban đầu `10/North`. Nếu dùng compute bắt buộc, user không thể nhập vườn 50 m² hoặc
hướng South theo nghiệp vụ thực tế.

## 29.8. Tại sao giá dương dùng SQL constraint?

Điều kiện đơn giản:

```sql
CHECK(price > 0)
```

nên để database bảo vệ cuối cùng cho mọi nguồn ghi và tránh race condition. Rule
cần logic ORM/quan hệ/thông báo phức tạp phù hợp với Python constraint.

## 29.9. Tại sao rule 90% nằm trên Property, không nằm trên Offer?

Offer thấp vẫn là một đề nghị hợp lệ cần được ghi nhận. Rule nghiệp vụ là “không
được **bán chính thức** dưới 90%”, và hai field liên quan đều ở Property:

```text
selling_price và expected_price
```

Khi Accept, Offer.price được copy vào selling_price; lúc đó constraint chạy.
Đặt constraint trên Property còn bảo vệ import/RPC/module khác ghi selling_price.

## 29.10. Tại sao Offer mới không được thấp hơn Best Offer?

Đây là yêu cầu bài học để minh họa override `create()`. Ta kiểm tra trước
`super().create()` để không INSERT dữ liệu sai. `@api.model_create_multi` giữ
method đúng với batch API của Odoo.

## 29.11. Tại sao phải gọi `super().create()`?

`super()` thực hiện các bước ORM chuẩn:

```text
ACL → defaults → conversion → INSERT → constraints → recompute
```

Tự viết SQL INSERT sẽ bỏ qua nhiều cơ chế và làm module khác không thể chain
inheritance đúng cách.

## 29.12. Tại sao state là Selection?

Workflow có tập trạng thái hữu hạn. Selection lưu technical key ổn định:

```text
offer_received
```

và hiển thị label có thể dịch:

```text
Offer Received
```

Không dùng label làm business value vì label có thể thay đổi hoặc dịch.

## 29.13. Tại sao check vẫn nằm trong method khi button đã invisible?

`invisible` chỉ ngăn click trên một view. Method vẫn có thể được gọi từ RPC,
Shell, test hoặc module khác. Business invariant phải ở server:

```python
if property_record.state == constants.PROPERTY_STATE_SOLD:
    raise UserError(...)
```

## 29.14. Tại sao Window Action cần `res_model`?

Menu chỉ biết action nào chạy. Action cần biết resource model cung cấp record:

```text
Menu → Action → res_model → View/ORM
```

`res_model` không trỏ trực tiếp table; nó trỏ ORM model. ORM mới áp dụng security,
compute, relations và sinh SQL cho table.

## 29.15. Tại sao `view_mode` có ba giá trị?

```text
list   → duyệt nhiều record
kanban → nhìn theo card/group
form   → xem/sửa một record
```

Mode đầu tiên là mặc định. Form vẫn cần trong action để New và mở record có giao
diện phù hợp.

## 29.16. Tại sao Menu load cuối manifest?

Menu lá tham chiếu XML ID của action. XML loader xử lý từ trên xuống, nên action
phải tồn tại trước reference. External ID giải quyết liên kết giữa các record data
files mà không dựa vào numeric database ID.

## 29.17. Tại sao `estate_account` là module riêng?

Nếu `estate` phụ thuộc `account`, mọi người chỉ muốn học/quản lý bất động sản cũng
phải cài Accounting. Link module cho phép dependency tùy chọn:

```text
estate độc lập
account độc lập
estate_account nối hai bên
```

Đây là pattern phổ biến của Odoo để tránh coupling giữa business apps.

## 29.18. Tại sao override Sold gọi `super()` trước rồi mới tạo Invoice?

Method gốc kiểm tra Buyer và trạng thái. Nếu không hợp lệ, không nên tạo hóa đơn.
Sau khi `super()` thành công, ta biết Property đủ điều kiện bán. Tất cả vẫn trong
một transaction; Invoice lỗi thì state Sold rollback.

## 29.19. Tại sao dùng `Command.create()`?

`invoice_line_ids` là One2many. ORM cần biết mỗi phần tử là “tạo line mới”, không
phải ID có sẵn. `Command.create(values)` biểu đạt operation rõ ràng và an toàn:

```python
"invoice_line_ids": [
    Command.create({...}),
    Command.create({...}),
]
```

## 29.20. Tại sao không dùng `sudo()` khi tạo Invoice?

`sudo()` bỏ qua access rights và có thể để một Estate User không có quyền kế toán
tạo chứng từ tài chính. Không dùng `sudo()` buộc hệ thống tôn trọng phân quyền. Nếu
quy trình yêu cầu service user, phải thiết kế và audit rõ ràng thay vì thêm sudo
để “hết lỗi”.

## 29.21. Tại sao cần tests nếu đã thử UI?

UI chỉ kiểm tra một đường thao tác. Tests gọi ORM trực tiếp, xác nhận invariant và
rollback, chạy lại được sau mọi lần refactor. Một thay đổi nhỏ trong Offer không
được âm thầm phá invoice khi Sold.

## 29.22. Tại sao dùng module `constants.py` thay vì `enum.Enum`?

Odoo trao đổi các giá trị Selection trực tiếp dưới dạng chuỗi:

```text
Python ORM ↔ JSON/RPC ↔ XML domain ↔ PostgreSQL
              "sold"
```

Nếu dùng `enum.Enum`, mỗi lần ghi, so sánh hoặc tạo domain lại phải nhớ lấy
`.value`. Điều đó làm code bài học dài hơn và dễ vô tình truyền một Enum object
vào ORM. Hằng chuỗi có tên giải quyết đúng vấn đề maintain mà vẫn khớp API Odoo:

```python
PROPERTY_STATE_SOLD = "sold"

if property_record.state == constants.PROPERTY_STATE_SOLD:
    ...
```

`frozenset` được dùng cho nhóm trạng thái vì nhóm đó không nên bị code khác sửa
nhầm lúc runtime:

```python
PROPERTY_CLOSED_STATES = frozenset(
    {PROPERTY_STATE_SOLD, PROPERTY_STATE_CANCELED}
)
```

## 29.23. Chuỗi nào nên và không nên đưa vào constants?

| Đưa vào constants | Để tại nơi sử dụng |
|---|---|
| Key Selection: `sold`, `accepted` | Thông báo `UserError`, `ValidationError` |
| Nhóm state được phép/cấm | Help text chỉ dùng ở một field |
| Tỷ lệ 90%, hoa hồng 6% | Tên model và tên field ORM |
| Default 3 tháng, 7 ngày | XML ID và tên method button |
| Key kỹ thuật `out_invoice` | Chuỗi dịch phụ thuộc ngữ cảnh |

Lý do: constants phục vụ giá trị kỹ thuật hoặc chính sách dùng lại. Nếu gom mọi
câu chữ vào một file, người đọc phải nhảy qua lại liên tục và Odoo khó trích dịch
đúng ngữ cảnh hơn.

XML view không import được Python module. Vì vậy các biểu thức như
`state == 'sold'` trong XML vẫn dùng chuỗi. Khi đổi một key Selection, hãy tìm
toàn project và sửa cả Python, XML, test:

```powershell
rg 'sold|PROPERTY_STATE_SOLD' .\my_addons\estate .\my_addons\estate_account
```

## 29.24. Chuẩn docstring cho mỗi loại hàm

Không cần docstring dài giống nhau một cách máy móc. Hãy trả lời đúng các câu hỏi
mà người maintain cần biết:

```python
def action_example(self):
    """Một câu nói rõ mục đích nghiệp vụ.

    Ai gọi hàm và hàm thay đổi record nào. Nêu rõ quy tắc không hiển nhiên và
    transaction nếu có.

    Args:
        values: Chỉ ghi khi hàm thực sự nhận tham số ngoài self.

    Raises:
        UserError: Điều kiện nghiệp vụ khiến hàm dừng.

    Returns:
        bool: Ý nghĩa của giá trị trả về.

    Side effects:
        Ghi field hoặc tạo record nào; dùng cho compute/onchange/inverse.
    """
```

Áp dụng theo loại hàm:

| Loại hàm | Docstring cần nói rõ |
|---|---|
| Default | Odoo gọi lúc nào và trả kiểu record/value gì |
| Compute | `@api.depends` nào kích hoạt và field nào được gán |
| Onchange | Chỉ đổi form tạm, chưa ghi database |
| Constraint | Khi chạy và exception nào được raise |
| CRUD override | Kiểu `vals`, thời điểm gọi `super()`, recordset trả về |
| Button action | Transition, điều kiện cấm, record bị ghi và return |
| Helper | Một trách nhiệm duy nhất và lý do helper tồn tại |

## 29.25. Checklist trước khi thêm một hàm mới

1. Đặt tên theo hành động: `_compute_*`, `_check_*`, `_default_*`, `action_*`.
2. Nếu logic lặp lại chuỗi kỹ thuật/con số chính sách, thêm constant có tên.
3. Không dùng `lambda` nếu logic cần giải thích, breakpoint hoặc nhiều điều kiện.
4. Viết docstring trước: ai gọi, thay đổi gì, lỗi gì, trả gì.
5. Luôn nhớ `self` có thể có nhiều record; chỉ `ensure_one()` khi thật sự cần một.
6. Gọi `super()` trong CRUD/inherited method để giữ lifecycle và MRO của Odoo.
7. Viết test cho happy path và ít nhất một đường bị từ chối.
8. Cập nhật tutorial nếu code mẫu đã đổi.

---

# 30. Một buổi thực hành từ folder trống, từng bước tuyệt đối

Phần này là checklist cầm tay. Chỉ chuyển bước khi tiêu chí “đạt” đúng.

Trước khi bắt đầu, cấu trúc project nên là:

```text
project-root/
├── odoo/
│   └── addons/          ← module chuẩn, không đặt estate ở đây
├── my_addons/           ← tự tạo
├── odoo.conf
└── odoo-bin             ← nếu bản source có launcher này
```

Trong `odoo.conf`:

```ini
[options]
addons_path = odoo/addons,my_addons
```

Nếu project của bạn còn có một folder addons chuẩn khác, giữ nó trong danh sách.
Mục tiêu là **bổ sung** `my_addons`, không xóa đường dẫn chuẩn đang hoạt động.

## Bước 1 – Tạo module shell

### Việc cần làm

Trong `my_addons`, tạo folder và file:

```text
my_addons/
└── estate/
    ├── __init__.py
    ├── __manifest__.py
    └── models/
        └── __init__.py
```

`estate/__manifest__.py`:

```python
{
    "name": "Real Estate",
    "version": "19.0.1.0.0",
    "depends": ["base"],
    "data": [],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
```

`estate/__init__.py`:

```python
from . import models
```

`estate/models/__init__.py` tạm thời để rỗng:

```python
# Các model sẽ được import tại đây ở bước tiếp theo.
```

### Tại sao làm như vậy?

```text
__manifest__.py → Odoo nhận diện folder là một module
root __init__.py → Python đi vào package models
models/__init__.py → nơi liệt kê model file cần import
data=[] → chưa yêu cầu Odoo đọc file chưa tồn tại
```

### Chạy và kiểm tra

Restart server, bật Developer Mode, vào Apps → Update Apps List rồi tìm
`Real Estate`. Chưa cần Install nếu bạn muốn tiếp tục ngay Bước 2; hoặc có thể
Install module shell để kiểm tra discovery.

```text
Đạt: module xuất hiện trong Apps.
Không đạt:
1. Kiểm tra my_addons có trong addons_path.
2. Kiểm tra tên chính xác là __manifest__.py, có hai dấu gạch dưới.
3. Kiểm tra dictionary Python có đóng đủ ngoặc và dấu phẩy.
4. Đọc traceback đầu tiên trong terminal, không chỉ dòng cuối.
```

## Bước 2 – Tạo model Property nhỏ nhất

### Việc cần làm

Tạo `estate/models/estate_property.py`:

```python
from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(string="Title", required=True)
    expected_price = fields.Float(required=True)
```

Sửa `estate/models/__init__.py`:

```python
from . import estate_property
```

### Tại sao cần cả file model và import?

File `.py` nằm trên ổ đĩa chưa tự chạy. Chuỗi thực tế là:

```text
Odoo import estate
→ estate/__init__.py import models
→ models/__init__.py import estate_property
→ Python thực thi class EstateProperty
→ Odoo đăng ký estate.property vào Registry
```

`_name` tạo technical model name; table mặc định là `estate_property`. Hai field
là metadata để ORM tạo/cập nhật columns khi install hoặc upgrade.

### Chạy và kiểm tra

Nếu module chưa cài:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -i estate --stop-after-init --no-http
```

Nếu module đã cài ở Bước 1:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin server -c .\odoo.conf -d DATABASE_NAME -u estate --stop-after-init --no-http
```

Mở Odoo Shell:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin shell -c .\odoo.conf -d DATABASE_NAME
```

Gõ:

```python
env["estate.property"]
env["estate.property"]._table
env["estate.property"]._fields.keys()
```

Kết quả `_table` phải là `estate_property`, và fields phải chứa `name`,
`expected_price` cùng các automatic fields.

```text
Đạt: Odoo Shell nhận env["estate.property"].
Không đạt:
1. KeyError estate.property → kiểm tra cả hai __init__.py.
2. ModuleNotFoundError → kiểm tra tên file/import có giống nhau.
3. Column chưa có → bạn mới restart nhưng chưa upgrade.
```

## Bước 3 – Thêm ACL

### Việc cần làm

Tạo folder `estate/security`, sau đó tạo
`estate/security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_estate_property_staff,access_estate_property_staff,model_estate_property,base.group_user,1,1,1,1
```

Sửa manifest từ:

```python
"data": [],
```

thành:

```python
"data": [
    "security/ir.model.access.csv",
],
```

### Tại sao cần ACL?

Model tồn tại không có nghĩa user được truy cập. Dòng CSV nói:

```text
Internal User (base.group_user)
→ được read/write/create/unlink
→ trên model estate.property
```

`model_estate_property` là external ID Odoo tạo từ `_name="estate.property"`.

### Chạy và kiểm tra

Upgrade `estate`. Đăng nhập bằng Internal User rồi thử truy cập model sau khi có
menu ở bước kế tiếp. Hiện tại có thể kiểm tra ACL trong Developer Mode tại:

```text
Settings → Technical → Security → Access Rights
```

```text
Đạt: Internal User không còn Access Error khi gọi model.
Không đạt:
1. External ID not found → model chưa vào Registry hoặc model_id viết sai.
2. ACL không đổi → CSV chưa có trong manifest hoặc chưa upgrade.
3. Admin làm được không chứng minh ACL đúng; hãy thử Internal User thường.
```

## Bước 4 – Tạo List/Form/Action/Menu tối thiểu

### Việc cần làm: View và Action

Tạo folder `estate/views`, rồi tạo `estate/views/estate_property_views.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="estate_property_view_list" model="ir.ui.view">
        <field name="name">estate.property.list</field>
        <field name="model">estate.property</field>
        <field name="arch" type="xml">
            <list string="Properties">
                <field name="name"/>
                <field name="expected_price"/>
            </list>
        </field>
    </record>

    <record id="estate_property_view_form" model="ir.ui.view">
        <field name="name">estate.property.form</field>
        <field name="model">estate.property</field>
        <field name="arch" type="xml">
            <form string="Property">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="expected_price"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="estate_property_action" model="ir.actions.act_window">
        <field name="name">Properties</field>
        <field name="res_model">estate.property</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

### Việc cần làm: Menu

Tạo `estate/views/estate_menus.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <menuitem id="estate_menu_root"
              name="Real Estate"
              sequence="10"/>

    <menuitem id="estate_menu_properties"
              name="Advertisements"
              parent="estate_menu_root"
              sequence="10"/>

    <menuitem id="estate_menu_property_list"
              name="Properties"
              parent="estate_menu_properties"
              action="estate_property_action"
              sequence="10"/>
</odoo>
```

### Việc cần làm: Load files từ manifest

Manifest lúc này:

```python
"data": [
    "security/ir.model.access.csv",
    "views/estate_property_views.xml",
    "views/estate_menus.xml",
],
```

Thứ tự có chủ đích:

```text
ACL → View/Action → Menu tham chiếu Action
```

### Tại sao cần cả bốn thành phần?

```text
Model  → dữ liệu và logic
View   → cách hiển thị field
Action → mở model bằng loại view nào
Menu   → nơi user bấm để chạy action
```

Menu không trực tiếp “mở file view”. Menu trỏ action; action chỉ model và mode;
web client tìm view tương ứng trong database.

### Chạy và kiểm tra

Upgrade `estate`, restart server rồi `Ctrl+F5` trình duyệt.

```text
Đạt: bấm menu mở list và New mở form.
Không đạt:
1. Menu không hiện → kiểm tra file menu trong manifest và ACL.
2. External ID action not found → file menu đang load trước file view/action.
3. Field không tồn tại → XML dùng tên chưa khai báo trong Python.
4. UI vẫn cũ → chưa upgrade, hoặc đang chạy nhầm database/addons_path.
```

## Bước 5 – Tạo record đầu tiên

### Việc cần làm

Chạy server bình thường:

```powershell
.\.venv\Scripts\python.exe .\odoo-bin -c .\odoo.conf -d DATABASE_NAME
```

Mở:

```text
Real Estate → Advertisements → Properties → New
```

Nhập:

```text
Title = First House
Expected Price = 100000
```

Rời form hoặc bấm nút lưu nếu giao diện hiển thị. Odoo 19 có thể tự lưu khi rời
Form. Sau đó mở record lại.

### Điều gì vừa xảy ra?

```text
Gõ field
→ browser giữ changes tạm, record dirty
→ hành động Save/rời Form gọi record.save()
→ RPC estate.property.web_save()
→ record mới nên ORM gọi create(values)
→ ACL/default/conversion/constraints
→ INSERT estate_property
→ database trả ID
→ browser chuyển record tạm thành record thật
```

```text
Đạt: record có ID và dữ liệu vẫn còn.
Không đạt:
1. Required field → nhập đủ Title và Expected Price.
2. Access Error → quay lại ACL ở Bước 3.
3. Record mất sau refresh → request save đã lỗi hoặc transaction rollback.
4. Mở DevTools → Network và tìm request web_save; xem terminal traceback.
```

## Bước 6 – Thêm toàn bộ Property fields

### Chỉ thêm field chưa phụ thuộc custom model

Ở bước này **không copy toàn bộ Phần 7**. Chỉ thêm các field scalar và quan hệ tới
model chuẩn đã tồn tại:

```text
description, postcode, date_availability
selling_price, bedrooms, living_area, facades
garage, garden, garden_area, garden_orientation
active, state
user_id → res.users
buyer_id → res.partner
```

Chưa thêm ba field sau:

```text
property_type_id → vì estate.property.type chưa tạo
tag_ids           → vì estate.property.tag chưa tạo
offer_ids         → vì estate.property.offer chưa tạo
```

Copy đúng khai báo của các field scalar từ Phần 7 vào class `EstateProperty`.
Nhớ thêm import:

```python
from dateutil.relativedelta import relativedelta

from . import constants
```

Đồng thời tạo hai named default methods `_default_date_availability()` và
`_default_salesperson()` như Phần 7 rồi truyền tên hàm vào `default=...`. Không
viết lại dưới dạng `lambda`, vì named method dễ đọc, đặt breakpoint và giải thích
bằng docstring hơn.

Sau đó upgrade module. Chỉ khi Python/schema upgrade thành công mới thêm từng
`<field>` tương ứng vào Form. Không thêm XML field trước Python field, vì view
validation sẽ báo “field does not exist”.

```text
Đạt: default Bedrooms=2, Date Availability=+3 tháng.
Không đạt:
1. NameError relativedelta → thiếu import.
2. Field không thấy trên UI → chưa thêm vào XML hoặc chưa upgrade.
3. Column does not exist → server đang dùng Registry/schema cũ.
```

## Bước 7 – Thêm compute/onchange

### Việc cần làm

Từ Phần 7, thêm:

```text
total_area = fields.Integer(compute="_compute_total_area")
@api.depends("living_area", "garden_area")
_compute_total_area()

@api.onchange("garden")
_onchange_garden()
```

Sửa import thành:

```python
from odoo import api, fields, models
```

Thêm `garden`, `garden_area`, `garden_orientation`, `total_area` lên Form rồi
upgrade module.

### Tại sao tách hai cơ chế?

```text
total_area → luôn suy ra từ dữ liệu, nên dùng compute
garden defaults → chỉ là gợi ý nhập liệu có thể sửa, nên dùng onchange
```

```text
Đạt: 80 + 20 = 100; bật Garden gợi ý 10/North.
Không đạt: kiểm tra @api.depends, tên compute và field trong Form.
```

## Bước 8 – Thêm Type và Tag

### Thứ tự an toàn

1. Tạo `estate_property_type.py` theo Phần 5, nhưng ở checkpoint này tạm bỏ
   `offer_ids` và `offer_count` vì Offer chưa tồn tại. Có thể giữ `property_ids`
   sau khi Property đã có `property_type_id`.
2. Tạo `estate_property_tag.py` đầy đủ theo Phần 6.
3. Import hai file trong `models/__init__.py`.
4. Thêm hai dòng ACL vào CSV.
5. Restart + upgrade để hai model vào Registry.
6. Lúc này mới thêm vào Property:

```python
property_type_id = fields.Many2one(
    comodel_name="estate.property.type",
    string="Property Type",
)
tag_ids = fields.Many2many(
    comodel_name="estate.property.tag",
    string="Tags",
)
```

7. Tạo Tag view đầy đủ theo Phần 14. Với Type view ở Phần 13, tạm bỏ
   `oe_button_box` và nút Offers vì `estate_property_offer_action` chưa tồn tại.
8. Thêm view files vào manifest.
9. Thêm menu Configuration sau khi actions đã được load.
10. Upgrade lại rồi tạo thử `Villa` và `Luxury`.

Tạm thời có thể bỏ `property_ids`, `offer_ids`, `offer_count` khỏi Type nếu muốn
học từng lát nhỏ. Chúng sẽ được bổ sung sau khi Property/Offer relations đầy đủ.

```text
Đạt: tạo Villa/Luxury và chọn được trên Property.
Không đạt: kiểm tra comodel có trong Registry trước khi nối relation.
```

## Bước 9 – Thêm Offer tối thiểu

### Việc cần làm

Tạo `estate_property_offer.py` phiên bản nhỏ nhất:

```python
from odoo import fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    price = fields.Float(required=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
    )
    property_id = fields.Many2one(
        comodel_name="estate.property",
        required=True,
        ondelete="cascade",
    )
```

Import file trong `models/__init__.py`, thêm ACL Offer và upgrade. Sau khi model
Offer tồn tại, thêm phía ngược vào Property:

```python
offer_ids = fields.One2many(
    comodel_name="estate.property.offer",
    inverse_name="property_id",
    string="Offers",
)
```

Thêm một tab Offers tối thiểu vào Property Form:

```xml
<page string="Offers" name="offers">
    <field name="offer_ids">
        <list editable="bottom">
            <field name="price"/>
            <field name="partner_id"/>
        </list>
    </field>
</page>
```

Upgrade rồi thêm một dòng. ORM tự gắn `property_id` vì `offer_ids` khai báo
`inverse_name="property_id"`.

```text
Đạt: Add a line tạo row estate_property_offer có property_id đúng.
Không đạt: kiểm tra inverse_name hai phía.
```

## Bước 10 – Thêm deadline, Best Price và create override

### Thứ tự thêm

1. Hoàn thiện Offer fields `status`, `validity`, `date_deadline` theo Phần 8.
2. Thêm related field `property_type_id` sau khi Type đã tồn tại.
3. Thêm `_price_positive`.
4. Thêm compute/inverse deadline.
5. Thêm `best_price` và `_compute_best_price()` vào Property.
6. Cuối cùng thêm override `create()` của Offer.
7. Upgrade và tạo Offer theo thứ tự `90 → 95 → 92`.

Giá ở đây có thể hiểu là `90`, `95`, `92` nếu Expected Price cùng thang đo; khi
thử dữ liệu thực tế nên dùng `90_000`, `95_000`, `92_000` cho dễ đọc.

```text
Đạt: Best Price=95; Offer 92 bị từ chối.
Không đạt: kiểm tra current_best và super().create().
```

## Bước 11 – Thêm workflow

### Thứ tự thêm

1. Bảo đảm Property đã có `state`, `buyer_id`, `selling_price`.
2. Bảo đảm Offer đã có `status`.
3. Thêm `action_accept()` và `action_refuse()` vào Offer.
4. Thêm `action_sold()` và `action_cancel()` vào Property.
5. Thêm buttons `type="object"` sau khi method Python tồn tại.
6. Thêm statusbar trên Property Form.
7. Restart + upgrade.

Button không chứa business logic; nó chỉ gửi tên method tới server. Vì thế phải
viết method trước, view button sau.

```text
Đạt: New → Offer Received → Offer Accepted → Sold.
Không đạt: xem method nào ghi state và button type có đúng không.
```

## Bước 12 – Thêm constraints và thử rollback

### Việc cần làm

1. Thêm SQL constraints giá dương vào Property và Offer.
2. Thêm `_check_selling_price()` với `@api.constrains` vào Property.
3. Thêm imports `ValidationError`, `_`, `float_compare`.
4. Restart + upgrade.
5. Tạo Property Expected Price `100000`.
6. Tạo Offer `85000`, rồi bấm Accept.

Offer được phép tồn tại; thao tác Accept mới phải thất bại vì `85000 < 90000`.

```text
Đạt: Validation Error; Buyer trống, Selling Price=0, Offer chưa accepted.
Không đạt: kiểm tra decorator chứa cả selling_price và expected_price.
```

## Bước 13 – Hoàn thiện Search/Kanban/User inheritance

Đến lúc này mọi model/field cần thiết đã tồn tại. Bạn mới nên thay Property view
tối thiểu bằng **toàn bộ code Phần 15**, rồi:

1. Tạo `res_users.py` theo Phần 9 và import nó.
2. Tạo `res_users_views.xml` theo Phần 16.
3. Hoàn thiện Offer view/action theo Phần 12.
4. Hoàn thiện Type model (`offer_ids`, `offer_count`) và Type view/stat button
   theo Phần 5 và Phần 13.
5. Tag view đã có thể giữ nguyên từ Bước 8.
6. Kiểm tra manifest theo Phần 18; Offer view phải đứng trước Type view vì stat
   button của Type tham chiếu Offer action.
7. Restart + upgrade.

```text
Đạt: menu mở List có Available; đổi Kanban; User thấy properties phụ trách.
Không đạt: xem file nào vừa thêm cuối cùng, đọc lỗi view validation đầu tiên.
```

## Bước 14 – Viết và chạy Estate tests

Không tiếp tục Accounting nếu test Estate chưa xanh.

```text
Đạt: 4 test methods, 0 failed, 0 errors.
```

## Bước 15 – Tạo estate_account

Tạo link module, override Sold, cài module và thử một Property đã Accept Offer.

```text
Đạt: Sold tạo đúng một Draft Customer Invoice có hai lines.
Không đạt: kiểm tra depends, import, MRO, quyền account.move và log transaction.
```

## Bước 16 – Chạy toàn bộ tests

```text
Đạt cuối: 5 test methods, 0 failed, 0 errors.
```

Khi đạt cả 16 bước, bạn không chỉ có code chạy; bạn đã tự xác nhận từng lớp từ
module discovery đến kế toán.

---

# 31. Tóm tắt kiến trúc bằng một sơ đồ

```text
Browser
  │
  │ menu/action/view + JSON-RPC
  ▼
estate.property
  ├── Many2one → estate.property.type
  ├── Many2many → estate.property.tag
  ├── One2many → estate.property.offer
  ├── Many2one → res.users (Salesperson)
  └── Many2one → res.partner (Buyer)
                  ▲
                  │ accepted offer.partner_id
estate.property.offer
  │
  │ action_accept
  ▼
estate.property.selling_price/state/buyer_id
  │
  │ action_sold; override bởi estate_account
  ▼
account.move + account.move.line
  │
  ▼
PostgreSQL transaction
```

Trình tự tư duy khi đọc một tính năng Odoo:

```text
Model nào sở hữu dữ liệu?
→ Field và relation nào tham gia?
→ ACL/record rule cho ai?
→ View hiển thị field ra sao?
→ Action mở model nào?
→ Menu gọi action nào?
→ Button gọi method nào?
→ ORM create/write chạy constraint nào?
→ Transaction commit hay rollback?
```

Nếu bạn trả lời được chuỗi trên cho Estate, bạn đã nắm được nền tảng quan trọng
nhất để tự viết một business module Odoo khác.
