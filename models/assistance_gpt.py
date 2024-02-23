from openai import OpenAI
from db_reader import store_reader as sr
import json
from pymongo import MongoClient
import sys
import path

dir = path.Path(__file__).abspath()
sys.path.append(dir.parent.parent)
api_key = "API-KEY"

model = "gpt-4-turbo-preview"
llm_client = OpenAI(
    api_key=api_key,
)

def getSystemText(jsonFile):
    with open(jsonFile) as f: data = json.load(f)
    return data

file_path = "system_json/store.json"

offers = {
    0: "Enjoy 10% off on dairy products! Visit the Food & Beverages Sections for this limited offer.",
    1: "Get 5% off men's clothing in our Fashion and Health & Beauty Sections. Don't miss out!",
    2: "Score 20% off TVs and printers. Check out the Electronics and Computer Section for this exciting deal."
}

def get_customer_service_assistance(_):
    return [{"content": "I have called a staff for help. Someone will be here to help you shortly. Meanwhile can I help you with anything?"},None]

system_message = getSystemText(file_path)
product_category = ['Alcoholic Beverages', 'Baby Gear', 'Beauty Personal Care & Hygiene', 'Bedding', 'Canned Food', 'Cell Phones', 'Cleaning Supplies', 'Clothing', 'Computer Components', 'Computers', 'Condiments & Sauces', 'Craft Supplies', 'DIY and Tools', 'Electronic Accessories', 'Electronics Cables', 'Food & Beverages', 'Footwear', 'Furniture', 'Garden & Patio', 'Grills & Outdoor Cooking', 'Grocery', 'Hardware Tools & Building Marterials', 'Health & Beauty Electronics', 'Health and Wellness', 'Home Decor Kitchen & Other', 'Large Appliances', 'Medical Aids & Equipment', 'Medicine & Supplements', 'Musical Instruments', 'Occasion & Seasonal', 'Office Supplies', 'Optical', 'Outdoor Living', 'Party Supplies', 'Personal Care', 'Pet Supplies', 'Printers Scanners & Imaging', 'Sports & Outdoors', 'TVs & Video Displays', 'Video Projectors']
product_list = ['2-in-1 laptops', '3D printers', '4K Ultra HD TVs', '4K projectors', 'Activewear', 'Air conditioners', 'Air fresheners and deodorizers', 'All-in-one computers', 'All-in-one printers', 'Allergy relief', 'Amplifiers and pedals', 'Aquariums and fish supplies', 'Audio cables', 'Baby bath products', 'Baby clothing', 'Baby monitors', 'Balloons and helium tanks', 'Banners and decorations', 'Basic cell phones', 'Basketball', 'Beads and jewelry-making kits', 'Beds', 'Beer', 'Belt', 'Beverages (coffee tea soda)', 'Beverages (juices sodas)', 'Bicycles', 'Bird cages and feed', 'Birthday party supplies', 'Blood glucose monitors', 'Blood pressure monitors', 'Bluetooth headsets', 'Body wash and soaps', 'Body washes and soaps', 'Bookshelves', 'Boots', 'Bread and bakery items', 'Business projectors', 'Calculators', 'Campbell Soup', 'Camping chairs', 'Candles and cake decorations', 'Candles and diffusers', 'Canned and jarred goods', 'Canned foods', 'Car mounts', 'Car seats', 'Cases', 'Champagne', 'Charcoal grills', 'Charging cables', "Children's shoes", 'Christmas decorations (ornaments lights)', 'Chromebooks', 'Clay and sculpting tools', 'Coaxial cables', 'Cocktail mixers', 'Coffee tables', 'Cold and flu medications', 'Compression garments', 'Condiments and spices', 'Contact lens cases', 'Contact lenses', 'Cooling fans', 'Costume accessories', 'Craft beers', 'Craft paper and scissors', 'Cribs and bedding', 'Curved TVs', 'Dairy products (milk cheese yogurt)', 'Dairy products (milk cheese)', 'Decorative garden stakes', 'Deodorants and antiperspirants', 'Desk lamps', 'Desks', 'Desktops', 'Diapers and wipes', 'Digestive health products', 'Digital signage displays', 'Dining tables', 'Dishwashers', 'Dishwashing liquids and detergents', 'Disinfectant wipes and sprays', 'DisplayPort cables', 'Disposable plates cups and utensils', 'Document scanners', 'Dog and cat food', 'Dressers', 'Dresses', 'Drills', 'Drums and percussion instruments', 'Dry goods (rice pasta)', 'Dryers', 'Earphones', 'Easter baskets and decor', 'Electric toothbrushes', 'Electrical supplies (wiring switches)', 'Electronic music equipment (synthesizers  DJ gear)', 'Envelopes and mailing supplies', 'Essential oils and diffusers', 'Ethernet cables', 'External hard drives', 'Eyeglass cases', 'Eyeglass frames', 'Eyeglass repair kits', 'Fabric and sewing supplies', 'Facial cleansers and scrubs', 'Facial cleansing brushes', 'Feeding bottles and accessories', 'Feminine hygiene products', 'Fiber optic cables', 'File folders and organizers', 'Fire Pits', 'Fire pits', 'Fireworks and sparklers', 'First aid kits', 'Fishing rods', 'Fitness equipment (yoga mats weights)', 'Fitness trackers', 'Flashlights', 'Flats', 'Flea and tick treatments', 'Floor cleaning solutions', 'Freezers', 'Fresh fruits and vegetables', 'Fresh produce (fruits and vegetables)', 'Frozen foods', 'Gaming PCs', 'Gaming monitors', 'Garden Decorations', 'Garden tools (spades rakes)', 'Gas grills', 'Glass and window cleaners', 'Glue and adhesives', 'Graphics cards', 'Grill cleaning tools', 'Grill covers', 'Grilling Accessories', 'Grilling tools and accessories', 'Grills', 'Grooming tools', 'Guitars (acoustic electric)', 'HDMI cables', 'Hair dryers', 'Hair styling products', 'Hair styling products (gel mousse)', 'Halloween costumes and decorations', 'Hammer', 'Hammocks', 'Hand tools (hammers screwdrivers)', 'Hard drives', 'Hard seltzers', 'Hardware (screws nails bolts)', 'Hats', 'Health monitors (blood pressure glucose)', 'Hearing aids', 'Heels', 'Herbal supplements', 'Herbal teas and natural remedies', 'High chairs', 'Highlighters and markers', 'Hiking backpacks', 'Home theater projectors', 'Imported beers', 'Inkjet printers', 'Instrument cases and bags', 'Interactive projectors', 'Invitations and thank-you cards', 'Jackets', 'Japanese mayonnaise', 'Jeans', 'Keyboard covers', 'Kitchen gadgets and utensils', 'LED TVs', 'Ladders', 'Lamps and lighting fixtures', 'Laptop bags', 'Laptops', 'Laser printers', 'Laser projectors', 'Laundry detergents and fabric softeners', 'Lawn mowers', 'Leashes and collars', 'Lens cleaning solutions', 'Light therapy devices', 'Liqueurs', 'Litter and litter boxes', 'Loafers', 'MacBooks', 'Magnifying glasses', 'Makeup (lipstick foundation mascara)', 'Makeup and cosmetic items', 'Massage devices', 'Meat and poultry', 'Meat and seafood', 'Meditation and mindfulness aids', 'Memory cards', 'Mental health books and journals', 'Microwaves', 'Mini PCs', 'Mini projectors', 'Mobility aids (walkers canes)', 'Moisturizers and lotions', 'Motherboards', 'Mousepads', 'Multipurpose cleaners', 'Music stands and accessories', 'Nails and screws', 'Nebulizers', "New Year's party supplies", 'Nightstands', 'Non-alcoholic versions', 'Notebooks and notepads', 'OLED TVs', 'Office chairs', 'Orthopedic supports', 'Outdoor Lighting', 'Outdoor Rugs', 'Outdoor TVs', 'Outdoor Umbrellas', 'Outdoor furniture sets', 'Outdoor heaters', 'Outdoor kitchens', 'Outdoor lighting', 'Outdoor projectors', 'Ovens and ranges', 'Overhead projectors', 'Pain relievers', 'Paints and brushes', 'Paints and canvases', 'Paper towels and cleaning cloths', 'Party favors and goody bags', 'Party games and activities', 'Patio Furniture Sets', 'Patio umbrellas', 'Pens and pencils', 'Pest Control', 'Pet beds and furniture', 'Pet clothing and accessories', 'Phone cases', 'Photo paper', 'Photo printers', 'Pianos and keyboards', 'Pill organizers', 'Pinatas', 'Planters', 'Planters and pots', 'Plumbing supplies (pipes faucets)', 'Portable grills', 'Portable projectors', 'Portable scanners', 'Portable speakers', 'Pots pans and cookware sets', 'Power banks', 'Power cables', 'Power drills and drill bits', 'Power supplies', 'Prescription eyeglasses', 'Prescription refill services', 'Printer ink cartridges', 'Printer paper', 'Probiotics', 'Processors (CPUs)', 'Protein powders and nutrition bars', 'RAM (Memory)', 'Range hoods', 'Razors and shaving creams', 'Reading glasses', 'Refrigerators', 'Rugs and mats', 'Running shoes', 'SIM cards', 'SSDs (Solid State Drives)', 'Safety gear (gloves goggles)', 'Sandals', 'Sandpaper and abrasives', 'Saws', 'Scarves', 'Scrapbooking materials', 'Screen protectors', 'Screwdrivers', 'Seafood', 'Seasonal wreaths and door decor', 'Shampoos and conditioners', 'Shavers and razors', 'Shaving creams and razors', 'Short throw projectors', 'Skin care devices', 'Skin care products (moisturizers cleansers)', 'Skin care treatments', 'Skincare and anti-aging products', 'Sleep aids', 'Sleep aids and relaxation products', 'Slippers', 'Smart TVs', 'Smartphones', 'Smokers', 'Snacks and chips', 'Snacks and confectionery', 'Sneakers', 'Soccer balls', 'Socks', 'Sofas', 'Sound cards', 'Spirits (vodka rum whiskey)', 'Sponges and scrubbing brushes', 'Stamps and ink pads', 'Staplers and staples', 'Stickers and embellishments', 'Storage containers and organizers', 'Straighteners and curling irons', 'Strollers', 'Sunglasses', 'Sunscreen and insect repellent', 'Sweaters', 'T-shirts', 'TENS units (Transcutaneous Electrical Nerve Stimulation)', 'TV stands', 'TV wall mounts', 'Tablecloths and napkins', 'Tablet stands', 'Tablets', 'Tableware (plates bowls glasses)', 'Tape measures', 'Teething toys', 'Tents', 'Thanksgiving tableware and decor', 'Throw pillows and blankets', 'Thunderbolt cables', 'Toner cartridges', 'Toolboxes', 'Toothpaste and dental care products', 'Toothpaste and mouthwash', 'Toys for pets', 'Trash bags and liners', 'USB cables', 'USB hubs', 'Ukuleles', 'VGA cables', 'VR headsets', "Valentine's Day gifts and cards", 'Vases and decorative bowls', 'Violins and string instruments', 'Vitamins and dietary supplements', 'Vitamins and supplements', 'Wall art and picture frames', 'Washing machines', 'Water bottles', 'Water heaters', 'Watering and irrigation supplies', 'Webcam covers', 'Wedding decorations and favors', 'Wheelchairs', 'Whiteboards and markers', 'Wind instruments (flute clarinet saxophone)', 'Wine', 'Wood chips for smoking', 'Woodworking tools', 'Work boots', 'Workstations', 'Wrenches', 'Yarn and knitting needles', 'Yoga mats']

