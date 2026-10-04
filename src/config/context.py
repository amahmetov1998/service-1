from .unit_of_work import UnitOfWork, RepositoryFactory


class UserContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.users = repo_factory.user(uow.session)
        self.phones = repo_factory.phone(uow.session)


class HTTPWorkerContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.users = repo_factory.user(uow.session)


class BrokerWorkerContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.events = repo_factory.outbox_event(uow.session)
