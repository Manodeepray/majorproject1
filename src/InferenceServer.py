import asyncio
import time
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from src.inference.processor import FastProcessor, LargeProcessor



from functools import partial

if not hasattr(asyncio , "to_thread"):
    async def to_thread(func , / ,*args , **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None , partial(func , *args , **kwargs))
    








# ------------------- Logging Setup -------------------
logger.add("inference.log", rotation="10 MB", backtrace=True, diagnose=True)

# ------------------- Metrics Setup -------------------
REQUEST_COUNT = Counter("inference_requests_total", "Total inference requests", ["model"])
REQUEST_LATENCY = Histogram("inference_request_latency_seconds", "Latency of inference requests", ["model"])

# ------------------- Tracing Setup -------------------
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",  # change if running remotely
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
tracer = trace.get_tracer(__name__)

# ------------------- FastAPI Init -------------------
app = FastAPI(title="Knowledge Graph Inference Server", version="1.0")
FastAPIInstrumentor.instrument_app(app)

# Initialize processors
fast_processor = FastProcessor()
large_processor = LargeProcessor()

# ------------------- Routes -------------------

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return JSONResponse(content=generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

@app.post("/infer")
async def infer(request: Request):
    """
    Regular inference (non-streaming)
    """
    body = await request.json()
    query = body.get("query")
    context = body.get("context", "")
    model = body.get("model", "fast")
    schema = body.get("schema")

    start_time = time.time()
    REQUEST_COUNT.labels(model=model).inc()

    try:
        with tracer.start_as_current_span(f"{model}_inference"):
            if model == "large":
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, large_processor.respond, query, context, schema)
                
            else:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, fast_processor.respond, query, context, schema)

    except Exception as e:
        logger.exception(e)
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        REQUEST_LATENCY.labels(model=model).observe(time.time() - start_time)
        logger.info(
            f"[INFER] model={model} query='{query[:60]}' latency={time.time()-start_time:.2f}s"
            )

    return {"result": result}


@app.post("/stream")
async def stream_infer(request: Request):
    """
    Stream inference response back to client
    """

    body = await request.json()
    query = body.get("query")
    context = body.get("context", "")
    model = body.get("model", "fast")

    processor = fast_processor if model == "fast" else large_processor

    async def token_stream():
        yield "[START STREAM]\n"
        with tracer.start_as_current_span(f"{model}_stream_inference"):
            for i in range(3):  # mock partial outputs; adapt for actual streaming APIs
                await asyncio.sleep(0.5)
                yield f"partial_response_chunk_{i}\n"
        yield "[END STREAM]\n"

    return StreamingResponse(token_stream(), media_type="text/plain")
