class EntityProcessingError(Exception):
    pass


class EntityNotFoundError(EntityProcessingError):
    pass


class EntityCreationError(EntityProcessingError):
    pass


class EntityUpdateError(EntityProcessingError):
    pass


class AddStakeholderError(Exception):
    pass
