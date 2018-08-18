import random
import time
from collections import namedtuple

from . import data_loader
from . import weighted_random
from . import itemgen

place_data = data_loader.init_data('place_data.json')
creature_data = data_loader.init_data('creature_data.json')

Village = namedtuple('Village', 'type name age size leader problem speciality oddity institutions')
Institution = namedtuple('Institution', 'name type')
Tavern = namedtuple('Tavern', 'name type speciality oddity guest')
Village_Size = namedtuple('Village_Size', 'name population')

Dungeon = namedtuple('Dungeon', 'type age size origin entrance oddity')
Dungeon_Size = namedtuple('Dungeon_Size', 'name rooms')

Fortress = namedtuple('Fortress', 'type name age size creator purpose history condition inhabitants oddity')
Fortress_Size = namedtuple('Fortress_Size', 'name size min_garrison max_garrison')

Room = namedtuple('Room', 'type doors traps treasures monsters oddity')
Door = namedtuple('Door', 'name trap status')
Treasure = namedtuple('Treasure', 'name contents trap')
Trap = namedtuple('Trap', 'name effect victim')

Origin = namedtuple('Origin', 'creator purpose reason history')
Age = namedtuple('Age', 'name years')



def create_village():
    t1 = time.time()

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
        all_institutions = {inst['name']: inst for inst in place_data['villages']['institutions']}
        institution = all_institutions[weighted_random.weighted_random_choice(institution_weights)]

        if institution.get('type') == "tavern":
            institutions.append(create_tavern())
        elif institution.get('type'):
            if institution.get('specializations'):
                institution_name = f'{institution["name"]} ({random.choice(institution.get("specializations"))})'
            else:
                institution_name = institution['name']
            institutions.append(Institution(name=institution_name, type=institution['type']))


    place_name = get_name('villages')
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


def create_fortress():
    t1 = time.time()

    place_age = get_age('fortresses')

    sizes = {size['name']: size for size in place_data['fortresses']['sizes']}
    size_weights = {size['name']: size['weight'] for size in sizes.values()}
    place_size = sizes[weighted_random.weighted_random_choice(size_weights)]
    place_size = Fortress_Size(name=place_size['name'], size=place_size['size'],
                               min_garrison=place_size['min_garrison'],
                               max_garrison=place_size['max_garrison'])

    creators = {creator['name']: creator for creator in place_data['fortresses']['origins']['creators']}
    creator_weights = {creator['name']: creator['weight'] for creator in creators.values()}
    place_creators = weighted_random.weighted_random_choice(creator_weights)
    creator_claim_to_fame = random.choice(place_data['fortresses']['origins']['claims_to_fame'])

    purpose_weights = {purpose['name']: purpose['weight'] for purpose in place_data['dungeons']['purposes']}
    place_purpose = weighted_random.weighted_random_choice(purpose_weights)

    conditions = {condition['name']: condition for condition in place_data['fortresses']['origins']['conditions']}
    condition_weights = {condition['name']: condition['weights'][place_age.name] for condition in conditions.values()}
    place_condition = weighted_random.weighted_random_choice(condition_weights)

    place_history = random.choice(place_data['fortresses']['origins']['histories'])

    inhabiteds = {result['name']: result for result in place_data['fortresses']['origins']['inhabitants']}
    inhabited_weights = {result['name']: result['weights'][place_condition] for result in inhabiteds.values()}
    place_inhabited = inhabiteds[weighted_random.weighted_random_choice(inhabited_weights)]

    if place_inhabited.get('roll_empty'):
        empties = {empty['name']: empty for empty in place_data['fortresses']['empty']}
        empty_weights = {empty['name']: empty['weight'] for empty in empties.values()}
        empty = empties[weighted_random.weighted_random_choice(empty_weights)]
        if empty.get('min_amount') and empty.get('max_amount'):
            amount = random.randint(empty['min_amount'], empty['max_amount'])
            place_inhabited = empty['name'].replace('{{ amount }}', str(amount))
        elif empty.get('monsters'):
            monster = random.choice(empty['monsters'])
            place_inhabited = empty['name'].replace('{{ monster }}', monster)
        else:
            place_inhabited = place_inhabited['name']
    elif place_inhabited.get('roll_moved_in'):
        intruders = {intruder['name']: intruder for intruder in place_data['fortresses']['intruders']}
        intruder_weights = {intruder['name']: intruder['weight'] for intruder in intruders.values()}
        intruders = intruders[weighted_random.weighted_random_choice(intruder_weights)]

        if intruders.get('roll_for_monster'):
            monsters = {monster['name']: monster for monster in creature_data['monsters']}
            monster_weights = {monster['name']: monster['weight'] for monster in monsters.values()}
            monster = monsters[weighted_random.weighted_random_choice(monster_weights)]
            place_inhabited = place_inhabited['name'].replace('{{ amount }} {{ intruder }}',
                                                              f'{monster["single"]} {monster["name"]}')
        else:
            amount = random.randint(intruders['amount'][place_size.size]['min_intruders'],
                                    intruders['amount'][place_size.size]['max_intruders'])
            if amount == 1:
                place_inhabited = place_inhabited['name'].replace('{{ amount }} {{ intruder }}',
                                                                  f'{intruders.get("single")}')
            else:
                place_inhabited = place_inhabited['name'].replace('{{ amount }} {{ intruder }}',
                                                                  f'{amount} {intruders["name"]}')
    else:
        place_inhabited = place_inhabited['name']

    place_oddity = random.choice(place_data['fortresses']['oddities'])

    place_creators = f'{place_creators} känd för {creator_claim_to_fame}'
    place_name = get_name('fortresses')

    fortress = Fortress(type='fortress', name=place_name, age=place_age, size=place_size, creator=place_creators,
                        purpose=place_purpose, history=place_history, condition=place_condition,
                        inhabitants=place_inhabited, oddity=place_oddity)

    t2 = time.time() - t1
    print(f'fortress generated in {t2*1000} ms')

    return fortress


