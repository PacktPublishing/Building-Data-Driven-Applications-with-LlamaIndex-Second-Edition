import llama_index.core.instrumentation as instrument
import models_config
from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.instrumentation.event_handlers import BaseEventHandler
from llama_index.core.instrumentation.events import BaseEvent

class SimpleEventHandler(BaseEventHandler):
    @classmethod
    def class_name(cls):
        return "SimpleEventHandler"

    def handle(self, event: BaseEvent, **kwargs):
        print(f"Event: {event.class_name()}")
        print(f"  Span ID: {event.span_id}")
        print()

span_handler = SimpleSpanHandler()
dispatcher = instrument.get_dispatcher()
dispatcher.add_span_handler(span_handler)
event_handler = SimpleEventHandler()
dispatcher.add_event_handler(event_handler)

documents = SimpleDirectoryReader('files').load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What are the main obligations of the supplier?")
print(response)

for span in span_handler.completed_spans:
    print(f"Span: {span.id_}"  )
    print(f"  Parent: {span.parent_id}")
    print(f"  Duration: {span.duration}")
    print(f"  Tags: {span.tags}")
    print()

