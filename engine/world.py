from world.rooms import Room, build_rooms


def create_world() -> dict[str, Room]:
    return build_rooms()
