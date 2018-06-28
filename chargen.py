import random
import time
from collections import namedtuple
import data_loader
import weighted_random

char_data = data_loader.init_data('char_data.json')
Adventurer = namedtuple('Adventurer', 'name title race age renown profession attributes skills talents')
Race = namedtuple('Race', 'name ages attribute professions talent compound')
Age = namedtuple('Age', 'name weight renown attribute_points skill_points talent_points')
Profession = namedtuple('Profession', 'name attribute skills talents definite')


def parse_attributes():
    return [{'name': a['name'], 'level': 2} for a in char_data['attributes']]


def parse_professions():
    return [Profession(name=p['name'],
                       attribute=[a for a in attributes if a['name'] in p['attribute']][0],
                       skills=[s for s in skills if s['name'] in p['skills']],
                       talents=[t for t in talents if t['name'] in p['talents']],
                       definite=p['definite']) for p in char_data['professions']]


def parse_skills():
    return [{'name': s['name'],
             'attribute': [a for a in attributes if a['name'] in s['attribute']][0],
             'level': 0} for s in char_data['skills']]


def parse_talents():
    return [{'name': t['name'],
             'type': t['type'],
             'races': t['races'],
             'professions': t['professions'],
             'skills': t['skills'],
             'level': 0} for t in char_data['talents']]


def parse_races():
    return [Race(name=r['name'],
                 ages=[Age(name=a['name'],
                           weight=r['ages'][a['name']],
                           renown=a['renown'],
                           attribute_points=a['attribute_points'],
                           skill_points=a['skill_points'],
                           talent_points=a['talent_points']) for a in char_data['ages'] if a['name'] in r['ages']],
                 attribute=[a for a in attributes if a['name'] in r['attribute']][0],
                 professions=[p for p in professions if p.name in r['professions']],
                 talent=[t for t in talents if r['talent'] == t['name']][0],
                 compound=r['compound']) for r in char_data['races']]



attributes = parse_attributes()
skills = parse_skills()
talents = parse_talents()
professions = parse_professions()
races = parse_races()

# the main weight used for random selection
# in regards to race, profession, and owned skills
main_weight = char_data['weights']['main_weight']


