import random
import time
from collections import namedtuple

from ...slumpgen.data_loader import init_char_data, init_name_data

char_data = init_char_data()
name_data = init_name_data()

Adventurer = namedtuple('Adventurer', 'name title race age renown profession attributes skills talents')
Race = namedtuple('Race', 'name ages attribute professions talent')
Age = namedtuple('Age', 'name weight renown attribute_points skill_points talent_points')
Profession = namedtuple('Profession', 'name attribute skills talents')


# returns a namedtuple of type Adventurer with randomly generated values
def create_adventurer(requested_race=None, requested_profession=None):
    t1 = time.time()
    races = get_races()

    # the main weight used for random selection
    # in regards to race, profession, and owned skills
    main_weight = char_data['weights']['main_weight']

    # returns a dictionary key chosen by its weight (value)
    # the higher the weight, the likelier it is that the key is chosen
    def get_weighted_random_choice(weights):
        if len(weights) > 0:
            weight_total = sum(weights.values())
            weighted_random_number = random.randint(0, weight_total - 1)
            total_sum = 0

            for weight in weights.items():
                total_sum += weight[1]
                if total_sum > weighted_random_number:
                    return weight[0]

    # assigns points in a dictionary using weighted random
    def assign_points(points, choices, max_points, weights):
        while points > 0:
            chosen = get_weighted_random_choice(weights)
            if char_race.attribute['name'] == chosen and \
                    char_race.attribute['name'] == char_profession.attribute['name']:
                max_points = 6
            elif char_race.attribute['name'] == chosen or char_profession.attribute['name'] == chosen:
                max_points = 5
            else:
                max_points = max_points
            for c in choices:
                if c['name'] == chosen and c['level'] < max_points:
                    c['level'] += 1
                    points -= 1
        return choices

    # returns an age based on the supplied race and its relative age weights
    def get_age(ages):
        chosen = get_weighted_random_choice({a.name: a.weight for a in ages})
        return [a for a in ages if a.name == chosen][0]

    # returns a profession weighted in favor of the supplied race's typical professions
    def get_profession(race):
        professions = get_professions()
        profession_weights = {**{p.name: main_weight for p in professions if p in race.professions},
                              **{p.name: 100 - main_weight for p in professions if p not in race.professions}}
        chosen = get_weighted_random_choice(profession_weights)
        return [p for p in professions if chosen == p.name][0]

    # returns a dictionary of attributes with values weighted in favor of the
    # supplied race and profession's main attributes
    def get_attributes(race, age, profession):
        attribute_weight = char_data['weights']['attribute_weight']
        attributes = [parse_attribute(a) for a in char_data['attributes']]
        attribute_weights = {**{a['name']: attribute_weight for a in attributes if a['name'] == race.attribute['name']
                                or a['name'] == profession.attribute['name']},
                             **{a['name']: 100 - attribute_weight for a in attributes if
                                a['name'] != race.attribute['name']
                                and a['name'] != profession.attribute['name']}}
        return assign_points(age.attribute_points, attributes, 4, attribute_weights)

    # returns a dictionary of skills with values weighted in favor of the supplied profession's typical skills
    def get_skills(age, profession):
        skills = [parse_skill(s) for s in char_data['skills']]
        skill_weights = {**{s['name']: main_weight for s in skills if
                            s['name'] in [s['name'] for s in profession.skills]},
                         **{s['name']: 100 - main_weight for s in skills if
                            s['name'] not in [s['name'] for s in profession.skills]}}
        return assign_points(age.skill_points, skills, 5, skill_weights)

    # returns a dictionary of talents with value weights based on race, profession and character skills
    def get_talents(race, age, profession, skills):
        owned_skills = [s['name'] for s in skills if s['level'] > 0]
        talents = [parse_talent(t) for t in char_data['talents'] if t['type'] == "general" or
                   t['name'] in [t['name'] for t in profession.talents] or
                   t['name'] == race.talent['name']]

        talent_weights = {**{t['name']: main_weight for t in talents if
                             race.name in t['races'] or
                             profession.name in t['professions'] or
                             len(set(t['skills']) & set(owned_skills)) > 0},
                          **{t['name']: 100 - main_weight for t in talents if
                             race.name not in t['races'] and
                             profession.name not in t['professions'] and
                             len(set(t['skills']) & set(owned_skills)) == 0}}

        profession_talent_weights = {talent: weight for talent, weight in talent_weights.items() if
                                     talent in [t['name'] for t in profession.talents]}
        profession_talent = get_weighted_random_choice(profession_talent_weights)

        for t in talents:
            if t['name'] == profession_talent or t['name'] in race.talent['name']:
                t['level'] += 1

        return assign_points(age.talent_points, talents, 3, talent_weights)

    def get_name(race):
        def generate_name():
            try:
                name_beg = random.choice(name_data['races'][race.name]['name_beginnings'])
                name_mid = random.choice(name_data['races'][race.name]['name_middles'])
                name_end = random.choice(name_data['races'][race.name]['name_endings'])
                return name_beg + name_mid + name_end
            except KeyError:
                print(f'ERROR - COULD NOT GET NAME DATA FOR RACE {race.name}')

        name = generate_name()
        while len(name) <= 2 or name in name_data['banned']['names']:
            name = generate_name()
        return name

    def get_title(race, profession):
        def generate_title():
            title_beg = ''
            title_end = ''
            while (title_beg == title_end and title_end == '') or \
                    (title_beg in title_end and title_beg != '') or \
                    (title_end in title_beg and title_end != ''):
                try:
                    title_beg = random.choice(list(set(name_data['races'][race.name]['title_beginnings'] +
                                                       name_data['professions'][profession.name]['title_beginnings'])))
                    title_end = random.choice(list(set(name_data['races'][race.name]['title_endings'] +
                                                       name_data['professions'][profession.name]['title_endings'])))
                except KeyError:
                    print(f'ERROR - COULD NOT GET NAME DATA FOR RACE {race.name} OR PROFESSION {profession.name}')
            return title_beg + title_end
        title = generate_title()
        while title in name_data['banned']['titles']:
            title = generate_title()
        # remove quadruple and triple letters in title
        for c in title:
            if c * 4 in title:
                title = title.replace(f'{c*4}', c*2)
            if c * 3 in title:
                title = title.replace(f'{c*3}', c*2)
        return title

    if requested_race:
        char_race = [r for r in get_races() if r.name == requested_race.lower()][0]
    else:
        char_race = random.choice(races)

    if requested_profession:
        char_profession = [p for p in get_professions() if p.name == requested_profession.lower()][0]
    else:
        char_profession = get_profession(char_race)

    char_age = get_age(char_race.ages)
    char_renown = char_age.renown
    char_attributes = get_attributes(char_race, char_age, char_profession)
    char_skills = get_skills(char_age, char_profession)
    char_talents = get_talents(char_race, char_age, char_profession, char_skills)
    char_name = get_name(char_race)
    char_title = get_title(char_race, char_profession)

    t2 = time.time() - t1

    print(f'character generated in {t2*1000} ms')

    return Adventurer(name=char_name,
                      title=char_title,
                      race=char_race,
                      age=char_age,
                      renown=char_renown,
                      profession=char_profession,
                      attributes=char_attributes,
                      skills=char_skills,
                      talents=char_talents)


