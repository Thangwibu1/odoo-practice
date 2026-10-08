# Chapter 11 - Add The Sprinkles

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

UI đã có inline One2many lists, `statusbar`, `many2many_tags` với color picker,
handle sequence, optional availability, editable offer/tag lists, decorations,
conditional invisible/readonly, default Available filter và stat button Offers.
Models có ordering: property id desc, offer price desc, tag name, type sequence/name.

`property_type_id` trên offer là related stored; type có `offer_ids` và computed
`offer_count`. Stat button gọi action với domain theo `active_id`.

Widget/options/decorations chỉ điều khiển cách hiển thị/nhập. Chúng không thay
constraint, ACL hay method validation. Lỗi phổ biến: expression dùng field không
có trong view, readonly chỉ đặt ở UI, widget không hợp kiểu field.

Tự kiểm tra: tại sao statusbar không tự đổi state? Related stored có tradeoff gì?
Bài tập: thêm decoration cho property canceled.
