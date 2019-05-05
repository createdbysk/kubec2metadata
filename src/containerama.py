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

    def join_crew(self, container_id, role, ip):
        """
        The crew provides the actors their credentials to act. 
        Specify the ip address for the container, which provides the credentials for the 
        given role.

        :param container_id:        The id for the container that provides the credentials.
        :param role:                The role for which the container provides credentials.
        :param ip:                  The ip address of this container. This is required to allow the 
                                    actors that need credentials for this role to connect to this container.
        """
        raise NotImplementedError()