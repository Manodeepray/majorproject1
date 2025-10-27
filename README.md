
use python >3.10

### RUN

in sequence

terminal1

```bash
source .env;
source .venv/bin/activate;
python3 -m uvicorn src.InferenceServer:app --host 0.0.0.0 --port 8000 --reload
```

terminal2

```bash
source .env;
source .venv/bin/activate;
python3 -m uvicorn src.server:app --host 0.0.0.0 --port 8001 --reload
```

terminal3

```bash
source .env;
source .venv/bin/activate;
python3 -m test
```


=====================================================================================



---done---


1. create the inference engine

    FastAPI + asyncio (serving, async requests, streaming).

    Loguru (developer-friendly logs).

    Prometheus + Grafana (metrics).

    OpenTelemetry + Jaeger (tracing).

2. data ingestion
    pdfs , docs , etc
    

3. data processing

    3.1 chunking , processing , tracing     
    
    3.2 vector embeddings
         convert to dense vector embeddings

    3.3 add to the vector database


    3.4 build  the vector stores
        then to vector stores-- hnsw + faiss

    
4. retrieval  

    Hierarchical Navigable Small Worlds (HNSW) search +   Faiss vector similarity search 

---done---


=========================================================================================



---todo---



batch inference
add watchdog for additional files
make upload endpoint database.py
fix inference token limit ...or chunk idk
implement hkg graph creation for display from retrieved data
retrieved docs to kg


5. Knowledge graph

    5.1 extract entity - relations
        then fast processor for entitiy-relationship recognition 
        then large processor for etc etc
    
    5.2 compile 
        e and r and e-r --> *.jsons

    5.3 build hkg
        clean redundant e , r , e-r
        build hkg/kg
    
    5.4 kg per query
        extract e and r and er from per doc
        gen kg

6. Prompt engine 
    re write , breakdown , reranker , feedback loop , editable context 


7. track performance


8. add safety 

9. prepare evaluation pipeline

10. memory + context engineering


---todo---

=========================================================================================
--- plan and implement---

health checks

query -- rerankers , query re write/breakdown  , feedback loops 
 
performance -- prompt caching , canary rollouts , rollback plans ,ci/cd , cost latency throughput

safety -- guard rails , prompt injection & jail break defence 

evaluation --

memory -- vector + grapg + episodic , pruning... memory policy ,  context chaining ,memory pruning

--- plan and implement---



https://chatgpt.com/c/68ec1ba2-7728-8323-be9e-6e52f2245aaa


