# Odoo 19 Cheatsheet

## Module và ORM

- `addons_path`: nơi server tìm addon; `depends`: thứ tự dependency module.
- `self`: recordset 0..n records, luôn loop hoặc `ensure_one()` khi cần singleton.
- `self.env`: cursor, user, company, context, registry/cache và truy cập model.
- `search(domain)`: query recordset; `browse(ids)`: dựng recordset theo ID, chưa
  bảo đảm record tồn tại; dùng `.exists()` nếu cần.
- `create(vals)` / `create(vals_list)`: INSERT; `write(vals)`: UPDATE recordset;
  `unlink()`: DELETE; tất cả đi qua security/business hooks/transaction.

```python
properties = self.env["estate.property"].search(
    [("state", "in", ["new", "offer_received"]), ("expected_price", ">", 0)]
)
property_record = self.env["estate.property"].browse(42).exists()
```

## Domain và context

Domain là điều kiện query: `[('field', 'operator', value)]`; `&`, `|`, `!` là
toán tử prefix. Context là dict metadata bất biến theo env, ví dụ default/filter,
language/company: `with_context(default_bedrooms=2)`.

## Relations và Commands

- Many2one: record A giữ foreign key tới B.
- One2many: mặt inverse, cần Many2one ở model con.
- Many2many: relation table.
- `Command.create(vals)`, `link(id)`, `unlink(id)`, `delete(id)`, `clear()`,
  `set(ids)` thay đổi x2many; ví dụ invoice lines dùng danh sách Command.create.

## Compute, onchange, constraint

```python
@api.depends("living_area", "garden_area")
def _compute_total_area(self):
    for record in self:
        record.total_area = record.living_area + record.garden_area
```

- `store=True` lưu computed field để search/group, đổi lại chi phí recompute.
- `@api.onchange`: trợ giúp form, không phải business invariant.
- `models.Constraint`: CHECK/UNIQUE ở PostgreSQL.
- `@api.constrains`: validation Python đa field; raise `ValidationError`.

## Inheritance, actions, views, QWeb

- `_inherit="res.users"`: mở rộng model; luôn cân nhắc `super()` khi override.
- View inheritance: `inherit_id` + XPath, không sửa core view.
- Window action chọn `res_model`, `view_mode`, domain/context.
- `type="object"` gọi method; `type="action"` gọi action external ID.
- XML view là metadata UI; list/form/search/kanban do web client render.
- QWeb: `t-name="card"`, `t-if`; `record.x.value` đã format,
  `record.x.raw_value` dùng logic.
