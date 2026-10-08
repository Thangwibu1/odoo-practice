# Chapter 14 - A Brief History Of QWeb

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

Kanban view có `<templates><t t-name="card">`, hiển thị name, expected price,
best price, selling price và tags. `t-if` dựa `record.state.raw_value`: best offer
chỉ hiện khi đã có offer; selling price khi accepted/sold. `default_group_by` là
property type và `records_draggable="false"` ngăn kéo record giữa group.

`record.field.value` là giá trị đã format cho user; `raw_value` phù hợp điều kiện
logic. `<field>` khai báo dữ liệu cần đọc và render widget. QWeb giống JSX ở
template động/component tree, nhưng directive là XML và được engine Odoo xử lý,
không phải JavaScript expression/component React tùy ý.

Kanban đã được Odoo validate/load. Lỗi phổ biến: dùng field trong QWeb nhưng
không khai báo, so sánh formatted value, sai `t-name="card"`.

Tự kiểm tra: value khác raw_value? Bài tập: thêm postcode có điều kiện.
