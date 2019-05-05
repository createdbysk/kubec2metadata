import pytraits

class Containerama(object, metaclass=pytraits.Singleton):
    """
    Provides containers the ability to act correctly based on their role.
    """
    def join_cast(self, container_id, role):
        """
        Join a container as an actor with a role. 
        A container can join multiple times. The latest role wins.
        Multiple actors are allowed to have the same role.

        :param container_id:        The id for the container.
        :param role:                The role for the container.
        :
        """
        raise NotImplementedError()
