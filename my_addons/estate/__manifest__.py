{
    # Metadata hiển thị trong Apps. Version theo dạng Odoo 19 + version addon.
    "name": "Real Estate",
    "version": "19.0.1.0.0",
    "summary": "Manage real estate properties and offers",
    "author": "Minh Lam",
    "license": "LGPL-3",
    "category": "Sales/Real Estate",
    # Chỉ phụ thuộc ``base`` để estate chạy độc lập với Accounting. Tích hợp kế
    # toán nằm ở link module ``estate_account``.
    "depends": ["base"],
    # Data files được load từ trên xuống. Action/view phải tồn tại trước khi menu
    # ở file cuối tham chiếu tới external ID của chúng.
    "data": [
        "security/ir.model.access.csv",
        "views/estate_property_offer_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_views.xml",
        "views/res_users_views.xml",
        "views/estate_menus.xml",
    ],
    "installable": True,
    "application": True,
}
