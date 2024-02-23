from pymongo import MongoClient
from rapidfuzz import process, fuzz
import random
from urllib.parse import quote
import re

client = MongoClient('mongodb+srv://abbozzo:abzo123abzo@serverlessinstance0.3swxn28.mongodb.net/?retryWrites=true&w=majority')
db = client["abbozzo_v4"]
art_collection = db.art_data

cloudfront_domain = "d3edkvggxkcni7.cloudfront.net/abbozz-gallery-images"  # Replace with your CloudFront domain name


def art_url(art, artist):
    print(art, artist)
    global cloudfront_domain
    safe_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/-+"
    art = re.sub(r'(\d)/(\d)', r'\1_\2', art)
    artist = re.sub(r'(\d) (\d)', r'\1_\2', artist)
    art = art.replace(" / ", " _ ").replace("A/P", "A_P").replace(":", "").replace("/", ":").replace(" ", "+")
    artist = artist.replace(":", "").replace("/", ":").replace(" ", "+")

    encoded_url_art = quote(f"{artist}/{art}.png", safe=safe_list)
    cloudfront_domain = "d3edkvggxkcni7.cloudfront.net/abbozz-gallery-images"  # Replace with your CloudFront domain name

    cloudfront_url = f"https://{cloudfront_domain}/{encoded_url_art}"
    print(cloudfront_url)
    return cloudfront_url

def find_best_match(full_names, misspelled_part, threshold=73.0):
    # Split each full name into first and last names
    split_names = [name.split() for name in full_names]

    # Flatten the list to include all first and last names separately
    all_name_parts = [name_part for name in split_names for name_part in name]

    # Find the best match for the misspelled part
    best_match, score, _ = process.extractOne(misspelled_part, all_name_parts, scorer=fuzz.WRatio)

    # Check if the score meets the threshold
    if score >= threshold:
        # Find and return the full name corresponding to the matched part
        for full_name in full_names:
            if best_match in full_name.split():
                return full_name
    return None  # Return None if no name meets the threshold

def art_recommendation(art_info):
    try:
        print(art_info)
        def find_arts(query, sort_order=None):
            return list(art_collection.find(query, sort=sort_order))

        def create_response(art):
            if art:
                img_url = art_url(art['art_name'], art['artist_name'])
                return [{"Art_Name": art['art_name'],"Artist_Name": art['artist_name'], "Art_Description": art['art_description']+"Do you like to know about more arts?", "Prompt_Question": "Do you like to know about more arts?"}, img_url]
            return [{"Message": "Sorry, the requested art was unavailable. Can you provide more details for a better recommendation?", "Question": "What other criteria would you like to use for your art recommendation?"}, None]

        def get_closest_art(query, price_start, price_end):
            arts = find_arts(query)
            if arts:
                # Sort arts by proximity to the price range
                arts.sort(key=lambda x: min(abs(x['price1'] - price_start), abs(x['price1'] - price_end)))
                return arts[0]
            # return None

        # Default pipeline for no criteria
        if len(art_info) == 0:
            # return create_response(random.choice(find_arts({'price1': {'$ne': 'Not available'}})))
            return [{"command": "Art Clarify"}, None]

        query = {}
        art_type, art_length_size, art_breadth_size = art_info.get('art_type'), art_info.get('art_length_size'), art_info.get('art_breadth_size')
        art_price_start, art_price_end, art_price_search_type = art_info.get('art_price_range_start'), art_info.get('art_price_range_end'), art_info.get('art_price_search_type')

        # Build query based on provided criteria
        if art_type:
            query['art_type'] = {'$regex': art_type, '$options': 'i'}

        if art_length_size:
            query['dim_inch_length'] = art_length_size

        if art_breadth_size:
            query['dim_inch_breadth'] = art_breadth_size

        price_query = {}
        if art_price_start or art_price_end:
            if art_price_search_type == 'between':
                price_query = {'$gte': art_price_start, '$lte': art_price_end}
            elif art_price_search_type == 'above':
                price_query = {'$gt': art_price_start}
            elif art_price_search_type == 'below':
                price_query = {'$lt': art_price_end}
            else:
                price_query = {'$eq': art_price_end}
        if price_query:
            query['price1'] = price_query

        # Initial search with all criteria
        arts = find_arts(query)
        if not arts:
            # Fallback: Try without size criteria
            query.pop('dim_inch_length', None)
            query.pop('dim_inch_breadth', None)
            arts = find_arts(query)
            if not arts and art_type:
                # Further fallback: Try only with art type
                query = {'art_type': {'$regex': art_type, '$options': 'i'}}
                arts = find_arts(query)
                if not arts:
                    # Last fallback: Closest art in price range for given art type
                    closest_art = get_closest_art(query, art_price_start, art_price_end)
                    if closest_art:
                        return create_response(closest_art)

        return create_response(random.choice(arts) if arts else None)

    except StopIteration:
        return [{"Status": "No data found"}, None]



