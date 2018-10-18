import math
import random
import time
from collections import namedtuple

from . import data_loader
from . import weighted_random
from . import chargen

item_data = data_loader.init_data('item_data.json')
char_data = data_loader.init_data('char_data.json')

Weapon = namedtuple('Weapon', 'name type grip rarity bonus damage range value weight attributes myth perk drawback')
Armor = namedtuple('Armor', 'name type rarity bonus value weight attributes myth perk drawback')
Treasure = namedtuple('Treasure', 'name type rarity value weight')
Item = namedtuple('Item', 'name category type grip rarity bonus damage range value weight attributes myth perk drawback')
Tier = namedtuple('Tier', ['descriptions', 'description_at_end', 'rarity', 'bonus_modifier', 'damage_modifier',
                           'value_multiplier', 'required_properties', 'required_attributes', 'added_attributes',
                           'weight_multiplier', 'armor_modifier', 'removed_attributes', 'creator_race',
                           'creator_profession', 'is_artifact', 'myth', 'perk', 'drawback', 'name_beginnings',
                           'name_endings', 'creator_named_item', 'skill_type', 'value_modifier'])
Skill = namedtuple('Skill', 'name type')

SKILLS = [Skill(name=s.get('name'), type=s.get('attribute')) for s in char_data['skills']]

ITEM_NAMES = item_data['item_names']

CURRENCIES = {denomination: currency for denomination, currency in item_data['money'].items()}
ITEM_WEIGHTS = item_data['carry_weights']

WEAPONS = [weapon for weapon in item_data['equipment']['weapons']]
TOOLS = [tool for tool in item_data['equipment']['tools']]
ARMOR_LISTS = {armor_type: armor_list for armor_type, armor_list in item_data['equipment']['armors'].items()}
ARMORS = []
for armor_list in ARMOR_LISTS.values():
    for armor in armor_list:
        ARMORS.append(armor)

TREASURE_LISTS = {treasure_type: treasure for treasure_type, treasure in item_data['items'].items()}
TREASURES = []
for treasure_list in TREASURE_LISTS.values():
    for treasure in treasure_list:
        TREASURES.append(treasure)

CHEAP_COPPER_LIMIT = 100
VALUABLE_COPPER_LIMIT = 400

CHEAP_TIER_WEIGHTS = {'junk': 70, 'common': 30}
VALUABLE_TIER_WEIGHTS = {'common': 60, 'uncommon': 40}
PRECIOUS_TIER_WEIGHTS = {'uncommon': 45, 'rare': 53, 'epic': 2}
ARTIFACT_TIER_WEIGHTS = {'epic': 1}
TIER_WEIGHTS = {'cheap': CHEAP_TIER_WEIGHTS, 'valuable': VALUABLE_TIER_WEIGHTS, 'precious': PRECIOUS_TIER_WEIGHTS,
                'artifact': ARTIFACT_TIER_WEIGHTS}

CHEAP_ITEMS = {
    'treasure': [treasure for treasure in TREASURES if treasure.get('value_in_copper') < CHEAP_COPPER_LIMIT],
    'armor': [armor for armor in ARMORS if armor.get('value_in_copper') < CHEAP_COPPER_LIMIT],
    'weapon': [weapon for weapon in WEAPONS if weapon.get('value_in_copper') < CHEAP_COPPER_LIMIT],
    'tool': [tool for tool in TOOLS if tool.get('value_in_copper') < CHEAP_COPPER_LIMIT]}

VALUABLE_ITEMS = {
    'treasure': [treasure for treasure in TREASURES if treasure.get('value_in_copper') < VALUABLE_COPPER_LIMIT],
    'armor': [armor for armor in ARMORS if armor.get('value_in_copper') < VALUABLE_COPPER_LIMIT],
    'weapon': [weapon for weapon in WEAPONS if weapon.get('value_in_copper') < VALUABLE_COPPER_LIMIT],
    'tool': [tool for tool in TOOLS if tool.get('value_in_copper') < VALUABLE_COPPER_LIMIT]}

PRECIOUS_ITEMS = {
    'treasure': [treasure for treasure in TREASURES if not treasure.get('ignore_tier')],
    'armor': [armor for armor in ARMORS if not armor.get('ignore_tier')],
    'weapon': [weapon for weapon in WEAPONS if not weapon.get('ignore_tier')],
    'tool': [tool for tool in TOOLS if not tool.get('ignore_tier')]}

ITEM_VALUES = {'cheap': CHEAP_ITEMS, 'valuable': VALUABLE_ITEMS, 'precious': PRECIOUS_ITEMS, 'artifact': PRECIOUS_ITEMS}

