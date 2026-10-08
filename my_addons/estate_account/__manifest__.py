{
    # Đây là link module: nối hai module độc lập mà không làm estate phụ thuộc account.
    "name": "Real Estate Accounting",
    "version": "19.0.1.0.0",
    "summary": "Create customer invoices when real estate properties are sold",
    "author": "Minh Lam",
    "license": "LGPL-3",
    "category": "Sales/Real Estate",
    # Dependency bảo đảm cả estate.property và account.move đã có trong registry
    # trước khi extension Python của module này được load.
    "depends": ["estate", "account"],
    "data": [],
    "installable": True,
    "application": False,
}
