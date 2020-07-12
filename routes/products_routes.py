from resources.product import ProductsApi, ProductApi, ProductSlotsApi, ProductSlotApi, ProductSessionsApi

def products_routes(api):
    api.add_resource(ProductsApi, '/api/products')
    api.add_resource(ProductApi, '/api/products/<id>')
    api.add_resource(ProductSlotsApi, '/api/products/<id>/slots')
    api.add_resource(ProductSessionsApi, '/api/products/<id>/sessions')
    api.add_resource(ProductSlotApi, '/api/products/<id>/slots/<slot_id>')
