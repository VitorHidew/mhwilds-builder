def transcended_slots_for_armor(armor) -> list[int]:
    """TU4: R5 first three / R6 first two slots, capped at level three."""
    affected = {5: 3, 6: 2}.get(armor.rarity, 0)
    slots = list(armor.slots)
    slots += [0] * max(0, affected - len(slots))
    for index in range(affected):
        slots[index] = min(3, slots[index] + 1)
    return [size for size in slots if size > 0]