# returns a namedtuple of type Adventurer with randomly generated values
def create_adventurer(requested_race=None, requested_profession=None):
    t1 = time.time()
    attributes = parse_attributes()
    skills = parse_skills()
    talents = parse_talents()

    # assigns points in a dictionary using weighted random
    def assign_points(points, choices, max_points, weights):
        choices = choices.copy()
        while points > 0:
            chosen = weighted_random.weighted_random_choice(weights)
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
        chosen = weighted_random.weighted_random_choice({a.name: a.weight for a in ages})
        return [a for a in ages if a.name == chosen][0]

    # returns a profession weighted in favor of the supplied race's typical professions
    def get_profession(race):
        profession_weights = {**{p.name: main_weight for p in professions if p in race.professions},
                              **{p.name: 100 - main_weight for p in professions if p not in race.professions}}
        chosen = weighted_random.weighted_random_choice(profession_weights)
        return [p for p in professions if chosen == p.name][0]

    # returns a dictionary of attributes with values weighted in favor of the
    # supplied race and profession's main attributes
    def get_attributes(race, age, profession):
        attribute_weight = char_data['weights']['attribute_weight']
        attribute_weights = {**{a['name']: attribute_weight for a in attributes if a['name'] == race.attribute['name']
                                or a['name'] == profession.attribute['name']},
                             **{a['name']: 100 - attribute_weight for a in attributes if
                                a['name'] != race.attribute['name']
                                and a['name'] != profession.attribute['name']}}
        return assign_points(age.attribute_points, attributes, 4, attribute_weights)

    # returns a dictionary of skills with values weighted in favor of the supplied profession's typical skills
    def get_skills(age, profession):
        skill_weights = {**{s['name']: main_weight for s in skills if
                            s['name'] in [s['name'] for s in profession.skills]},
                         **{s['name']: 100 - main_weight for s in skills if
                            s['name'] not in [s['name'] for s in profession.skills]}}
        return assign_points(age.skill_points, skills, 5, skill_weights)

    # returns a dictionary of talents with value weights based on race, profession and character skills
    def get_talents(race, age, profession):
        def preferred(talent):
            if race.name in talent.get('races') or \
                    profession.name in talent.get('professions') or \
                    len(set(talent.get('skills')) & set(owned_skills)) > 0:
                return True
            return False

        owned_skills = [s.get('name') for s in char_skills if s.get('level') > 0]
        char_talents = [t for t in talents if t.get('type') == "general" or
                        t.get('name') in [t.get('name') for t in profession.talents] or
                        t.get('name') == race.talent.get('name')]

        talent_weights = {**{t.get('name'): main_weight for t in char_talents if preferred(t)},
                          **{t.get('name'): 100 - main_weight for t in char_talents if not preferred(t)}}

        profession_talent_weights = {talent: weight for talent, weight in talent_weights.items() if
                                     talent in [t.get('name') for t in profession.talents]}
        profession_talent = weighted_random.weighted_random_choice(profession_talent_weights)

        for t in char_talents:
            if t.get('name') == profession_talent or t.get('name') in race.talent.get('name'):
                t['level'] += 1

        return assign_points(age.talent_points, char_talents, 3, talent_weights)

    def get_name(race):
        def generate_name():
            try:
                name_beg = random.choice(list(set(char_data['names']['races'][race.name]['name_beginnings'])))
                name_mid = random.choice(list(set(char_data['names']['races'][race.name]['name_middles'])))
                name_end = random.choice(list(set(char_data['names']['races'][race.name]['name_endings'])))
                return name_beg + name_mid + name_end
            except KeyError:
                print(f'ERROR - COULD NOT GET NAME DATA FOR RACE {race.name}')

        name = generate_name()
        while len(name) <= 2 or name in char_data['names']['banned']['names']:
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
                    title_beg = random.choice(list(set(char_data['names']['races'][race.name]['title_beginnings'] +
                                                       char_data['names']['professions'][profession.name]['title_beginnings'])))
                    title_end = random.choice(list(set(char_data['names']['races'][race.name]['title_endings'] +
                                                       char_data['names']['professions'][profession.name]['title_endings'])))
                except KeyError:
                    print(f'ERROR - COULD NOT GET NAME DATA FOR RACE {race.name} OR PROFESSION {profession.name}')
            return title_beg + title_end
        title = generate_title()
        while title in char_data['names']['banned']['titles']:
            title = generate_title()
        # remove quadruple and triple letters in title
        for c in title:
            if c * 4 in title:
                title = title.replace(f'{c*4}', c*2)
            if c * 3 in title:
                title = title.replace(f'{c*3}', c*2)
        return title

    if requested_race:
        char_race = [r for r in races if r.name == requested_race.lower()][0]
    else:
        char_race = random.choice(races)

    if requested_profession:
        char_profession = [p for p in professions if p.name == requested_profession.lower()][0]
    else:
        char_profession = get_profession(char_race)

    char_age = get_age(char_race.ages)
    char_renown = char_age.renown
    char_attributes = get_attributes(char_race, char_age, char_profession)
    char_skills = get_skills(char_age, char_profession)
    char_talents = get_talents(char_race, char_age, char_profession)
    char_name = get_name(char_race)
    char_title = get_title(char_race, char_profession)

    t2 = time.time() - t1

    print(f'character generated in {t2*1000} ms')


    return Adventurer(name=char_name,
                      title=char_title,
                      race=char_race,
                      age=char_age.name,
                      renown=char_renown,
                      profession=char_profession,
                      attributes=[{'name': a.get('name'), 'level': a.get('level')} for a in char_attributes],
                      skills=[{'name': s.get('name'), 'level': s.get('level')} for s in char_skills],
                      talents=[{'name': t.get('name'), 'level': t.get('level'), 'type': t.get('type')}
                               for t in char_talents])


if __name__ == '__main__':
    for _ in range(0, 1000):
        cool = create_adventurer()