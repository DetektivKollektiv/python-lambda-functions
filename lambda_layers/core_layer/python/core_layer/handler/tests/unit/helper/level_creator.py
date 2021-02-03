from core_layer.model import Level


def create_level(id: int, required_exp: int) -> Level:
    level = Level()

    level.id = id
    level.required_experience_points = required_exp

    return level