# Example: Random Artist Recommendation
def artist_recommendation(_= None):
    try:
        pipeline = [
            {'$match': {'price1': {'$ne': 'Not available'}}},  # Exclude documents where price1 is 'Not available'
            {'$sample': {'size': 1}}  # Randomly sample one document
        ]

        art = art_collection.aggregate(pipeline).next()
        img_url = art_url(art['art_name'], art['artist_name'])
        return [{"Art_Name": art['art_name'],"Artist_Name": art['artist_name'], "Art_Description": art['art_description'], "Question": "Do you like to know about more arts?"}, img_url]
    except StopIteration:
        return [{"Status": "No data found"}, None]

# More functions need to be adapted similarly...
def art_description(art_name):
    try:
        art_name = art_name['art_name']
        art = art_collection.find_one({'art_name': {'$regex': art_name, '$options': 'i'}})
        if art:
            img_url = art_url(art['art_name'], art['artist_name'])
            return [{"Art_Name": art['art_name'],"Artist_Name":art['artist_name'], "Art_Description": art['art_description'], "Question": "Do you like to know about more arts?"}, img_url]
        else:
            art_names = [a['art_name'] for a in art_collection.find({}, {'art_name': 1})]
            matched_name = find_best_match(art_names, art_name.upper())
            if matched_name:
                art = art_collection.find_one({'art_name': matched_name})
                img_url = art_url(art['art_name'],art['artist_name'])
                return [{"Art_Name": art['art_name'], "Artist_Name": art['artist_name'], "Art_Description": art['art_description'], "Question": "Do you like to know about more arts?"}, img_url]
            return [{"Status": "Art not found"}, None]
    except Exception as e:
        return [{"Status": "Error: " + str(e)}, None]

def art_characteristics(art_name):
    try:
        art_name = art_name['art_name']
        art = art_collection.find_one({'art_name': {'$regex': art_name, '$options': 'i'}})
        if art:
            img_url = art_url(art['art_name'], art['artist_name'])
            return [{"Art_Name": art['art_name'], "Artist_Name": art['artist_name'], "Art_type": art.get('art_type', 'N/A'), "Art_Dimension": art.get('dimension1', 'N/A'),"Question":"Do you like to know about more arts?"}, img_url]
        else:
            # Fuzzy matching part
            art_names = [a['art_name'] for a in art_collection.find({}, {'art_name': 1})]
            matched_name = find_best_match(art_names, art_name.upper())
            if matched_name:
                art = art_collection.find_one({'art_name': matched_name})
                img_url = art_url(art['art_name'], art['artist_name'])
                return [{"Art_Name": art['art_name'], "Artist_Name": art['artist_name'],"Art_type": art.get('art_type', 'N/A'), "Art_Dimension": art.get('dimension1', 'N/A'),"Question": "Do you like to know about more arts?"}, img_url]
            return [{"Status": "Art not found"}, None]
    except Exception as e:
        return [{"Status": "Error: " + str(e)}, None]


