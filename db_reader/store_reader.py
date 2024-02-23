from pymongo import MongoClient
from rapidfuzz import process, fuzz
from urllib.parse import quote
import requests

client = MongoClient('mongodb+srv://abbozzo:abzo123abzo@serverlessinstance0.3swxn28.mongodb.net/?retryWrites=true&w=majority')
db = client["store_product_demo"]
collection = db.product_list_v6

cloudfront_domain = "d3edkvggxkcni7.cloudfront.net/abbozz-gallery-images"  # Replace with your CloudFront domain name


def product_url(product, category):
    global cloudfront_domain, db, collection
    safe_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/-+"
    product_component = None
    category_component = None
   # product = collection.find_one({"product_column": product})
    if product is not None:
        product_component = product.replace(":", "").replace(" ", "+")
        product_component = quote(f"{product_component}.png", safe=safe_list)
        cloudfront_domain = "d3edkvggxkcni7.cloudfront.net/StoreDemo"  # Replace with your CloudFront domain name
        cloudfront_url = f"https://{cloudfront_domain}/{product_component}"
        res = requests.get(cloudfront_url)
        if res.status_code == 200:
            return cloudfront_url
    elif category is not None:
        category_component = category.replace(":", "").replace(" ", "+")
        cloudfront_domain = "d3edkvggxkcni7.cloudfront.net/StoreDemo"  # Replace with your CloudFront domain name
        category_component = quote(f"{category_component}.png", safe=safe_list)
        cloudfront_url = f"https://{cloudfront_domain}/{category_component}"
        return cloudfront_url
    return None

def get_product_location(product_info):
    global db, collection
    print(product_info)
    product_name, product_category = product_info.get("product_name"), product_info.get("product_category")
    if product_name:
        result = collection.find_one({"Product": product_name}, {"Ailse": 1, "Section Name": 1, "Section No": 1, "_id": 1,"Category":1})
        print("result",result)
    if result is None:
        product_name = None
        result = collection.find_one({"Category": product_category}, {"Ailse": 1, "Section Name": 1, "Section No": 1, "_id": 1,"Category":1})
    img_url = product_url(product_name, product_category)
    if result:
        return [{"Aisle": result['Ailse'], "Block Name": result['Section Name'], "Section Number": result['Section No'],"Product Category":result["Category"]}, img_url]
    else:
        return [{"error": "No matching document found for the given category."}, None]




