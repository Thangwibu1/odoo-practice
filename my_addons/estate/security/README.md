# Giải thích `ir.model.access.csv`

CSV này là data file đặc biệt của Odoo; không chèn comment trực tiếp vào CSV vì
comment có thể bị parser hiểu thành một access-control record không hợp lệ.

Mỗi dòng gồm:

- `id`: external ID duy nhất trong module;
- `name`: tên kỹ thuật của ACL;
- `model_id:id`: external ID `ir.model` do Odoo sinh từ `_name`;
- `group_id:id`: group nhận quyền, ở đây là Internal User hoặc Settings/System;
- `perm_read`, `perm_write`, `perm_create`, `perm_unlink`: `1` cho phép, `0` từ chối.

ACL kiểm tra quyền ở cấp model. Nó không lọc từng record; muốn giới hạn record
theo salesperson/company cần thêm `ir.rule`. Việc giấu menu hoặc field trên XML
không thay thế ACL/record rule vì user vẫn có thể gọi RPC trực tiếp.
