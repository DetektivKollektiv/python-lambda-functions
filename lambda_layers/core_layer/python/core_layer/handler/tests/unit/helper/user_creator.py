from core_layer.model import User, Level


def create_user(id: int, level: Level, exp=None, name=None) -> User:
    user = User()

    user.id = id
    user.level = level
    user.name = name
    if exp == None:
        user.experience_points = level.required_experience_points
    else:
        if exp >= level.required_experience_points:
            user.experience_points = exp
        else:
            raise Exception(
                "Exp must be equal or greater than required exp of the defined level")

    return user
