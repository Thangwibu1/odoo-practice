# Chapter 5 - Finally, Some UI To Play With

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

`estate_property_action` mở model bằng list/kanban/form. `estate_menus.xml` tạo
ba cấp menu và được load sau action. Property có selling price readonly/copy
false; availability sau ba tháng/copy false; bedrooms mặc định 2; `active=True`;
state required/copy false/default new.

Luồng: **Menu → Window Action → View → RPC/ORM → PostgreSQL**. Action gần route
config nhưng còn mang model, view modes, domain và context; không phải `onClick`.

Action/menu đã load. Lỗi phổ biến: menu load trước action, Date default sai kiểu,
nhầm readonly UI với security. Tự kiểm tra: `active=False` ảnh hưởng search thế
nào? `copy=False` chạy lúc nào? Bài tập: duplicate property và so field.
