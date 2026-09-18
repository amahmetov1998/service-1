import functools
import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaTimeoutError,
    RequestTimedOutError,
)

from src.exceptions import BrokerUnavailableError
from src.schemas import IdempotencyHeaders, OutboxEventSchema

log = logging.getLogger(__name__)


def handle_transport_errors(request_func):
    @functools.wraps(request_func)
    async def wrapper(*args, **kwargs):
        try:
            return await request_func(*args, **kwargs)
        except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError) as e:
            log.warning(
                "Broker not available. Error type=%s, error=%s", type(e).__name__, e
            )
            raise BrokerUnavailableError("Broker unavailable")

    return wrapper


class ServiceBroker:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    @handle_transport_errors
    async def send_and_wait_ack(
        self, headers: IdempotencyHeaders, topic_name: str, event: OutboxEventSchema
    ) -> None:
        await self.producer.send_and_wait(
            headers=[("Idempotency-Key", headers.idempotency_key.encode())],
            topic=topic_name,
            value=event.model_dump(mode="json"),
        )
