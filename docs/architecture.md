# Architecture

## TLDR;

## 1) Purpose

Production-ready, retrieval-augmented generation (RAG) chatbot on **Google Cloud**. Objectives:

* **Availability:** no single points of failure; graceful degradation if external APIs fail.
* **Scalability:** elastic compute, horizontal read capacity, and caching.
* **Cost efficiency:** serverless where possible, cache/short-circuit expensive LLM and search calls, right-size stateful services.

---

## 2) System at a Glance

**Two subsystems**

* **Data Ingestion (offline / batch):** prepare the knowledge base.
* **Serving (online / real-time):** answer user questions with RAG (documents + web search) and LLM.

**Key GCP services**

* **Vertex AI** (Text Embeddings + Gemini)
* **Cloud Storage** (staging)
* **Cloud SQL for PostgreSQL + pgvector** (vector store)
* **Cloud Run (FastAPI)** (stateless API)
* **Memorystore for Redis** (semantic/response cache)
* **External Web Search API** (fresh info)

---

## 3) What’s in the deployment diagram (current state)

**Data Ingestion (left box)**

1. Python notebook generates **embeddings** with **Vertex AI Embeddings**.
2. Embedding files uploaded to **Cloud Storage**.
3. A small import job loads embeddings into **Cloud SQL (pgvector)**.

**Serving (right box)**

1. **User → Cloud Run (FastAPI)** request.
2. Backend **embeds query** (Vertex AI) → **vector search** in **Cloud SQL (pgvector)**.
3. Optionally call **external web search API** for fresh context.
4. Build prompt (retrieved docs + web snippets) → **Vertex AI Gemini**.
5. Apply light post-processing / safety checks → **cache** response in **Memorystore (Redis)** → return to user.

---

## 4) Request flow (concise)

1. Receive request (Cloud Run).
2. Cache check (Redis) → hit = return.
3. Embed query (Vertex AI) → top-k semantic matches (pgvector).
4. Optional web search.
5. Compose prompt → Gemini generate.
6. Store in cache → respond.

---

## 5) Why these GCP services scale (and help availability & cost)

* **Cloud Run (FastAPI)**

  * *Scales to zero* when idle, *autoscale out* per traffic burst; managed HTTPS, revisions, health checks.
  * Regional, zonal diversity behind the service load-balancer; low ops overhead → lower TCO.

* **Vertex AI (Embeddings + Gemini)**

  * Fully managed inference; request-based autoscaling; latest model upgrades without infra work.
  * Pay-per-use; concurrency controls to cap spend.

* **Cloud SQL (PostgreSQL + pgvector)**

  * Familiar SQL + vector search; vertical scale up, read replicas for horizontal reads; automated backups/failover.
  * Good fit while corpus/query rate is moderate; switch path to **AlloyDB** for higher throughput/latency SLOs.

* **Cloud Storage**

  * Durable (11×9s), cheap, infinite capacity; decouples ingest from DB import.

* **Memorystore (Redis)**

  * Millisecond in-memory cache; reduces LLM and DB calls → **cuts latency & cost** dramatically on repeats.

---

## 6) Security & Observability on GCP (map from local → prod)

| Concern           | Local today        | Production recommendation (GCP)                                                   |
| ----------------- | ------------------ | --------------------------------------------------------------------------------- |
| Secrets           | `.env` files       | **Secret Manager** + per-service IAM; mount at runtime; rotate/versions           |
| Network           | Default egress     | **Serverless VPC Access**; private IP to Cloud SQL & Memorystore; restrict egress |
| AuthN/Z           | Ad-hoc             | **Identity-Aware Proxy** / API Gateway + JWT; Cloud Armor for WAF/rate-limit      |
| Logging           | Loguru             | **Cloud Logging** (structured JSON); log-based metrics & alerts                   |
| Metrics           | Prometheus/Grafana | **Cloud Monitoring** (PromQL support) + **Cloud Trace** + **Error Reporting**     |
| Keys/data at rest | N/A                | CMEK where needed; DB encryption defaults; Secrets/KMS for app keys               |

---

## 7) Gaps → Production-readiness plan

**Ingestion automation**

* Trigger: Cloud Storage → **Pub/Sub** → **Cloud Run Job** (or Cloud Functions) for parsing/chunking (Document AI if needed), embeddings (Vertex AI), **upsert to pgvector**.
* Benefit: continuous freshness, no manual steps.

**Quality & safety**

* Add **evaluation loop** (scheduled Cloud Run job): canned prompts → score with rubric/LLM-judge → store in **BigQuery**.
* Add **Responsible AI / moderation** before returning responses.

**Data & model lifecycle**

* Scheduled **re-embedding** on model change/new docs.
* Migrate to **AlloyDB** or **Vertex AI Matching Engine** if pgvector latency or scale becomes a bottleneck.

**SLOs & alerts**

* Define SLOs (e.g., p95 latency ≤ 1.5s; error rate < 1%).
* Alerts on: LLM errors, DB latency, cache miss rate spikes, cost anomalies.

**Delivery & infra**

* **CI/CD** (Cloud Build or GitHub Actions) → build, test, deploy to Cloud Run.
* **Terraform** for Cloud Run, SQL, Redis, secrets, policies (repeatable envs).

---

## 8) Cost levers

