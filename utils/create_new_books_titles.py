CATEGORIES = [
    ('CK', 'Cooking'),
    ('CR', 'Crime'),
    ('MY', 'Mistery'),
    ('SF', 'Science Fiction'),
    ('FAN', 'Fantasy'),
    ('HIS', 'History'),
    ('ROM', 'Romance'),
    ('TXT', 'Textbook'),
]

AUTHORS = [
    "Alvaro Barragan Bernal",
    "Carlos Gutierrez Bernal",
    "Julius Gun",
    "Matt Ricote Kristiansen"
]

def generate_book_title(author_name, category_code):
    """
    Generates a stereotypical Norwegian/Viking themed book title based on author and category.
    """
    category_templates = {
        'CK': ["The {NorwegianFood} Cookbook", "{VikingActivity} Feasts", "Arctic Kitchen: {Ingredient} Recipes"],
        'CR': ["{City} Midnight Murders", "The {MythicalCreature} Conspiracy", "{VikingThing} Robbery"],
        'MY': ["Silence of the {NorwegianPlace}", "The {WeatherCondition} Enigma", "{NorseGod}'s Riddle"],
        'SF': ["Vikings in {SpacePlace}", "Arctic {SpaceObject} Odyssey", "The {FutureTech} Saga"],
        'FAN': ["Trolls of {MountainName}", "{MythicalPlace} Legends", "The {MagicalItem} Prophecy"],
        'HIS': ["{VikingLeader}'s Voyages", "{HistoricalEvent} of Norway", "Sagas of the {NorsePeople}"],
        'ROM': ["Love in the Time of {NaturalPhenomenon}", "{NorwegianCity} Romance", "Viking {Emotion} Stories"],
        'TXT': ["A {Adjective} Guide to {NorwegianThing}", "The {Essential} Handbook of {Activity}", "Living in {NorwegianPlace}: A Survival Manual"]
    }

    keywords = {
        'NorwegianFood': ["Lutefisk", "Brunost", "Fårikål", "Krumkake", "Smalahove"],
        'VikingActivity': ["Viking", "Norse", "Longship", "Raid", "Berserker"],
        'ArcticThing': ["Ice", "Snow", "Midnight Sun", "Northern Lights", "Polar Night"],
        'City': ["Oslo", "Bergen", "Trondheim", "Stavanger", "Tromsø"],
        'MythicalCreature': ["Troll", "Draugr", "Valkyrie", "Nisse", "Fenrir"],
        'VikingThing': ["Axe", "Shield", "Helmet", "Longboat", "Rune"],
        'NorwegianPlace': ["Fjords", "Mountains", "Arctic", "Wilderness", "Forests"],
        'WeatherCondition': ["Winter", "Ice", "Snow", "Darkness", "Storm"],
        'NorseGod': ["Odin", "Thor", "Freya", "Loki", "Heimdall"],
        'SpacePlace': ["Space", "Void", "Galaxy", "Nebula", "Cosmos"],
        'SpaceObject': ["Star", "Planet", "Comet", "Asteroid", "Black Hole"],
        'FutureTech': ["AI", "Robots", "Cybernetics", "Nanobots", "Virtual Reality"],
        'MountainName': ["Tromsdalstind", "Gaustatoppen", "Rondane", "Jotunheimen", "Hardangervidda"],
        'MythicalPlace': ["Valhalla", "Asgard", "Midgard", "Niflheim", "Helheim"],
        'MagicalItem': ["Mjollnir", "Gungnir", "Draupnir", "Skíðblaðnir", "Gleipnir"],
        'VikingLeader': ["Ragnar Lothbrok", "Erik the Red", "Harald Fairhair", "Leif Erikson", "Olaf Tryggvason"],
        'HistoricalEvent': ["Viking Age", "Kalmar Union", "Black Death", "Union with Sweden", "WWII Occupation"],
        'NorsePeople': ["Vikings", "Norsemen", "Norwegians", "Scandinavians", "Nordics"],
        'NaturalPhenomenon': ["Midnight Sun", "Northern Lights", "Polar Night", "Winter Solstice", "Summer Solstice"],
        'NorwegianCity': ["Tromsø", "Bergen", "Oslo", "Stavanger", "Trondheim"],
        'Emotion': ["Hearts", "Dreams", "Sagas", "Tales", "Whispers"],
        'Adjective': ["Cozy", "Hygge", "Essential", "Ultimate", "Complete"],
        'NorwegianThing': ["Hygge", "Janteloven", "Winter", "Fjords", "Hiking"],
        'Essential': ["Essential", "Basic", "Fundamental", "Indispensable", "Crucial"],
        'Activity': ["Hiking", "Programming", "Cooking", "Surviving", "Socializing"],
    }

    import random

    template = random.choice(category_templates.get(category_code, ["A Generic Book Title"])) # Fallback title
    title = template.format(**{k: random.choice(v) for k, v in keywords.items() if '{' + k + '}' in template})

    # Add author-specific touch (optional and very basic for now)
    if "Barragan" in author_name:
        if category_code == 'ROM':
            title = "Spanish Hearts in the Norse Fjords: A " + title
        elif category_code == 'TXT':
            title = "Conquering " + title + ": A Barragan's Method"
    elif "Gutierrez" in author_name:
        if category_code == 'TXT':
            title = "The Gutierrez Guide to " + title
        elif category_code == 'CK':
            title = "Gutierrez's Nordic " + title
    elif "Julius" in author_name:
        if category_code == 'TXT':
            title = "Julius Gun's " + title + " Survival Handbook"
        elif category_code == 'HIS':
            title = "Guns and Sagas: A Julius Gun " + title
    elif "Kristiansen" in author_name:
        if category_code == 'TXT':
            title = "Kristiansen's Approach to " + title
        elif category_code == 'ROM':
            title = "Love Stories of Kristiansen and " + title

    return title



existing_code = []  # Initialize existing_code as an empty list
new_books = []
for author in AUTHORS:
    for category_code, _ in CATEGORIES:
        title = generate_book_title(author, category_code)
        new_book = {
            "title": title,
            "author": author,
            "due_date": None,
            "isbn": "978-NEW-ISBN-" + category_code + "-" + author.split()[-1], # Placeholder ISBN
            "category": category_code,
            "language": "English", # Assuming English for all new books
            "user": None,
            "condition": "NW", # Defaulting to New condition
            "available": True,
            "image": "static/images/covers/generic_cover.jpg", # Placeholder image
            "storage_location": "Shelf NEW", # Placeholder storage
            "publisher": "Generated Viking Press", # Placeholder publisher
            "publication_year": 2024, # Defaulting to current year
            "copy_number": 1
        }
        existing_code.append(new_book)


print(existing_code)
# save to file
import json
# with open('new_books.json', 'w') as f:
#     json.dump(existing_code, f, indent=4)