mgdb_client = MongoClient('mongodb+srv://abbozzo:abzo123abzo@serverlessinstance0.3swxn28.mongodb.net/?retryWrites=true&w=majority')
db = mgdb_client["store_product_demo"]
collection = db.product_list_v6
product_category = collection.distinct('Category')
product_list = collection.distinct('Product')

user_convo_count = 0
offers_count = len(offers)
def predict(input, session_id):
    global message_history, system_message, user_convo_count, offers_count
    message_history = system_message
    message_history.append({'role': 'user', 'content': input})
    user_convo_count +=1
    print("The value of user_convo_count",user_convo_count)
    functions = [
    {
        "name": "get_product_category",
        "description": "Determines the category of a product based on customer inquiries about product location or availability in the store. This function helps in navigating the customer to the correct category aisle or confirming product availability.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_category": {
                    "type": "string",
                    "enum": product_category,
                    "description": "Specifies the category for the queried product. For example, for the query 'Where can I find diapers?', the function should return 'Baby Products' as the category. Use 'Others' for products not fitting any predefined category."
                },
                "product_name": {
                    "type": "string",
                    "enum": product_list,
                    "description": "Identifies the specific product the customer is inquiring about. For example, in response to 'Where can I find diapers?', the function should return the product name 'Diapers'. Use 'Others' for unnamed or unlisted products."
                }
            },
            "required": ["product_category", "product_name"]
        }
    },
    {
        "name": "get_customer_service_assistance",
        "description": "Facilitates a direct connection to customer service assistance for personalized help. This function should be invoked when the customer requests human assistance, ask for a human to talk to or calls for a human support or needs support",
        "parameters": {
            "type": "object",
            "properties": {},
            "description": "This function does not require any parameters. It initiates a request for customer service assistance, potentially using customer context or previous interactions to route the request appropriately."
        }
    }
]

    response = llm_client.chat.completions.create(
        model=model,
        max_tokens = 128,
        user = session_id,
        messages=message_history,
        functions=functions,
        function_call="auto",
    )
    # print(response)
    # print(response.choices[0].message)
    response_message = response.choices[0].message
    # print(response_message)
    if response_message.function_call:
        available_functions = {
            "get_product_category": sr.get_product_location,
            "get_customer_service_assistance": get_customer_service_assistance,
        }
        function_name = response_message.function_call.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message.function_call.arguments)
        function_response = function_to_call(function_args)

        print("Function response: ", function_response)

        if function_response[0] is not None:
            print(function_response)
            print(function_response[0])
            img_url = function_response[1]
            message_history.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": str(function_response[0])
                }
            )
            second_response = llm_client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                max_tokens=256,
                user = session_id,
                messages=message_history),
            answer = second_response[0].choices[0].message.content.split("\n")[0]
            if user_convo_count <= offers_count*2:
                msg_hist = [{"role": "system","content": " You are Athena at who takes input the response and answers it in a different way by rephrasing the response and  improving the grammar of the response"}]
                msg_hist.append({"role": "assistant", "content": answer+ offers[user_convo_count%offers_count]})
                second_response = llm_client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    max_tokens=256,
                    messages=msg_hist),
                answer = second_response[0].choices[0].message.content.split("\n")[0]
                print(answer)
                message_history.append({"role": "assistant", "content": answer})
            message_history.append({'role': 'assistant', 'content': answer})
            return {"answer": answer, "img_url": img_url}


        else:

            second_response = llm_client.chat.completions.create(
                model=model,
                max_tokens=256,
                user = session_id,
                messages=message_history,
            )
            answer = second_response[0].choices[0].message.content.split("\n")[0]
            message_history.append({'role': 'assistant', 'content': answer})
            return {"answer": answer}

    else:

        answer = response.choices[0].message.content.split("\n")[0]
        message_history.append({'role': 'assistant', 'content': answer})
        return {"answer": answer}


if __name__ == '__main__':
    while True:
        line = input()
        print(predict(line, "asddfs3423"))
