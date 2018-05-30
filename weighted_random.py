import random


# returns a dictionary key chosen by its weight (value)
# the higher the weight, the likelier it is that the key is chosen
def weighted_random_choice(weights):
    if len(weights) > 0:
        weight_total = sum(weights.values())
        weighted_random_number = random.randint(0, weight_total - 1)
        total_sum = 0

        for weight in weights.items():
            total_sum += weight[1]
            if total_sum > weighted_random_number:
                return weight[0]