def art_artist_name(art_name):
    try:
        art_name = art_name['art_name']
        art = art_collection.find_one({'art_name': {'$regex': art_name, '$options': 'i'}})
        if art:
            img_url = art_url(art['art_name'], art['artist_name'])
            return [{"Art_Name": art['art_name'], "Artist_Name": art.get('artist_name', 'Unknown'), "Art_Description": art['art_description'], "Question":"Do you like to know about more arts?"}, img_url]
        else:
            art_names = [a['art_name'] for a in art_collection.find({}, {'art_name': 1})]
            matched_name = find_best_match(art_names, art_name.upper())
            if matched_name:
                art = art_collection.find_one({'art_name': matched_name})
                img_url = art_url(art['art_name'], art['artist_name'])
                return [{"Art_Name": art['art_name'], "Artist_Name": art.get('artist_name', 'Unknown'), "Art_Description": art['art_description'], "Question": "Do you like to know about more arts?"},img_url]
            return [{"Status": "Artist name not found"}, None]
    except Exception as e:
        return [{"Status": "Error: " + str(e)}, None]

def art_price(art_name):
    try:
        art_name = art_name['art_name']
        art = art_collection.find_one({'art_name': {'$regex': art_name, '$options': 'i'}})
        if art:
            img_url = art_url(art['art_name'], art['artist_name'])
            return [{"Art_Name": art['art_name'], "Artist_Name": art['artist_name'], "Art_price": art.get('price1', 'N/A'), "Question":"Do you like to know about more arts?"}, img_url]
        else:
            art_names = [a['art_name'] for a in art_collection.find({}, {'art_name': 1})]
            matched_name = find_best_match(art_names, art_name.upper())
            if matched_name:
                art = art_collection.find_one({'art_name': matched_name})
                img_url = art_url(art['art_name'], art['artist_name'])
                return [{"Art_Name": art['art_name'],"Artist_Name": art['artist_name'], "Art_price": art.get('price1', 'N/A'),"Question": "Do you like to know about more arts?"}, img_url]
            return [{"Status": "Art not available in Abbozzo Gallery"}, None]
    except Exception as e:
        return [{"Status": "Error: " + str(e)}, None]


def artist_art_suggestion(artist_name):
    try:
        artist_name = artist_name['artist_name']
        pipeline = [
            {'$match': {
                'artist_name': {'$regex': artist_name, '$options': 'i'},
                # Match artist name with case-insensitive regex
                'price1': {'$ne': 'Not available'}  # Exclude documents where price1 is 'Not available'
            }},
            {'$sample': {'size': 1}}  # Randomly sample one document
        ]

        arts = art_collection.aggregate(pipeline)
        art = next(arts, None)
        if art:
            img_url = art_url(art['art_name'], art['artist_name'])
            return [{"Artist_Name": art['artist_name'], "Art_Name": art['art_name'], "Art_Description": art["art_description"], "Question":"Do you like to know about more arts?"}, img_url]
        else:
            artist_names = [a['artist_name'] for a in art_collection.find({}, {'artist_name': 1})]
            matched_name = find_best_match(artist_names, artist_name.upper())
            if matched_name:
                pipeline = [
                    {'$match': {'artist_name': {'$regex': matched_name, '$options': 'i'}}},
                    {'$sample': {'size': 1}}
                ]

                arts = art_collection.aggregate(pipeline)
                art = next(arts, None)
                img_url = art_url(art['art_name'], art['artist_name'])
                return [{"Artist_Name": art['artist_name'], "Art_Name": art['art_name'],"Art_Description": art["art_description"], "Question":"Do you like to know about more arts?"}, img_url]

            return [{"Status": "Arts of the Artist not found in Abbozzo Gallery"}, None]
    except Exception as e:
        return [{"Status": "Error: " + str(e)}, None]

