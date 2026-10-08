# Chapter 8 - Computed Fields And Onchanges

Trạng thái: **HOÀN THÀNH, ĐÃ UPGRADE**.

`total_area` phụ thuộc living/garden area; `best_price` phụ thuộc offer prices;
offer deadline bằng creation date + validity và có inverse. Onchange garden đặt
10 m²/North hoặc xóa giá trị.

`@api.depends` quản lý recompute/cache. Compute phải gán cho từng record. Chỉ
store khi cần search/group hoặc hiệu năng phù hợp. Onchange chỉ trợ giúp form,
không chạy chắc chắn qua import/RPC, nên business rule không được phụ thuộc nó.
Nó giống phản ứng UI hơn `useEffect`, nhưng chạy trên pseudo-record server-side.

Test bao phủ area, best offer, deadline. Lỗi thường gặp: thiếu dependency, không
loop recordset, inverse quên fallback `create_date`. Bài tập: tính phần trăm vườn.
