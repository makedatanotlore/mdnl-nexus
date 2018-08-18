import random
import time
from collections import namedtuple
from . import data_loader as dl
from . import weighted_random as wr

# Initialize and load data from JSON file
char_data = dl.init_data('char_data.json')

# A character with attributes
Character = namedtuple('Character', ['name', 'title', 'kin', 'profession', 'attributes', 'skills', 'talents',
                                     'personality', 'age', 'renown'])

# An age with attributes
Age = namedtuple('Age', ['name', 'renown', 'attribute_points', 'skill_points',
                         'talent_points'])

# A kin (fantasy race) with attributes
Kin = namedtuple('Kin', ['name', 'age_weights', 'compound', 'attribute',  'talent',
                         'professions'])

# A profession (class) with attributes
Profession = namedtuple('Profession', ['name', 'attribute', 'skills', 'talents', 'definite'])

Attribute = namedtuple('Attribute', ['name', 'level'])

Skill = namedtuple('Skill', ['name', 'attribute', 'level'])

Talent = namedtuple('Talent', ['name', 'type', 'level'])

Personality = namedtuple('Personality', ['trait', 'like', 'dislike'])


# Return a dictionary of possible ages and their attributes
# {'young': Age(name='young', base_renown=...)}
def parse_ages():
    ages = []
    age_data = char_data.get('ages')
    for age in age_data:
        ages.append(Age(name=age.get('name'),
                        renown=age.get('renown'),
                        attribute_points=age.get('attribute_points'),
                        skill_points=age.get('skill_points'),
                        talent_points=age.get('talent_points')))
    return {age.name: age for age in ages}


# Return a dictionary of possible kins and their attributes
# {'human': Kin(name='human', age_weights=...)}
def parse_kins():
    kins = []
    kin_data = char_data.get('races')
    for kin in kin_data:
        kins.append(Kin(name=kin.get('name'),
                        age_weights=kin.get('ages'),
                        attribute=kin.get('attribute'),
                        professions=kin.get('professions'),
                        compound=kin.get('compound'),
                        talent=kin.get('talent')))
    return {kin.name: kin for kin in kins}


# Return a dictionary of possible professions and their attributes
# {'warrior': Profession(name='warrior', attribute=...)}
def parse_professions():
    professions = []
    profession_data = char_data.get('professions')
    for profession in profession_data:
        professions.append(Profession(name=profession.get('name'),
                                      attribute=profession.get('attribute'),
                                      skills=profession.get('skills'),
                                      talents=profession.get('talents'),
                                      definite=profession.get('definite')))
    return {profession.name: profession for profession in professions}


# Instantiate static lists/dicts of character options
AGES = parse_ages()
KINS = parse_kins()
PROFESSIONS = parse_professions()
ATTRIBUTES = char_data.get('attributes')
SKILLS = {skill.get('name'): skill for skill in char_data.get('skills')}
TALENTS = {talent.get('name'): talent for talent in char_data.get('talents')}
POINT_LIMITS = char_data.get('point_limits')

WEIGHTS = char_data.get('weights')
BASE_WEIGHT = WEIGHTS.get('BASE')
ATTRIBUTE_WEIGHT = WEIGHTS.get('attributes')
SKILL_WEIGHT = WEIGHTS.get('skills')
PROFESSION_WEIGHT = WEIGHTS.get('professions')
TALENT_WEIGHT = WEIGHTS.get('talents')


def get_attributes(base_points, kin, profession):
    points = base_points + random.randint(-1, 1)
    attributes = {attribute.get('name'): 2 for attribute in ATTRIBUTES}
    point_limits = {}
    weights = {}

    for attribute in attributes.keys():
        # matches is the number of matching attributes with the main attribute of the kin and profession
        # if they match, the point limit of the particular attribute will be higher
        matches = len({kin.attribute} & {attribute}) + len({profession.attribute} & {attribute})
        point_limit = POINT_LIMITS.get('attributes').get(str(matches))
        point_limits[attribute] = point_limit if point_limit else POINT_LIMITS.get('attributes').get('DEFAULT')

        # getting the weights of the different attributes depending on the number of matches
        weights[attribute] = ATTRIBUTE_WEIGHT if matches > 0 else BASE_WEIGHT - ATTRIBUTE_WEIGHT

    while points > 0 and len(weights.keys()) > 0:
        attribute = wr.weighted_random_choice(weights)
        if attributes[attribute] < point_limits[attribute]:
            attributes[attribute] += 1
            points -= 1
        else:
            del weights[attribute]

    return [Attribute(name=key, level=value) for key, value in attributes.items()]


