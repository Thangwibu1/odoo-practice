# Chapter 15 - The Final Word

Trạng thái: **HOÀN THÀNH**.

Code đã được tách theo model/view, tên class/model/XML ID nhất quán, import order
rõ ràng, manifest theo version Odoo 19, method compute/action/constraint theo quy
ước. Security không dùng `sudo()`. `estate_account` giữ dependency một chiều để
`estate` độc lập. Có transaction tests cho business rules cốt lõi.

Checklist review: module structure, manifest/data order, Python/XML parse, Odoo
registry upgrade, ACL, fields/external IDs, constraints, actions, inheritance,
kanban và invoice integration.

Runbot là CI của Odoo, kiểm tra commit/branch/PR và dựng instance với demo data.
Project local này **không được chạy trên Runbot**; kết quả chỉ phản ánh database
`f_soft_test` và test runner local.

Tự kiểm tra: coding guideline giúp inheritance/teamwork thế nào? Test transaction
khác thử tay UI ra sao? Bài tập: chạy linter rồi sửa từng warning không liên quan
đến code core/venv.
