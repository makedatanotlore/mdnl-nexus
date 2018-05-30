import random
import time
from collections import namedtuple
from . import data_loader
from . import weighted_random

place_data = data_loader.init_data('place_data.json')

Village = namedtuple('Village', 'type name age size leader problem speciality oddity institutions')
Institution = namedtuple('Institution', 'name type')
Tavern = namedtuple('Tavern', 'name type speciality oddity guest')
Size = namedtuple('Size', 'name population')
Age = namedtuple('Age', 'name years')


def create_village():
    def get_name():
        def generate_name():
            name_beg = random.choice(list(set(place_data['villages']['names']['beginnings'])))
            name_end = random.choice(list(set(place_data['villages']['names']['endings'])))
            while name_beg in name_end or name_end in name_beg:
                name_beg = random.choice(list(set(place_data['villages']['names']['beginnings'])))
                name_end = random.choice(list(set(place_data['villages']['names']['endings'])))
            return name_beg + name_end
        name = generate_name()
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


    size_weights = {size['name']: size['weight'] for size in place_data['villages']['sizes']}
    place_size = weighted_random.weighted_random_choice(size_weights)
    place_population = [random.randint(size['min_population'], size['max_population']) for size in
                        place_data['villages']['sizes'] if size['name'] == place_size][0]
    place_size = Size(name=place_size, population=place_population)

    place_age = get_age('villages')

    place_leader = random.choice(place_data['villages']['leaders']['oddities']) + " " + \
                   random.choice(place_data['villages']['leaders']['types'])

    place_problem = random.choice(place_data['villages']['problems'])
    place_speciality = random.choice(place_data['villages']['specialities'])
    place_oddity = random.choice(place_data['villages']['oddities'])

    institutions = []
    institution_weights = {inst['name']: inst['weight'] for inst in place_data['villages']['institutions']}
    number_of_institutions = [random.randint(size['min_institutions'], size['max_institutions']) for size in
                              place_data['villages']['sizes'] if size['name'] == place_size.name][0]
    for _ in range(number_of_institutions):
        institution = weighted_random.weighted_random_choice(institution_weights)
        institution_type = [inst['type'] for inst in place_data['villages']['institutions']
                            if inst['name'] == institution][0]

        if institution_type == "tavern":
            institutions.append(create_tavern())
        elif institution_type != "none":
            institutions.append(Institution(name=institution, type=institution_type))

    place_name = get_name()

    village = Village(type='village', name=place_name, age=place_age, size=place_size, leader=place_leader,
                      problem=place_problem, speciality=place_speciality, oddity=place_oddity,
                      institutions=institutions)

    return village


def get_age(place_type):
    age_weights = {age['name']: age['weight'] for age in place_data[place_type]['ages']}
    place_age = weighted_random.weighted_random_choice(age_weights)
    place_years = [random.randint(age['min_age'], age['max_age']) for age in
                   place_data['villages']['ages'] if age['name'] == place_age][0]
    place_age = Age(name=place_age, years=place_years)
    return place_age