TIERS = {tier: [Tier(
    descriptions=subtier.get('descriptions'),
    description_at_end=subtier.get('description_at_end'),
    rarity=tier,
    bonus_modifier=subtier.get('bonus_modifier'),
    damage_modifier=subtier.get('damage_modifier'),
    value_multiplier=subtier.get('value_multiplier'),
    required_properties=subtier.get('required_properties'),
    required_attributes=subtier.get('required_attributes'),
    added_attributes=subtier.get('added_attributes'),
    weight_multiplier=subtier.get('weight_multiplier'),
    armor_modifier=subtier.get('armor_modifier'),
    removed_attributes=subtier.get('removed_attributes'),
    creator_race=subtier.get('creator_race'),
    creator_profession=subtier.get('creator_profession'),
    myth=subtier.get('myth'),
    perk=subtier.get('perk'),
    drawback=subtier.get('drawback'),
    name_beginnings=subtier.get('name_beginnings'),
    name_endings=subtier.get('name_endings'),
    creator_named_item=subtier.get('creator_named_item'),
    skill_type=subtier.get('skill_type'),
    is_artifact=subtier.get('is_artifact'),
    value_modifier=subtier.get('value_modifier'))
    for subtier in item_data['item_tiers'][tier]] for tier in item_data['item_tiers']}


def generate_item(item_types, item_value='cheap', max_weight=100):
    t1 = time.time()

    print(f'requested item of type {item_types}')
    item_type = random.choice(item_types)
    print(list(ITEM_VALUES.get(item_value).keys()))
    if item_type.lower() not in list(ITEM_VALUES.get(item_value).keys()):
        item_type = random.choice(list(ITEM_VALUES.get(item_value).keys()))

    if max_weight is None:
        max_weight = 100

    def get_item_list():
        items = ITEM_VALUES.get(item_value).get(item_type.lower())
        return [item for item in items if item.get('carry_weight') <= max_weight]

    tiers = TIERS.get(weighted_random.weighted_random_choice(TIER_WEIGHTS.get(item_value)))

    possible_items = get_item_list()
    while not possible_items:
        item_type = random.choice(list(ITEM_VALUES.get(item_value).keys()))
        possible_items = get_item_list()

    item = random.choice(possible_items)

    item_properties = item.get('properties')
    item_attributes = item.get('attributes')

    if not item.get('ignore_tier'):
        item_tier = get_tier(item_properties, tiers)
    else:
        tiers = TIERS.get('common')
        item_tier = get_tier(item_properties, tiers)

    item_weight = get_item_weight(item, item_tier)
    item_attributes = get_item_attributes(item_attributes, item_tier, item_weight)

    item_myth = None
    item_perk = None
    item_drawback = None
    creator = None

    if item_tier.is_artifact:
        creator = chargen.generate_character(requested_kin=item_tier.creator_race,
                                             requested_profession=item_tier.creator_profession)
        creator_name = f'{creator.name.title()} {creator.title.title()}'
        item_myth = item_tier.myth.replace('{{ creator_name }}', creator_name)
        item_myth = item_myth.replace('{{ determiner }}',
                                      item_data['determiners'][item.get("indefinite")])
        item_myth = item_myth.replace('{{ item_name }}', item.get('name').split(' ')[-1])
        item_myth = item_myth.replace('{{ race_compound }}', creator.kin.compound)
        item_myth = item_myth.replace('{{ profession_definite }}', creator.profession.definite)

        item_myth = item_myth.replace('{{ creator_origin }}', random.choice(item_data['creator_origins']))
        skills = {s.name: s.level for s in creator.skills}
        skill = max(skills, key=(lambda key: skills[key])).capitalize()
        item_perk = item_tier.perk.replace('{{ skill }}', skill)
        item_drawback = item_tier.drawback.replace('{{ skill }}', skill)

    item_name = get_item_name(item, item_tier, creator=creator)

    t2 = time.time() - t1

    if item.get('damage'):
        item_damage = (item.get('damage') + item_tier.damage_modifier
                       if item.get('damage') + item_tier.damage_modifier >= 0 else 0)
    else:
        item_damage = None
    if item.get('bonus'):
        if item_type == 'armor':
            item_bonus = (item.get('bonus') + item_tier.armor_modifier
                          if item.get('bonus') + item_tier.armor_modifier >= 0 else 0)
        else:
            item_bonus = (item.get('bonus') + item_tier.bonus_modifier
                          if item.get('bonus') + item_tier.bonus_modifier >= 0 else 0)
    else:
        item_bonus = None

    item = Item(
        name=item_name,
        category=item_type,
        type=item.get('type'),
        grip=item.get('grip'),
        rarity=item_tier.rarity,
        bonus=item_bonus,
        damage=item_damage,
        range=item.get('range'),
        value=get_total_value(item.get('value_in_copper'), item_tier.value_multiplier, item_tier.value_modifier),
        weight=item_weight,
        attributes=item_attributes,
        myth=item_myth,
        perk=item_perk,
        drawback=item_drawback)

    print(f'{item_type} generated in {t2*1000} ms')

    return item


def get_tier(properties, tiers):
    tier = random.choice(tiers)
    if tier.required_properties:
        if not (len(set(tier.required_properties) & set(properties)) > 0):
            print(f'- could not get tier (Properties: {properties}) - recursion!')
            tier = get_tier(properties, tiers)
    return tier


