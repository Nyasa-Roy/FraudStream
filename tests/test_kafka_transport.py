from types import SimpleNamespace

from fraudstream_producer import Transaction, TransactionGenerator
from fraudstream_producer.publisher import TransactionPublisher
from fraudstream_processor.worker import TransactionWorker


class FakeProducer:
    def __init__(self):
        self.messages = []

    def send(self, topic, **kwargs):
        self.messages.append((topic, kwargs))
        return "future"

    def flush(self):
        pass

    def close(self):
        pass


class FakeConsumer:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


def test_publisher_serializes_transaction_event():
    transaction = next(TransactionGenerator(seed=4).generate(1))
    producer = FakeProducer()
    publisher = TransactionPublisher(producer=producer)
    publisher.publish(transaction)
    assert producer.messages[0][0] == "transactions"
    assert producer.messages[0][1]["key"] == transaction.transaction_id
    assert producer.messages[0][1]["value"]["amount"] == transaction.amount


def test_worker_processes_valid_event_and_commits():
    transaction = next(TransactionGenerator(seed=4).generate(1))
    consumer = FakeConsumer()
    processed = []
    worker = TransactionWorker(processed.append, consumer=consumer)
    assert worker.handle(SimpleNamespace(value=transaction.as_event())) is True
    assert processed[0].transaction_id == transaction.transaction_id
    assert consumer.commits == 1


def test_worker_drops_invalid_event_without_processing():
    consumer = FakeConsumer()
    processed = []
    worker = TransactionWorker(processed.append, consumer=consumer)
    assert worker.handle(SimpleNamespace(value={"amount": -1})) is False
    assert processed == []
    assert consumer.commits == 1

