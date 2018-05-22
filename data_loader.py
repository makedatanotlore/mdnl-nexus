import json
import os

from collections import namedtuple

base_folder = os.path.dirname(__file__)
Race = namedtuple('Race', 'name ages attribute professions talent')
Age = namedtuple('Age', 'name weight renown attribute_points skill_points talent_points')
Profession = namedtuple('Profession', 'name attribute skills talents')


def init_data():
    with open(os.path.join(base_folder, 'sources', 'char_data.json'), encoding='utf-8') as f:
        data = json.load(f)
        return data


def init_name_data():
    with open(os.path.join(base_folder, 'sources', 'name_data.json'), encoding='utf-8') as f:
        data = json.load(f)
        return data


char_data = init_data()
name_data = init_name_data()


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