def parse_race(r):
    return Race(name=r['name'],
                ages=[parse_age(r, a) for a in char_data['ages'] if a['name'] in r['ages']],
                attribute=[parse_attribute(a) for a in char_data['attributes'] if a['name'] in r['attribute']][0],
                professions=[parse_profession(p) for p in char_data['professions'] if p['name'] in r['professions']],
                talent=[parse_talent(t) for t in char_data['talents'] if r['talent'] == t['name']][0])


def parse_age(r, a):
    return Age(name=a['name'],
               weight=r['ages'][a['name']],
               renown=a['renown'],
               attribute_points=a['attribute_points'],
               skill_points=a['skill_points'],
               talent_points=a['talent_points'])


def parse_attribute(a):
    return {'name': a['name'], 'level': 2}


def parse_profession(p):
    return Profession(name=p['name'],
                      attribute=[parse_attribute(a) for a in char_data['attributes'] if a['name'] in p['attribute']][0],
                      skills=[parse_skill(s) for s in char_data['skills'] if s['name'] in p['skills']],
                      talents=[parse_talent(t) for t in char_data['talents'] if t['name'] in p['talents']])


def parse_skill(s):
    return {'name': s['name'],
            'attribute': [parse_attribute(a) for a in char_data['attributes'] if a['name'] in s['attribute']][0],
            'level': 0}


def parse_talent(t):
    return {'name': t['name'],
            'type': t['type'],
            'races': t['races'],
            'professions': t['professions'],
            'skills': t['skills'],
            'level': 0}


def get_races():
    return [parse_race(r) for r in char_data['races']]


def get_professions():
    return [parse_profession(p) for p in char_data['professions']]