ROOM_TYPES = {type['name']: type for type in place_data['dungeons']['rooms']['types']}
ROOM_CONTENTS = {content['name']: content for content in place_data['dungeons']['rooms']['contents']}
ROOM_TREASURES = {treasure['name']: treasure for treasure in place_data['dungeons']['rooms']['treasures']}
ROOM_TRAPS = {trap['name']: trap for trap in place_data['dungeons']['rooms']['traps']}
ROOM_DOORS = {door['number']: door['weight'] for door in place_data['dungeons']['rooms']['entrances']}
ROOM_DOOR_STATES = {state['name']: state for state in place_data['dungeons']['rooms']['entrance_states']}
ROOM_MONSTERS = {monster['name']: monster['weight'] for monster in place_data['dungeons']['inhabitants']}


def create_room():
    def roll_door():
        state = ROOM_DOOR_STATES[weighted_random.weighted_random_choice(door_weights)]
        trap = None
        if state.get('trapped'):
            trap = roll_trap()
        return Door(name=state.get('name'), trap=trap, status=state.get('status'))

    def roll_treasure():
        treasure_weights = {treasure['name']: treasure['weight'] for treasure in ROOM_TREASURES.values()}
        treasure = ROOM_TREASURES[weighted_random.weighted_random_choice(treasure_weights)]
        trap = None
        if 0 < treasure.get('trap_chance') <= random.randint(1, 6):
            trap = roll_trap()

        items = []
        max_weight = treasure.get('max_weight')
        if max_weight is None:
            max_weight = 100
        for _ in range(0, treasure.get('simple_treasure_rolls')):
            items.append(itemgen.generate_item(['any'], item_value='cheap', max_weight=max_weight))
        for _ in range(0, treasure.get('valuable_treasure_rolls')):
            items.append(itemgen.generate_item(['weapon', 'armor', 'treasure'], item_value='valuable', max_weight=max_weight))
        for _ in range(0, treasure.get('precious_treasure_rolls')):
            items.append(itemgen.generate_item(['weapon', 'armor', 'treasure'], item_value='precious', max_weight=max_weight))

        return Treasure(name=treasure.get('name'), contents=items, trap=trap)

    def roll_trap():
        trap_weights = {trap['name']: trap['weight'] for trap in ROOM_TRAPS.values()}
        trap = ROOM_TRAPS[weighted_random.weighted_random_choice(trap_weights)]
        trap_effect = trap.get('effect')
        if trap.get('effect_min'):
            trap_effect = trap.get('effect').replace('{{ effect }}', str(random.randint(trap.get('effect_min'),
                                                                                        trap.get('effect_max'))))
        return Trap(name=trap.get('name'),
                    effect=trap_effect,
                    victim=trap.get('victim'))

    type_weights = {type['name']: type['weight'] for type in ROOM_TYPES.values()}
    room_type = ROOM_TYPES[weighted_random.weighted_random_choice(type_weights)]
    door_amount = int(weighted_random.weighted_random_choice(ROOM_DOORS))
    door_weights = {state['name']: state['weight'] for state in ROOM_DOOR_STATES.values()}

    doors = []
    for _ in range(0, door_amount):
        doors.append(roll_door())

    content_weights = {content['name']: content['weight'] for content in ROOM_CONTENTS.values()}

    treasure = []
    traps = []
    monsters = []

    if room_type.get('content_rolls') > 0:
        for _ in range(0, room_type.get('content_rolls')):
            room_content = ROOM_CONTENTS[weighted_random.weighted_random_choice(content_weights)]

            roll = random.randint(1, 6)
            if room_content.get('treasure_chance') >= roll:
                treasure.append(roll_treasure())

            if room_content.get('trapped'):
                traps.append(roll_trap())

            if room_content.get('inhabited'):
                monsters.append(weighted_random.weighted_random_choice(ROOM_MONSTERS))

    return Room(type=room_type.get('name'),
                doors=doors,
                traps=list(set(traps)),
                treasures=treasure,
                monsters=list(set(monsters)),
                oddity=random.choice(place_data['dungeons']['oddities']))