* Cache aggressively (Redis TTL + semantic keys).
* Cap LLM max tokens; prefer **retrieval quality** over larger generations.
* Right-size Cloud SQL; add read replicas only when needed.
* Use **Cloud Run concurrency** and min instances = 0 for dev/low-traffic.
* Log sampling for verbose traces.

---

## 9) Minimal runbook (operations)

* **Deploy:** CI/CD pipeline builds container, applies Terraform, deploys new revision to Cloud Run (gradual traffic split).
* **Secrets:** rotate quarterly via Secret Manager; no secrets in images.
* **Backups:** Cloud SQL automated backups + PITR; tested restore procedure.
* **Incidents:** dashboards (latency, errors, cache hit%), on-call alert policies, documented rollback (previous revision).
* **Data updates:** Storage drop → Pub/Sub → ingest job; monitor ingest queue lag.

---

## 10) Component summary

* **Frontend / Client**: calls Cloud Run REST.
* **API (Cloud Run, FastAPI)**: orchestrates RAG, handles auth, safety, caching.
* **Vector Store (Cloud SQL + pgvector)**: semantic retrieval, metadata filters.
* **Embeddings/LLM (Vertex AI)**: query/doc embeddings; Gemini generation.
* **Cache (Memorystore/Redis)**: response & embedding cache.
* **Staging (Cloud Storage)**: corpus & embedding artifacts.
* **Web Search**: external API for recency/coverage.

---

## 11) Migration checkpoints (current → prod)

1. Move secrets to **Secret Manager**; add private connectivity to SQL/Redis.
2. Turn on **Cloud Logging/Monitoring/Trace** with structured logs + dashboards + alerts.
3. Automate ingestion with **Pub/Sub + Cloud Run Job**; add idempotent upserts.
4. Add **evaluation pipeline** (BigQuery store) and **moderation** step.
5. Load test; if needed, migrate vector store to **AlloyDB** or **Matching Engine**.

This yields a secure, observable, autoscaling RAG backend that is cost-aware and straightforward to operate.


## High-Level Overview

This document provides a high-level overview of the chatbot backend architecture deployed on Google Cloud Platform (GCP). The system uses a retrieval-augmented generation (RAG) approach, which improves a large language model’s answers by grounding them on relevant external data sources. In practice, this means the application can fetch information from a document knowledge base and web search results, and feed those into an LLM to produce accurate, up-to-date responses.

**Subsystems**: The architecture is broadly divided into two main parts – a Data Ingestion pipeline and a Serving (query-handling) subsystem. The Data Ingestion side prepares domain documents (Tripitaka texts) for retrieval by generating and storing their vector embeddings. The Serving side handles live user queries: it retrieves relevant data via vector search (and web search API calls) and then invokes an LLM (Vertex AI’s Gemini model) to generate answers augmented with that data.

