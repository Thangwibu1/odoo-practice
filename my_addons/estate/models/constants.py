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
