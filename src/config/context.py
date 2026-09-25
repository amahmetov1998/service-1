from sqlalchemy.ext.asyncio import AsyncSession

from .unit_of_work import UnitOfWork, RepositoryFactory


class UserContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.users = repo_factory.user(uow.session)
        self.phones = repo_factory.phone(uow.session)


class NotificationContext:
    def __init__(self, session: AsyncSession, repo_factory: RepositoryFactory):
        self.session = session
        self.users = repo_factory.user(session)
        self.notifications = repo_factory.notification(session)
        self.events = repo_factory.outbox_event(session)


class HTTPWorkerContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.users = repo_factory.user(uow.session)


class BrokerWorkerContext:
    def __init__(self, uow: UnitOfWork, repo_factory: RepositoryFactory):
        self.uow = uow
        self.events = repo_factory.outbox_event(uow.session)