![plot](https://github.com/bladestery/fastapi-genai-boilerplate/tree/main/docs/poc_deployment.png)

Figure: Current RAG Chatbot Architecture (deployed on GCP). The Data Ingestion subsystem (left, green) involves offline embedding of Tripitaka documents using Vertex AI and storing the embeddings in a Cloud Storage bucket and CloudSQL database. The Serving subsystem (right, green) is a FastAPI backend on Cloud Run that accepts user queries, retrieves relevant document embeddings from CloudSQL (pgvector), calls an external web search API for latest information, and then invokes the Vertex AI Gemini LLM to generate a response. A Redis cache (Memorystore) is used to store recent query results for faster lookup on repeat queries. The user interacts via a frontend or API client which sends requests to the Cloud Run backend.

## Data Ingestion and Embedding Generation

The data ingestion pipeline prepares external knowledge (the Tripitaka documents) by converting them into vector embeddings that can be efficiently searched. Currently, this process is conducted manually (offline) and consists of the following steps:

1.	Embedding Generation: A Python notebook is used to call the Vertex AI Embeddings for Text API to generate vector embeddings for the Tripitaka documents. Each document (or document chunk) is transformed into a high-dimensional numeric vector representation that captures its semantic content. Using Vertex AI’s managed embedding model ensures high-quality embeddings without needing to train a model from scratch.

2.	Staging in Cloud Storage: The resulting embedding data (for all documents) is saved to a file and uploaded to a Google Cloud Storage bucket. Cloud Storage provides a scalable, cost-effective repository for large datasets (such as embedding files), with the benefit of high durability and virtually unlimited capacity. This staging step decouples the compute-intensive embedding generation from the database import, and also creates a persistent backup of the embeddings.

3.	Import to Vector Database: The embeddings file is then imported into a Cloud SQL for PostgreSQL database that has the pgvector extension enabled. Within Cloud SQL, a table stores the document vectors along with references to the original text. The pgvector extension allows efficient similarity search on these vectors using indexed nearest-neighbor queries. In other words, the Postgres database now acts as a vector store where we can find documents by semantic similarity to a query vector. This approach leverages a managed SQL database for vector search – benefiting from familiarity, consistency, and transactional support – while still enabling fast approximate lookups via pgvector math operations.

Using GCP managed services in this pipeline ensures scalability and reliability. For example, Cloud Storage is highly durable (with regional or multi-region replication for availability) and inexpensive for large volumes of data, which suits the need to store many embeddings. Cloud SQL provides a managed Postgres environment with automated backups and scaling options, simplifying operations. (At the current scale, Cloud SQL’s performance is sufficient; for larger-scale or latency-critical applications, one might consider AlloyDB for PostgreSQL – which offers the same pgvector interface with higher performance on analytical workloads.) The key outcome of the ingestion stage is that the system has a ready-to-use vector index of the documents, enabling semantic searches at query time.
Note: In the current implementation, the ingestion process is run manually. In a production scenario, this could be automated (see Production Readiness below) – for example, new documents uploaded to the Cloud Storage bucket could automatically trigger a pipeline (via Pub/Sub and Cloud Run jobs) to generate embeddings and update the database. This ensures the knowledge base stays current without manual intervention.

# Serving Subsystem: Retrieval and Response Generation

The serving subsystem is the online query-processing component. It is implemented as a FastAPI application running on Cloud Run, which provides a stateless, autoscaling backend for handling user requests. The service orchestrates the retrieval-augmented generation flow: it takes a user’s query, finds relevant contextual data (from the vector store and web search), and calls the LLM to produce a grounded answer. Below is the typical request/response flow:

1.	User Request: A user interacts with the system through a client (e.g. a chat UI or API call). The query (in natural language) is sent to the backend’s HTTP API endpoint. The Cloud Run service (FastAPI) receives the request and begins processing it. Because Cloud Run is serverless and can scale on demand, the backend can handle multiple concurrent users and will scale out if the request volume increases.

2.	Query Embedding: The backend first converts the incoming query from text into a vector embedding, using the same Vertex AI embedding model that was used during ingestion. This step is crucial: by representing the user’s question as a vector in the same semantic space as the document embeddings, the system can perform an accurate similarity search. (This uses Vertex AI’s embedding API behind the scenes, ensuring consistency in how text is vectorized for both queries and documents[2]. The embedding model and parameters must match those used for the knowledge base; using a different embedding model for queries versus documents would make the similarity search ineffective.) The result of this step is an embedding vector for the user’s query.

3.	Vector Database Retrieval: Next, the backend uses the query’s embedding vector to perform a semantic nearest-neighbor search in the CloudSQL vector store. A pgvector similarity query (e.g. cosine distance) is executed to find the top n document embeddings in the database that are closest to the query vector. These correspond to the most relevant pieces of content in the Tripitaka documents, based on semantic similarity. The database returns references (e.g. document IDs or passages) along with their similarity scores. This vector retrieval finds information related to the query’s meaning, even if the words don’t exactly match, enabling the system to surface context that a keyword search might miss. The retrieved document snippets (e.g. paragraphs from the scriptures) will be used to ground the LLM’s answer.

4.	External Web Search (optional): In parallel with the vector DB lookup, the backend may query an external Web Search API (such as a Google Programmable Search or Bing Web search API) if the query suggests that up-to-date or open-domain information is needed. For example, if the user’s question is not fully answered by the Tripitaka corpus (which is static), the system can call a web search service to fetch relevant recent information or broader context. This is an optional augmentation: it expands the knowledge available to the LLM by including current web results[1]. The web search results (e.g. top snippets or URLs) are collected by the backend, typically with some post-processing to extract text snippets.

5.	Prompt Construction: Once the relevant contextual data is gathered (from the vector store and possibly web search), the backend builds a prompt for the LLM. The prompt includes the user’s original question and the retrieved supporting information. For instance, the prompt might be constructed as a system message like: “Use the following context to answer the question…” followed by the content of the top documents and web snippets, and then the user’s query. This step essentially augments the user’s query with domain knowledge. By combining the query and retrieved text, we ensure the LLM is aware of the factual reference material when formulating its answer. (The backend may also truncate or prioritize context if there is too much data, to stay within the LLM’s token limit.)

6.	LLM Inference: The composed prompt is sent to the Vertex AI LLM endpoint (using the Vertex AI SDK or REST API). The model in use is Google’s Gemini LLM (via Vertex AI’s Generative AI service), which is a state-of-the-art foundation model. Vertex AI handles the scaling of this model behind an API, so the backend simply makes a request and receives a generated completion. The LLM reads the prompt (with the query and context) and produces a conversational answer. Thanks to the included context, the response should be relevant and grounded in the provided data. In other words, the model’s natural language generation is augmented by the retrieval step – improving factual accuracy and relevance. The use of Vertex AI for inference offloads the heavy computation of running an LLM to a managed service, and ensures we can leverage the latest model improvements (Gemini) without managing model servers. The FastAPI backend receives the LLM’s response (usually a few paragraphs of text answering the user’s question).

7.	Post-processing and Safety Checks: Before returning the LLM’s answer to the user, the backend can perform additional checks or transformations. For example, the system might run the answer through a Responsible AI filter (or moderation API) to detect and remove any disallowed content[3]. This step is recommended in production to ensure the chatbot doesn’t return harmful or sensitive information. Additionally, the backend might format the answer (e.g. adding citations if applicable, or adjusting markdown for the frontend). Any analytics events (for example, logging the prompt and response length, or capturing model latency) are recorded at this stage for monitoring.

8.	Caching and Response Delivery: The final answer is sent back to the user (frontend). Simultaneously, the system caches the result in Redis (Google Cloud Memorystore). The cache might store the question embedding or a normalized form of the question as the key, and the LLM answer (plus maybe retrieved context) as the value. On subsequent queries that are identical or very similar, the backend can skip the expensive retrieval + generation process and return the cached answer immediately if appropriate. This semantic caching strategy dramatically reduces latency and cost for repeated queries, as it avoids redundant calls to the Vertex LLM and database for questions the system has seen before. The Redis cache is stored in-memory, making lookups extremely fast (sub-millisecond), which improves the user experience for frequently asked questions. In addition to caching, the backend’s use of Loguru for logging means that each request/response is logged to the console (which in Cloud Run is captured by Cloud Logging by default). Metrics about the request (like query processing time, whether a cache was hit, etc.) are exposed via Prometheus (and visualized in Grafana), since the current setup includes a Prometheus/Grafana stack for observability. These logs and metrics allow developers to monitor usage patterns and system performance over time.

Overall, the serving workflow combines semantic retrieval with generative AI to deliver answers that are both knowledgeable and context-aware. The use of Cloud Run for the backend means it automatically scales with traffic and remains cost-efficient (scaling to zero instances when idle). By orchestrating calls to the database, external search, and Vertex AI, the backend integrates multiple services yet presents a single, unified API to the end user. The inclusion of a caching layer (Redis) further optimizes the system by trading off a small amount of memory storage for significant gains in speed and reduced API usage.

# GCP Services and Design Rationale

The current architecture leverages several GCP-managed services and technologies. Each was chosen for specific reasons related to scalability, cost-efficiency, and reliability:

•	Vertex AI (Embeddings & LLM): The system uses Vertex AI for both embedding generation and large-language model inference. Vertex AI’s embedding models (such as the text embedding API) provide high-quality vector representations out-of-the-box, saving us from building our own embedding model. Likewise, the Vertex AI Gemini LLM is accessed via a simple API call, and Google handles all the heavy lifting of model hosting and scaling. This choice greatly simplifies development and maintenance. It also ensures we can seamlessly upgrade to newer model versions (or fine-tune models) in the future via Vertex AI’s platform. In terms of scalability, Vertex AI will automatically allocate more resources behind the scenes as our requests increase, and we pay only for what we use (per embedding or per text generation). This managed ML approach means the team does not need to maintain custom ML servers or worry about uptime — it’s handled by GCP.

•	Cloud Storage: Google Cloud Storage is used to stage and store embedding files (and could also store raw documents). Cloud Storage is essentially “limitless” object storage with high durability (99.999999999% annual durability) and availability, which is ideal for large datasets like our document embeddings. It’s also very cost-effective for infrequently accessed data (we incur costs mainly for storage and egress, with no overhead for idle data). By using Cloud Storage as a middle layer in data ingestion, we decouple processing steps and have a permanent copy of the embeddings that can be re-used or re-imported as needed. Cloud Storage also integrates with other services (like Pub/Sub notifications or Dataflow) easily, which positions us to automate the pipeline later.

•	Cloud SQL (PostgreSQL with pgvector): The vector database is implemented on Cloud SQL, Google’s managed relational database service. We chose PostgreSQL for its robustness and familiarity, and enabled the pgvector extension to perform vector similarity searches. The benefit of Cloud SQL is that it’s fully managed: Google handles backups, updates, and failover for us. We can scale the instance (e.g., more vCPUs or RAM) as our data or query load grows, and even add read replicas for horizontal read scaling. Using a relational database also means we can store metadata along with vectors (e.g., document titles or IDs) and use SQL queries to filter or join, if needed. The pgvector capability allows queries like “find the nearest vectors to this query vector”, which is the core of our semantic search. While Cloud SQL handles our current workload well, for very large-scale similarity search or lower latency, we could migrate to AlloyDB, which is a PostgreSQL-compatible service optimized by Google for performance. AlloyDB can provide better throughput on vector searches and complex queries, at the cost of a slightly more involved setup and potentially higher cost – it’s an option as the application scales up.

•	Cloud Run (FastAPI Backend): Cloud Run is a serverless container platform that runs our FastAPI backend. The choice of Cloud Run is driven by its simplicity and scalability. We just deploy a Docker container and Cloud Run handles provisioning, autoscaling, and load balancing automatically. It can scale down to zero instances when no users are querying (meaning we incur no compute cost during idle periods), and it can quickly scale out to many instances if the traffic spikes, ensuring the application remains responsive. Cloud Run’s costs are granular (billed per CPU/Memory-second only while requests are being handled), which makes it cost-efficient for workloads with variable or unpredictable traffic. Additionally, Cloud Run abstracts away server management – we don’t need to manage VM instances or Kubernetes clusters, reducing operational overhead. It also integrates well with other GCP services (for example, it can easily connect to Cloud SQL via a VPC connector, and logs/metrics are automatically collected). The FastAPI application running on Cloud Run is stateless, which aligns perfectly with Cloud Run’s request-based ephemeral instances design. Overall, Cloud Run gives us a highly scalable and highly available application layer with minimal DevOps effort.

•	Memorystore for Redis (Caching): The architecture includes Redis (managed through Memorystore) as an in-memory cache to store frequently accessed results. Redis is known for its extremely low latency (in-memory data access) and simple key-value data model, which makes it ideal for caching API responses. By using a managed Redis (Memorystore), we get the benefits of Redis without having to maintain a VM – Google takes care of uptime and patching. The cache significantly speeds up repeated queries and reduces load on the LLM and database. For example, if multiple users ask the same question, the first query’s answer can be cached and subsequent ones can be served in milliseconds from Redis, avoiding expensive Vertex AI calls. This both improves user experience and lowers overall cost (since Vertex AI calls are one of the more expensive operations). Redis in this context is configured with an appropriate eviction policy (e.g., LRU or time-based eviction) to ensure it doesn’t grow without bound. In terms of scalability, Memorystore for Redis supports scaling up memory and a replica for high availability if needed. It’s important to note that caching is a best-effort performance optimization – the system is functional without it, but it greatly improves efficiency under load.

•	External Search API: Although not a GCP service, it’s worth mentioning that the integration of an external web search API is a design choice to enhance the system’s capabilities. We selected an API that provides reliable and fast search results (for example, the Google Custom Search JSON API or Bing Search API). The cost of using a search API is typically per request, so we use it judiciously (only when the internal knowledge base might not have sufficient information). The external search results broaden the scope of the chatbot’s knowledge beyond the documents we’ve embedded. This is crucial for handling queries about recent events or topics outside the Tripitaka documents. To keep things efficient, the system could also cache web search results (for a short time) or preprocess them similarly to document embeddings if they are repeatedly useful.

•	Observability & Telemetry: In the current setup, observability is handled by a combination of tools: the application uses Loguru for structured logging (which prints logs to stdout/stderr – and Cloud Run forwards these to Cloud Logging by default), and Prometheus/Grafana for metrics and monitoring. Prometheus scrapes metrics (if the FastAPI app exposes an endpoint or via sidecar), and Grafana displays dashboards for things like request latency, cache hits, etc. This choice was initially made to leverage existing open-source monitoring tools. However, GCP provides out-of-the-box logging and monitoring: Cloud Run automatically exports logs to Cloud Logging, and metrics can be collected in Cloud Monitoring (which supports Prometheus metrics integration as well). In the current design, the observability stack works, but it exists somewhat outside of GCP’s managed services. We discuss in the next section how this can be improved for production (using GCP’s Cloud Logging, Monitoring, and Trace for a more integrated solution).

Each of these components was chosen to maximize scalability (handle increasing load easily), cost-efficiency (pay as we go, avoid idle resource costs), and availability (managed services with high uptime SLAs). By using fully managed cloud services, the architecture minimizes the operational burden on developers and benefits from GCP’s reliability. In summary, the design favors a serverless, event-driven approach with powerful managed ML capabilities, which allows the team to focus on application logic rather than infrastructure.

# Production Readiness and Future Enhancements

While the current architecture is functional, several improvements are recommended to harden the system for production use. These enhancements focus on security, automation, observability, and maintainability, aligning the system with best practices:

•	Secure Secret Management: Replace the use of local .env files for sensitive configuration with Google Cloud Secret Manager. Secret Manager provides a central, encrypted store for API keys, database passwords, and other credentials. In a production environment, the Cloud Run service (and other services) can be granted access to specific secrets via IAM, and the secrets can be loaded as environment variables at runtime securely. This prevents secrets from being checked into code or configuration and ensures they are encrypted at rest and in transit. It also supports versioning and rotation of credentials without changing application code. By using Secret Manager, we adhere to the principle of least privilege and reduce the risk of secret leaks (for example, no plain-text secrets in logs or in the Cloud Run config).

•	Centralized Logging and Monitoring: Transition to using GCP’s native observability tools for a more integrated monitoring solution. Cloud Run automatically sends application logs to Cloud Logging, so we should take advantage of that by structuring log messages (in JSON) to be easily searchable and by setting up log-based metrics or alerts. Likewise, enable Cloud Monitoring to track metrics like request count, latency, error rates, and custom application metrics (Cloud Run provides some metrics out of the box, and we can push custom Prometheus metrics to Cloud Monitoring as well). This eliminates the need to run a separate Prometheus/Grafana stack and ensures that all telemetry is available on GCP with minimal setup[4]. We can configure alerts on key metrics (e.g., high error rate or slow response time) through Cloud Monitoring’s alerting policies. Additionally, integrating Cloud Trace and Error Reporting would help with diagnosing performance issues and catching exceptions in production. Overall, using Cloud Logging & Monitoring improves reliability – operators can quickly get insights and set up dashboards without maintaining separate infrastructure.

•	Automate the Ingestion Pipeline: As noted earlier, the document embedding process can be fully automated to handle new or updated data continuously. We suggest implementing an event-driven pipeline such as: when new documents or files are added to the Cloud Storage bucket, a Pub/Sub notification is emitted; a Cloud Run job or Cloud Function subscribed to that topic then picks up the event and processes the new data. This processing job could use Document AI for parsing complex file formats if needed, chunk the documents into smaller pieces, and then call the Vertex AI embedding API to vectorize them. The newly generated embeddings would be written to the CloudSQL (pgvector) database (or potentially to a separate temporary store, then merged). By automating ingestion in this way, the knowledge base stays up-to-date without manual intervention, allowing the chatbot to continually learn new information. It also enables near real-time updates – for instance, if we have a pipeline for user-provided content or frequent document releases. Such pipelines can be managed with tools like Cloud Composer (Airflow) or Workflows if the process gets more complex (multiple steps, error handling, etc.).

•	Continuous Model and Index Maintenance: Production systems should have a strategy for maintaining and updating the ML components. For our case, this includes the embeddings and the LLM. We should schedule periodic re-embedding of documents if the embedding model is updated or if new data accumulates. This could be done via a scheduled Cloud Run job or Cloud Composer DAG that re-processes the document corpus (for example, using an updated Vertex AI embedding model). On the LLM side, Vertex AI will automatically offer new versions of models (like updated Gemini models); we should regularly evaluate new model versions on sample queries and be prepared to switch to them for improved performance or cost. If we decide to fine-tune a model for our domain, we would incorporate that into Vertex AI’s training pipeline and host the fine-tuned model endpoint. Additionally, as the vector database grows in size, we should monitor query performance – if queries slow down, consider strategies like using an approximate nearest neighbor index (Annoy, FAISS, or Vertex AI Matching Engine) instead of pgvector for faster similarity search at scale. This can be introduced as a new service (e.g., Vertex Matching Engine) and would require an ingestion pipeline to populate that index. In short, orchestration of these maintenance tasks (data reprocessing, model updates, index rebuilding) is important. Utilizing infrastructure-as-code (Terraform or Deployment Manager) to manage schema changes or resource provisioning can also improve consistency across environments.

•	Quality Evaluation and Feedback Loop: Introduce a quality evaluation subsystem to continuously measure how well the chatbot is performing. In Google’s reference architecture, they set up a separate pipeline that periodically feeds evaluation prompts to the system and measures the responses. We can implement something similar: define a set of test questions (and possibly reference answers), and regularly run them through the system (perhaps using a scheduled Cloud Run job). The responses can then be evaluated either by automatic means (comparing to reference answers or using another LLM to judge correctness) or by human reviewers. We would collect metrics such as accuracy, relevancy, and completeness of answers. These evaluation results should be stored in a database or data warehouse (BigQuery) for analysis. Over time, this helps identify regressions or knowledge gaps. Additionally, we should capture user feedback from the live system – e.g., if the frontend allows users to rate answers or if we observe users rephrasing questions (indicating the first answer wasn’t good). This feedback loop can guide improvements: updating documents, fine-tuning the model, or adjusting the prompt template. Having a formal quality evaluation pipeline in production ensures the system maintains a high standard of response quality and factual accuracy as it evolves.

•	Enhanced Security and Compliance: As the system moves to production, we should tighten security on all fronts. For Cloud Run, ensure it’s running with a dedicated service account that has minimal permissions (e.g., just the ability to Cloud SQL and Secret Manager access, no broad project roles). Use VPC Service Connect or Serverless VPC Access for Cloud Run to talk to Cloud SQL and Memorystore over private IP, so that these services are not exposed over the public internet. Enforce HTTPS and authentication on the API endpoints (for example, using Identity-Aware Proxy or an API Gateway) if this is a user-facing service. Implementing rate limiting or quotas might be necessary to protect against abuse (Cloud Run can integrate with Cloud Armor or an API Gateway for this). Storing sensitive user data (if any) should be done in a secure manner (consider using Cloud KMS for any additional encryption needs). From a compliance perspective, enabling audit logging on GCP services and using tools like Cloud Audit Logs can track access to sensitive operations. We should also consider enabling Cloud Armor in front of the Cloud Run URL for basic DDoS and WAF protections if the service is public. In short, adopt the principle of defense-in-depth: cloud-native services like Secret Manager for secrets, proper IAM roles, network isolation, and security scans. These measures ensure the architecture not only scales but is robust against security threats and meets organizational compliance requirements.

•	Observability and SRE Practices: Building on the earlier observability point – in production, we’d unify on Cloud Logging and Monitoring, and possibly introduce more advanced practices. For instance, enable distributed tracing (Cloud Trace) to get latency breakdowns of the steps (DB query vs. LLM call vs. web search). Implement structured and semantic logging so that we can easily search logs (e.g., log a unique request ID across all components for a given request, to trace a query through the system). Set up dashboards in Cloud Monitoring for key metrics (cache hit rate, average LLM response time, vector search time, etc.), and define SLOs/SLAs for the service’s response time and uptime. Embrace an SRE mindset: error budgets, alerting on-call engineers if error rates go above a threshold, etc. Another improvement is to integrate Profiling (Cloud Profiler) if needed to optimize performance and Cloud Debugger for troubleshooting without downtime. These GCP tools can be very helpful once the system is at scale with many users.

•	CI/CD and Infrastructure as Code: To manage the architecture as it grows, we should invest in automation for deployment and configuration. Use a CI/CD pipeline (for example, Cloud Build or GitHub Actions) that automatically builds and tests the Docker image for the FastAPI service, and deploys it to Cloud Run on push to the main branch (after running unit/integration tests). This ensures quick and safe deployments. Manage infrastructure (Cloud Run service config, database instance, Redis instance, etc.) through declarative IaC templates – this makes it easier to reproduce the environment in different stages (dev/staging/prod) and to track changes in version control. For instance, Terraform scripts can define the Cloud SQL instance, including enabling pgvector, so that a new environment setup is one command away. Automated tests for the system (perhaps using simulated queries and checking responses) should be part of the pipeline to catch issues early. Embracing these software engineering best practices will make the system more maintainable and reduce the chance of human error during configuration changes or deployments.
By implementing the above enhancements, the chatbot backend will be more robust, secure, and maintainable, especially as usage grows. Many of these align with common production best practices and Google’s recommendations for cloud applications (e.g., managing secrets, using built-in logging, automating pipelines, etc.). In essence, these changes take the architecture from a proof-of-concept level to an enterprise-grade deployment.

# Comparison with Google’s Reference Architecture

To put the current design in context, we compare it with Google’s published RAG reference architecture for generative AI applications on GCP. The reference architecture (from Google’s documentation) illustrates an end-to-end, production-ready setup with additional subsystems and best practices:

![plot](https://github.com/bladestery/fastapi-genai-boilerplate/tree/main/docs/prod_deployment.png)

Figure: Google Cloud reference architecture for a RAG-capable generative AI application (high-level overview). This diagram (from Google’s Cloud Architecture Center) shows three subsystems – Data Ingestion, Serving, and Quality Evaluation – along with a shared database layer. Data ingestion is event-driven (Cloud Storage + Pub/Sub triggers) and uses services like Document AI and Vertex AI for processing incoming data into embeddings. The serving subsystem (right, green) includes a frontend, a backend, and calls to Vertex AI for LLM inference, similar to our design, but also highlights Responsible AI checks, logging to BigQuery/Cloud Logging, and Monitoring. The quality evaluation subsystem (bottom) continuously evaluates responses using stored evaluation prompts, with results stored for analysis. This reference model provides a blueprint for scaling and productionizing RAG applications on GCP.

Many aspects of our current architecture align with this reference design, but there are notable differences and potential improvements as outlined below:

•	Data Ingestion Pipeline: In the current architecture, document ingestion and embedding is a manual, offline process (run via a notebook and manual file upload). By contrast, the reference architecture implements an automated data ingestion subsystem. It uses Cloud Storage and Pub/Sub to automatically trigger processing when new data is available, and a Cloud Run job to handle parsing (with Document AI for OCR/formatting) and embedding generation. The processed embeddings are then stored directly into the vector database. This event-driven pipeline ensures continuous integration of new data and removes the need for human intervention. Moving to a similar model would greatly improve scalability and make it feasible to frequently update the knowledge base (the current design could adopt this by leveraging Pub/Sub and Cloud Run, as discussed). In summary, current vs. reference: manual one-time ingestion vs. automated, continuous ingestion pipeline.

•	Vector Store (Database): Our system uses Cloud SQL for PostgreSQL with pgvector as the vector store. The reference architecture uses AlloyDB for PostgreSQL for storing embeddings. Both are PostgreSQL-based and support pgvector, so functionally they are similar. The key difference is that AlloyDB is a Google-managed enhanced version of PostgreSQL that offers higher performance (especially for analytical and vector workloads) and better scalability for heavy workloads. Cloud SQL is perfectly adequate for moderate traffic and simpler use cases; AlloyDB would be considered in a production environment where query throughput is high or low-latency vector searches are critical. In practice, upgrading to AlloyDB is mostly a configuration change (loading data into AlloyDB and pointing the app to it) since the application code using pgvector remains the same. It’s worth noting that neither architecture uses a specialized vector database or Vertex Matching Engine – they rely on Postgres+pgvector for semantic search, which is sufficient for many applications. In production, if we anticipate scale issues, migrating to AlloyDB or even a dedicated vector service would be prudent, but at our current scale Cloud SQL is an acceptable choice.

•	LLM Serving and Prompting: Both the current and reference architectures use Vertex AI for LLM inference (e.g. calling a foundation model like PaLM or Gemini). The reference explicitly allows for either a foundation model or a custom fine-tuned model to be deployed on Vertex AI. Our current system uses the out-of-the-box Gemini model. In a production setting, we might experiment with fine-tuning or prompting techniques to improve domain-specific accuracy, which Vertex AI supports (through Model Garden or custom model endpoints). One subtle point: the reference architecture’s serving diagram shows a clear step of converting the user request to an embedding and doing semantic search, which we also do. It then combines results into a prompt and calls the LLM – again mirroring our flow. So conceptually, the Serving subsystem is quite aligned between current and reference designs. One addition in the reference is that it mentions writing prompts or user requests to BigQuery for analytics[4] – e.g., logging what users are asking and what the model responded, to allow offline analysis. Our current system doesn’t have this logging to BigQuery; we only log to console/Prometheus. For parity, we might consider logging interactions to BigQuery or another data store for long-term analysis and insight extraction (especially if we want to analyze trends or fine-tune the system later).

•	Caching Layer: The current architecture has a Redis cache deployed (Memorystore) to store recent query results. The Google reference architecture, as published, does not explicitly show a caching layer in the diagrams or description. This doesn’t mean caching isn’t applicable – rather, the reference focus is on core components, and caching is an optional optimization that system designers can add. In our case, we recognized the value of caching to improve latency and reduce cost, so we included Redis from the start. In a production scenario, implementing a cache is generally recommended if usage patterns include repetitive queries. It’s a straightforward addition: since our architecture already has it, we actually go beyond the reference here in terms of performance optimization. One just needs to ensure cache invalidation logic is in place if the underlying data changes (which ties into how frequently embeddings are updated).

•	Observability and Analytics: The reference architecture emphasizes using Cloud Logging, Cloud Monitoring, and BigQuery for observability. For example, it suggests storing prompts and responses in BigQuery for analysis, and using Cloud Logging for all application logs[4]. Our current implementation uses Loguru + Prometheus/Grafana which provides basic monitoring but isn’t as integrated. In a production-grade setup, we would shift to the Google approach: all logs to Cloud Logging (with proper metadata and severity levels) and monitoring via Cloud Monitoring dashboards or exported to BigQuery for deeper analysis. The difference is largely in convenience and depth: GCP’s tools can handle large scale logging and have powerful querying (Logs Explorer, BigQuery SQL for analytics), whereas our current approach might require manually managing a Prometheus server and has data retention limits. So, adopting the reference model’s observability stack would improve our ability to troubleshoot and optimize the system in production.

•	Secret & Configuration Management: Though not depicted in the reference diagram, Google best practices (and implicitly the reference architecture) would have Secret Manager and config management in place instead of plain environment variables. Our current system’s use of .env files is fine for local or test, but in production it’s a liability. In comparison, a production-ready setup uses Secret Manager, environment-specific config, and CI/CD pipelines to inject those secrets at deploy time. We have highlighted this in the improvements section. Essentially, moving to managed secrets and parameterizing deployments (no hard-coded secrets) is required to meet the bar set by Google’s exemplar architecture in terms of security.

•	Quality Evaluation Subsystem: One major component the reference architecture has (and ours lacks currently) is the Quality Evaluation subsystem. This is a parallel process where the system’s own answers are periodically evaluated for quality. In Google’s design, they store a set of evaluation prompts and expected outcomes in the database, then a Cloud Run evaluator job is triggered (say on a schedule or event) to generate answers for those prompts and score them (using either automated metrics or by comparison to reference answers), storing the results in BigQuery. The purpose is to continuously monitor metrics like factual accuracy, relevance, etc., and catch drifts or issues (for example, if a new model update decreases performance on certain queries). Our current architecture does not include anything like this – we rely on ad-hoc testing. For true production readiness, implementing such a subsystem (or at least periodically evaluating the model’s outputs) is very beneficial. It provides quantitative measures of the chatbot’s quality over time. As we progress, we plan to incorporate this, perhaps starting with a simple list of questions and using a secondary LLM to judge responses (RAG As a Self-Reviewer approach) or human review for critical queries, and then expand it.

•	Responsible AI and Safety: The reference design explicitly shows a “Responsible AI checks” step in the serving flow[3]. This indicates using content filters or moderation to ensure the LLM’s output adheres to guidelines (no profanity, hate speech, privacy violations, etc.). In our current implementation, we haven’t integrated a specific content moderation step yet. We rely on the fact that Vertex AI’s Gemini model has some built-in moderation, but a dedicated step would give more control. In a production environment, we would adopt this practice – for instance, using Vertex AI’s moderation endpoint or a third-party content filter on the LLM output before delivering it to users. This helps in mitigating risks associated with generative AI (like the model producing inappropriate or biased content). Additionally, rate limiting and user authentication (to prevent misuse of the service) tie into responsible usage – these are not illustrated in the Google diagram but are implied in a secure deployment.

•	Cost Considerations: While not immediately visible in architecture diagrams, a production-ready design also optimizes for cost at scale. Our current architecture, being largely serverless and pay-per-use, is already cost-conscious (Cloud Run, Cloud Storage incur minimal costs when idle; Cloud SQL and Redis are the only steady cost components). The Google exemplar pattern similarly uses serverless components (Cloud Run jobs, etc.). One difference is that the reference suggests additional services like Document AI and BigQuery which add cost but provide value (automated document processing, powerful analytics). In an enterprise setting, those costs are justified by the benefits (e.g., easier data ingestion, deeper insights from analytics). We have to plan capacity (like sizing the Cloud SQL instance appropriately, enabling Redis with sufficient memory but not over-provisioning, etc.) and possibly implement cost monitoring (BigQuery can be used to analyze Vertex AI usage costs, for example). Google’s architecture implicitly assumes monitoring of usage and implementing caching (which we have) to cut down on expensive calls. So in effect, our design is aligned on cost strategy, with caching as a cost saver, and we would add more monitoring to ensure the cost stays within acceptable bounds.

**Summary**: The current architecture covers the fundamental components needed for a RAG chatbot (document store with pgvector, retrieval logic, LLM invocation, caching, etc.) and is largely consistent with Google’s reference vision in the Serving subsystem. The differences are mainly in the surrounding capabilities – automation of data ingestion, enhanced monitoring, evaluation, and some security practices – which we have identified and planned to improve. By evolving the current system to incorporate these elements, we will move closer to the reference architecture’s production-ready state. This means a more automated, robust pipeline (new data flows in seamlessly), better introspection of system performance (logs/metrics/analytics), continuous quality control, and strong security guardrails. These changes will enable the chatbot to scale to larger workloads and be maintained reliably over time, while ensuring users continue to receive accurate and timely answers grounded in the latest data.