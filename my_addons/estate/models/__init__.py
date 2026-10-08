# Odoo chỉ đăng ký những file Python được import qua chuỗi __init__.py.
# Tách mỗi business object ra một file giúp inheritance và bảo trì dễ hơn.
from . import estate_property
from . import estate_property_offer
from . import estate_property_tag
from . import estate_property_type
from . import res_users
