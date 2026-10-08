# Chapter 9 - Ready For Some Action?

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

Button `type="object"` gọi method Python trên recordset: `action_sold`,
`action_cancel`, `action_accept`, `action_refuse`. Button `type="action"` gọi
window action bằng external ID, dùng ở stat button của property type.

Accept offer ghi buyer, selling price và state; chỉ một offer được accept. Sold
không áp dụng cho canceled hoặc property chưa có buyer; canceled không áp dụng
cho sold. `UserError` đưa thông báo nghiệp vụ có thể hiểu được và transaction
rollback nếu lỗi.

Khác `onClick()` React: click chỉ khởi phát RPC; quyết định hợp lệ nằm ở server.
UI invisible giúp UX nhưng method vẫn tự bảo vệ invariant.

Test chạy toàn flow offer → accepted → sold. Tự kiểm tra: vì sao method phải loop
`self`? `type=object` khác `type=action`? Bài tập: thêm action đưa canceled về new.