def get_age(place_type):
    age_weights = {age['name']: age['weight'] for age in place_data[place_type]['ages']}
    place_age = weighted_random.weighted_random_choice(age_weights)
    place_years = [random.randint(age['min_age'], age['max_age']) for age in
                   place_data[place_type]['ages'] if age['name'] == place_age][0]
    place_age = Age(name=place_age, years=place_years)
    return place_age


def get_name(place_type):
    def generate_name():
        name_beg = random.choice(list(set(place_data[place_type]['names']['beginnings'])))
        name_end = random.choice(list(set(place_data[place_type]['names']['endings'])))
        while name_beg in name_end or name_end in name_beg:
            name_beg = random.choice(list(set(place_data[place_type]['names']['beginnings'])))
            name_end = random.choice(list(set(place_data[place_type]['names']['endings'])))
        return name_beg + name_end
    name = generate_name()
    for c in name:
        if c * 4 in name:
            name = name.replace(f'{c*4}', c*2)
        if c * 3 in name:
            name = name.replace(f'{c*3}', c*2)
    return name


place_types = {'village': create_village, 'dungeon': create_dungeon, 'fortress': create_fortress}


def create_place(create_place_type=None):
    if create_place_type:
        return place_types[create_place_type]()
    place_type = random.choice([place_type for place_type in place_types.values()])
    return place_type()


"""room = create_room()
print(room.type.capitalize())
print('Egenhet ---')
print(f'    {room.oddity.capitalize()}')
print()
if room.traps:
    print('Fällor ---')
    print(f'    Typ: {room.traps.name.capitalize()}')
    print(f'    Effekt: {room.traps.effect.capitalize()}')
    print(f'    Drabbar: {room.traps.victim.capitalize()}')
    print()
if room.doors:
    print('Dörrar ---')
    for door in room.doors:
        print(f'    {door.name.capitalize()}')
        if door.trap:
            print(f'        Fälla:')
            print(f'            Typ: {door.trap.name.capitalize()}')
            print(f'            Effekt: {door.trap.effect.capitalize()}')
            print(f'            Drabbar: {door.trap.victim.capitalize()}')
    print()
if room.treasures:
    print('Skatter ---')
    print(f'    {room.treasures.name.capitalize()}:')
    for item in room.treasures.contents:
        print(f'        {item.name.capitalize()}')
        print(f'            Typ: {item.type.title()} {("(" + item.grip.upper() + ")") if item.grip else ""}')
        if item.range:
            print(f'            Räckvidd: {item.range.title()}')
        if item.bonus is not None:
            print(f'            Bonus: {item.bonus}')
        if item.damage is not None:
            print(f'            Skada: {item.damage}')
        print(f'            Värde: {str(item.value).capitalize()} Vikt: {str(item.weight).capitalize()}')
        if item.attributes:
            print(f'            Egenskaper: {", ".join(item.attributes).capitalize()}')
        if item.myth:
            print(f'            Sägen: {item.myth}')
            print(f'            Effekt: {item.perk}')
            print(f'            Nackdel: {item.drawback}')
    if room.treasures.trap:
        print(f'    Fälla:')
        print(f'        Typ: {room.treasures.trap.name.capitalize()}')
        print(f'        Effekt: {room.treasures.trap.effect.capitalize()}')
        print(f'        Drabbar: {room.treasures.trap.victim.capitalize()}')
    print()
if room.monsters:
    print('Monster ---')
    print(f'    {room.monsters.capitalize()}')
    print()"""