def get_total_value(value, multiplier, modifier, randomize_value=True):
    gold_value_in_copper = CURRENCIES['gold']['copper_value']
    silver_value_in_copper = CURRENCIES['silver']['copper_value']
    gold = CURRENCIES['gold']['name']
    silver = CURRENCIES['silver']['name']
    copper = CURRENCIES['copper']['name']
    worthless = CURRENCIES['worthless']['name']

    if modifier:
        remaining_copper = (value + modifier) * multiplier
    else:
        remaining_copper = value * multiplier

    if randomize_value:
        min_value = int(remaining_copper * 0.9)
        max_value = int(remaining_copper * 1.1)
        remaining_copper = random.randint(min_value, max_value)

    if remaining_copper > 0:
        total_value_in_gold = 0
        total_value_in_silver = 0

        if remaining_copper > 1000:
            while remaining_copper - gold_value_in_copper >= 0:
                total_value_in_gold += 1
                remaining_copper -= gold_value_in_copper

        while remaining_copper - silver_value_in_copper >= 0:
            total_value_in_silver += 1
            remaining_copper -= silver_value_in_copper

        total_value_in_copper = int(remaining_copper)
        values = []
        if total_value_in_gold > 0:
            values.append(f'{total_value_in_gold} {gold}')
        if total_value_in_silver > 0:
            values.append(f'{total_value_in_silver} {silver}')
        if total_value_in_copper > 0:
            values.append(f'{total_value_in_copper} {copper}')

        return ', '.join(values)
    else:
        return worthless


def get_item_name(item, tier, creator=None):
    if creator:
        if tier.creator_named_item or random.choice([True, False]):
            first_name = creator.name
            if first_name.endswith('s'):
                name = f'{first_name} {item.get("name").split(" ")[-1]} ({item.get("name")})'
            else:
                name = f'{first_name}s {item.get("name").split(" ")[-1]} ({item.get("name")})'
            return name
        else:
            name_beginnings = tier.name_beginnings
            name_endings = tier.name_endings
            for name in ITEM_NAMES:
                if len(set(name.get('required_properties')) & set(item.get('properties'))) > 0:
                    name_endings += name['name_endings']
            name = f'{random.choice(name_beginnings)}{random.choice(name_endings)} ({item.get("name")})'
            return name
    if tier.descriptions:
        if tier.description_at_end:
            return f'{item.get("name")} {tier.descriptions.get(item.get("indefinite"))}'
        else:
            return f'{tier.descriptions.get(item.get("indefinite"))} {item.get("name")}'
    return item.get('name')


def get_item_weight(item, tier, creator=None):
    item_weight = item.get('carry_weight')
    if tier.weight_multiplier:
        item_weight = item_weight * tier.weight_multiplier
        if item_weight > 0.5:
            item_weight = math.ceil(item_weight)
        elif 0 < item_weight < 0.5:
            item_weight = 0.5
        elif item_weight == 0.0:
            item_weight = 0

    return ITEM_WEIGHTS.get(str(item_weight)) if ITEM_WEIGHTS.get(str(item_weight)) else str(item_weight)


def get_item_attributes(attributes, tier, weight):
    if attributes is not None:
        item_attributes = sorted(list(set(attributes)))
    else:
        item_attributes = attributes
    if tier.added_attributes and item_attributes is not None:
        item_attributes = list(set(item_attributes).union(set(tier.added_attributes)))
    if tier.removed_attributes and item_attributes is not None:
        item_attributes = list(set(item_attributes) - (set(tier.removed_attributes)))
    if item_attributes is not None and weight != ITEM_WEIGHTS.get('0') and weight != ITEM_WEIGHTS.get('1'):
        if len(item_attributes) > 0 and len(weight) > 1:
            item_attributes.insert(0, ITEM_WEIGHTS.get('2')) \
                if weight not in ITEM_WEIGHTS.values() else item_attributes.insert(0, weight)
        elif len(weight) > 1:
            item_attributes.append(ITEM_WEIGHTS.get('2')) \
                if weight not in ITEM_WEIGHTS.values() else item_attributes.append(weight)

    return item_attributes


"""item = generate_item('tool')
print(f'Föremål: {item.name.title()}')
print(f'Typ: {item.type.title()} {("(" + item.grip.upper() + ")") if item.grip else ""}')
if item.range:
    print(f'Räckvidd: {item.range.title()}')
if item.bonus:
    print(f'Bonus: {item.bonus} Skada: {item.damage}')
print(f'Värde: {str(item.value).capitalize()} Vikt: {str(item.weight).capitalize()}')
if item.attributes:
    print(f'Egenskaper: {", ".join(item.attributes).capitalize()}')
if item.myth:
    print(f'Sägen: {item.myth}')
    print(f'Effekt: {item.perk}')
    print(f'Nackdel: {item.drawback}')
print()"""


