from resources.product import ProductsApi, ProductApi

def products_routes(api):
    api.add_resource(ProductsApi, '/api/products')
    api.add_resource(ProductApi, '/api/products/<id>')