def get_skills(base_points, profession):
    points = base_points + random.randint(-1, 1)
    skills = {skill.get('name'): 0 for skill in SKILLS.values()}
    point_limits = {}
    weights = {}

    for skill in skills.keys():
        # matches is the number of matching skills with the skills of the profession
        # if matches, the higher the point limit of the particular skill
        matches = len(set(profession.skills) & {skill})
        point_limit = POINT_LIMITS.get('skills').get(str(matches))
        point_limits[skill] = point_limit if point_limit else POINT_LIMITS.get('skills').get('DEFAULT')

        # getting the weights of the different skills depending on the number of matches
        weights[skill] = SKILL_WEIGHT if matches > 0 else BASE_WEIGHT - SKILL_WEIGHT

    while points > 0 and len(weights.keys()) > 0:
        skill = wr.weighted_random_choice(weights)
        if skills[skill] < point_limits[skill]:
            skills[skill] += 1
            points -= 1
        else:
            del weights[skill]

    return [Skill(name=key, level=value, attribute=SKILLS.get(key).get('attribute')) for key, value in skills.items()
            if value > 0]


def get_talents(base_points, kin, profession, skills):
    points = base_points
    talents = {kin.talent: 1}

    point_limit = POINT_LIMITS.get('talents').get('DEFAULT')
    weights = {}

    for profession_talent in profession.talents:
        talent = TALENTS.get(profession_talent)
        matches = (len({kin.name} & set(talent.get('races'))) +
                   len({profession.name} & set(talent.get('professions'))) +
                   len(set(skills) & set(talent.get('skills'))))
        weights[profession_talent] = TALENT_WEIGHT * matches if matches > 0 else BASE_WEIGHT - TALENT_WEIGHT

    talents[wr.weighted_random_choice(weights)] = 1

    for talent in TALENTS.values():
        if talent.get('type') == 'general':
            matches = (len({kin.name} & set(talent.get('races'))) +
                       len({profession.name} & set(talent.get('professions'))) +
                       len(set(skills) & set(talent.get('skills'))))
            weights[talent.get('name')] = TALENT_WEIGHT * matches if matches > 0 else BASE_WEIGHT - TALENT_WEIGHT

    while points > 0 and len(weights.keys()) > 0:
        talent = wr.weighted_random_choice(weights)
        if talents.get(talent):
            if talents[talent] < point_limit:
                talents[talent] += 1
                points -= 1
            else:
                del weights[talent]
        else:
            talents[talent] = 1
            points -= 1

    return [Talent(name=key, level=value, type=TALENTS.get(key).get('type')) for key, value in talents.items()]


NAME_BITS = char_data.get('names')


def get_character_name(kin: str):
    name_beginnings = NAME_BITS.get('races').get(kin).get('name_beginnings')
    name_middles = NAME_BITS.get('races').get(kin).get('name_middles')
    name_endings = NAME_BITS.get('races').get(kin).get('name_endings')

    def generate_name():
        name = random.choice(name_beginnings) + random.choice(name_middles) + random.choice(name_endings)

        while name in NAME_BITS.get('banned').get('names') or len(name) <= 2:
            name = generate_name()

        return name

    return generate_name()


def get_character_title(kin: str, profession: str):
    title_beginnings = NAME_BITS.get('races').get(kin).get('title_beginnings') + \
                       NAME_BITS.get('professions').get(profession).get('title_beginnings')
    title_endings = NAME_BITS.get('races').get(kin).get('title_endings') + \
                    NAME_BITS.get('professions').get(profession).get('title_endings')

    def generate_title():
        title = random.choice(title_beginnings) + random.choice(title_endings)

        while title in NAME_BITS.get('banned').get('titles') or len(title) <= 2:
            title = generate_title()

        return title

    return generate_title()


PERSONALITIES = char_data.get('personalities')


def get_personality():
    trait = random.choice(PERSONALITIES.get('traits'))
    like, dislike = random.sample(PERSONALITIES.get('things'), 2)

    return Personality(trait=trait,
                       like=like,
                       dislike=dislike)


def generate_character(requested_kin=None, requested_profession=None):
    t1 = time.time()
    # Get requested kin or choose a random one
    if requested_kin:
        kin = KINS.get(requested_kin)
    else:
        kin = random.choice(list(KINS.values()))

    # Get a weighted random age depending on kin
    age = AGES.get(wr.weighted_random_choice(kin.age_weights))

    # Get requested kin or choose a random one based on kin
    if requested_profession:
        profession = PROFESSIONS.get(requested_profession)
    else:
        profession_weights = {}
        for profession in PROFESSIONS.values():
            profession_weights[profession.name] = PROFESSION_WEIGHT if profession.name in kin.professions \
                else BASE_WEIGHT - PROFESSION_WEIGHT
        profession = PROFESSIONS.get(wr.weighted_random_choice(profession_weights))

    attributes = get_attributes(age.attribute_points, kin, profession)
    skills = get_skills(age.skill_points, profession)
    talents = get_talents(age.talent_points, kin, profession, skills)
    name = get_character_name(kin.name)
    title = get_character_title(kin.name, profession.name)
    personality = get_personality()

    character = Character(name=name,
                          title=title,
                          age=age,
                          renown=age.renown,
                          kin=kin,
                          profession=profession,
                          attributes=attributes,
                          skills=skills,
                          talents=talents,
                          personality=personality)

    t2 = time.time() - t1

    print(f'character generated in {t2*1000} ms')

    return character