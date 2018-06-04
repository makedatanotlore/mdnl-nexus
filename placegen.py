import random
import time
from collections import namedtuple
from . import data_loader
from . import weighted_random

place_data = data_loader.init_data('place_data.json')

Village = namedtuple('Village', 'type name age size leader problem speciality oddity institutions')
Institution = namedtuple('Institution', 'name type')
Tavern = namedtuple('Tavern', 'name type speciality oddity guest')
Village_Size = namedtuple('Village_Size', 'name population')
Age = namedtuple('Age', 'name years')

Dungeon = namedtuple('Dungeon', 'type age size origin entrance oddity')
Dungeon_Size = namedtuple('Dungeon_Size', 'name rooms')
Origin = namedtuple('Origin', 'creator purpose reason history')


def create_village():
    t1 = time.time()

    def get_name():
        def generate_name():
            name_beg = random.choice(list(set(place_data['villages']['names']['beginnings'])))
            name_end = random.choice(list(set(place_data['villages']['names']['endings'])))
            while name_beg in name_end or name_end in name_beg:
                name_beg = random.choice(list(set(place_data['villages']['names']['beginnings'])))
                name_end = random.choice(list(set(place_data['villages']['names']['endings'])))
            return name_beg + name_end
        name = generate_name()
        for c in name:
            if c * 4 in name:
                name = name.replace(f'{c*4}', c*2)
            if c * 3 in name:
                name = name.replace(f'{c*3}', c*2)
        return name

    def create_tavern():
        tavern_oddity = random.choice(place_data['villages']['taverns']['oddities'])
        tavern_speciality = random.choice(place_data['villages']['taverns']['specialities'])
        tavern_guest = random.choice(place_data['villages']['taverns']['guests'])

        ampersand = random.choice([True, False])
        if ampersand:
            first, second = random.sample(place_data["villages"]["taverns"]["names"]["endings"], k=2)
            tavern_name = f'{first}' \
                          f' & ' \
                          f'{second}'
        else:
            tavern_name = f'{random.choice(place_data["villages"]["taverns"]["names"]["beginnings"])}' \
                          f' ' \
                          f'{random.choice(place_data["villages"]["taverns"]["names"]["endings"])}'
        return Tavern(name=tavern_name, oddity=tavern_oddity, speciality=tavern_speciality,
                      guest=tavern_guest, type='tavern')

    sizes = {size['name']: size for size in place_data['villages']['sizes']}
    size_weights = {size['name']: size['weight'] for size in sizes.values()}
    place_size = sizes[weighted_random.weighted_random_choice(size_weights)]
    place_population = random.randint(place_size['min_population'], place_size['max_population'])

    place_age = get_age('villages')

    place_leader = random.choice(place_data['villages']['leaders']['oddities']) + " " + \
                   random.choice(place_data['villages']['leaders']['types'])

    place_problem = random.choice(place_data['villages']['problems'])
    place_speciality = random.choice(place_data['villages']['specialities'])
    place_oddity = random.choice(place_data['villages']['oddities'])

    institutions = []
    institution_weights = {inst['name']: inst['weight'] for inst in place_data['villages']['institutions']}
    number_of_institutions = random.randint(place_size['min_institutions'], place_size['max_institutions'])
    for _ in range(number_of_institutions):
        institution = weighted_random.weighted_random_choice(institution_weights)
        institution_type = [inst['type'] for inst in place_data['villages']['institutions']
                            if inst['name'] == institution][0]

        if institution_type == "tavern":
            institutions.append(create_tavern())
        elif institution_type != "none":
            institutions.append(Institution(name=institution, type=institution_type))


    place_name = get_name()
    place_size = Village_Size(name=place_size['name'], population=place_population)

    village = Village(type='village', name=place_name, age=place_age, size=place_size, leader=place_leader,
                      problem=place_problem, speciality=place_speciality, oddity=place_oddity,
                      institutions=institutions)
    t2 = time.time() - t1
    print(f'village generated in {t2*1000} ms')
    return village


def create_dungeon():
    t1 = time.time()

    size_weights = {size['name']: size['weight'] for size in place_data['dungeons']['sizes']}
    place_size = weighted_random.weighted_random_choice(size_weights)
    place_rooms = [random.randint(size['min_rooms'], size['max_rooms']) for size in
                   place_data['dungeons']['sizes'] if size['name'] == place_size][0]
    place_size = Dungeon_Size(name=place_size, rooms=place_rooms)

    place_age = get_age('dungeons')

    creators = {creator['name']: creator for creator in place_data['dungeons']['origins']['creators']}
    creator_weights = {creator['name']: creator['weight'] for creator in creators.values()}
    place_creators = creators[weighted_random.weighted_random_choice(creator_weights)]

    if place_creators['manmade']:
        purpose_weights = {purpose['name']: purpose['weight'] for purpose in place_data['dungeons']['purposes']}
        place_purpose = weighted_random.weighted_random_choice(purpose_weights)
        creator_reason = random.choice(place_data['dungeons']['origins']['reasons'])
        creator_history = random.choice(place_data['dungeons']['origins']['histories'])
    else:
        place_purpose = ""
        creator_reason = ""
        creator_history = ""

    place_origin = Origin(creator=place_creators['name'], purpose=place_purpose, reason=creator_reason,
                          history=creator_history)

    entrance_weights = {entrance['name']: entrance['weight'] for entrance in place_data['dungeons']['entrances']}
    place_entrance = weighted_random.weighted_random_choice(entrance_weights)

    place_oddity = random.choice(place_data['dungeons']['oddities'])

    dungeon = Dungeon(type='dungeon', age=place_age, size=place_size, entrance=place_entrance, origin=place_origin,
                      oddity=place_oddity)

    t2 = time.time() - t1
    print(f'dungeon generated in {t2*1000} ms')

    return dungeon



def get_age(place_type):
    age_weights = {age['name']: age['weight'] for age in place_data[place_type]['ages']}
    place_age = weighted_random.weighted_random_choice(age_weights)
    place_years = [random.randint(age['min_age'], age['max_age']) for age in
                   place_data[place_type]['ages'] if age['name'] == place_age][0]
    place_age = Age(name=place_age, years=place_years)
    return place_age


place_types = {'village': create_village, 'dungeon': create_dungeon}


def create_place(create_place_type=None):
    if create_place_type:
        return place_types[create_place_type]()
    place_type = random.choice([place_type for place_type in place_types.values()])
    return place_type()