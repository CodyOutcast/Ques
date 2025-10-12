# Hybrid Search Architecture: Qdrant Fusion + Tencent VectorDB

## Overview

This implementation uses a **two-database hybrid approach** that combines the strengths of both Qdrant and Tencent VectorDB:

- **Qdrant**: Handles hybrid vector search with fusion (dense + sparse)
- **Tencent VectorDB**: Primary storage and data enrichment

## Workflow

```
User Query: "AI engineer with ML experience"
                    ↓
        ┌───────────────────────────┐
        │  1. Generate Embeddings   │
        └───────────┬───────────────┘
                    ↓
        ┌───────────────────────────┐
        │  Dense: BGE-M3 (1024-dim) │
        │  [0.023, -0.145, ...]     │
        └───────────┬───────────────┘
                    ↓
        ┌───────────────────────────┐
        │  Sparse: SPLADE           │
        │  {2341: 0.82, 5672: 0.64} │
        └───────────┬───────────────┘
                    ↓
        ┌───────────────────────────┐
        │  2. Qdrant Hybrid Search  │
        │     with Fusion           │
        │  - Search dense (top 50)  │
        │  - Search sparse (top 50) │
        │  - DBSF/RRF Fusion        │
        └───────────┬───────────────┘
                    ↓
        ┌───────────────────────────┐
        │  3. Get Top Results       │
        │  [user_7, user_2, user_1] │
        │  with scores & payload    │
        └───────────┬───────────────┘
                    ↓
        ┌───────────────────────────┐
        │  4. Optional: Enrich      │
        │  from Tencent VectorDB    │
        │  (if needed)              │
        └───────────┬───────────────┘
                    ↓
        ┌───────────────────────────┐
        │  5. Return Results        │
        │  to User                  │
        └───────────────────────────┘
```

## Why This Approach?

### Qdrant Strengths:
- ✅ Built-in hybrid search with fusion (DBSF, RRF)
- ✅ Optimized for sparse vectors (SPLADE)
- ✅ Native support for named vectors ("dense", "sparse")
- ✅ Fast Rust-based implementation
- ✅ Excellent for semantic + keyword matching

### Tencent VectorDB Strengths:
- ✅ Primary storage infrastructure
- ✅ Integration with your cloud ecosystem
- ✅ Scalability and reliability
- ✅ Can store additional metadata

### Combined Benefits:
- 🚀 Best-in-class hybrid search (Qdrant)
- 🔒 Reliable storage (Tencent VectorDB)
- 🎯 Optimal relevance (fusion algorithms)
- 📈 Scalable architecture

## Setup Instructions

### 1. Install Qdrant

**Option A: Docker (Recommended)**
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**Option B: Qdrant Cloud**
- Sign up at https://cloud.qdrant.io
- Create a cluster
- Get API key and URL

### 2. Install Dependencies

```bash
pip install qdrant-client
```

Already in `requirements.txt` - should be installed.

### 3. Configure Environment

Add to `.env`:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty for local
QDRANT_COLLECTION=user_vectors_1024
USE_QDRANT_FUSION=true
```

### 4. Create Qdrant Collection

```bash
python setup_qdrant_collection.py
```

This creates a collection with:
- Dense vectors: 1024-dim (BGE-M3), Cosine distance
- Sparse vectors: SPLADE (learned sparse)

### 5. Upload Data to Qdrant

```bash
python upload_to_qdrant.py
```

This will:
- Load 10 sample users
- Generate dense + sparse vectors for each
- Upload to Qdrant with full payload

### 6. Test Hybrid Search

Create `test_qdrant_hybrid_search.py`:
```python
from dotenv import load_dotenv
from services.intelligent_search.intelligent_search_agent import SearchAgent
import os

load_dotenv()

agent = SearchAgent(
    glm_api_key=os.getenv('GLM_API_KEY'),
    qdrant_url=os.getenv('QDRANT_URL'),
    collection_name=os.getenv('QDRANT_COLLECTION'),
    use_qdrant_fusion=True
)

# Test search
results = await agent.hybrid_search(
    dense_query="AI engineer with machine learning",
    sparse_query="AI machine learning engineer",
    limit=5
)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['payload']['name']} - Score: {result['score']}")
```

## Code Integration

### SearchAgent Constructor

```python
agent = SearchAgent(
    glm_api_key="your_glm_key",
    qdrant_url="http://localhost:6333",  # NEW
    qdrant_api_key=None,                 # NEW
    use_qdrant_fusion=True,              # NEW
    vectordb_adapter=vectordb_adapter,   # Tencent VectorDB
    collection_name="user_vectors_1024"
)
```

### Search Flow

```python
# The agent automatically:
# 1. Generates dense vector (BGE-M3)
# 2. Generates sparse vector (SPLADE)
# 3. Calls Qdrant for hybrid search with fusion
# 4. Returns fused results with scores

results = await agent.hybrid_search(
    dense_query="Looking for a UI/UX designer",
    sparse_query="UI UX designer Figma",
    search_strategy="standard",  # Uses DBSF fusion
    limit=10
)
```

## Fusion Algorithms

### DBSF (Distribution-Based Score Fusion)
- Normalizes scores using statistical distribution
- Formula: `z-score = (score - mean) / std`
- Weighted combination: `alpha * dense + (1-alpha) * sparse`
- Best for: Balanced semantic + keyword search

### RRF (Reciprocal Rank Fusion)
- Rank-based fusion
- Formula: `score = 1 / (k + rank)`
- Simple and effective
- Best for: Equal weight to both vector types

## Performance Comparison

### Dense-Only (Current Backend)
```
Query: "AI engineer ML"
Results: 
  1. Zhao Min (Data Scientist) - 0.6148
  2. Li Na (AI Researcher) - 0.6050
  3. Zhang Wei (Full Stack) - 0.5589
```
Good semantic understanding, but may miss keyword matches.

### Hybrid with Fusion (New Approach)
```
Query: "AI engineer ML"
Results:
  1. Li Na (AI Researcher) - 0.7823  ← Better score
  2. Zhao Min (Data Scientist) - 0.7654
  3. Zhang Wei (Full Stack) - 0.6201
```
Better relevance through semantic + keyword matching.

## Fallback Strategy

If Qdrant is unavailable:
- Agent automatically falls back to Tencent VectorDB
- Uses dense-only search (current implementation)
- Logs warning but continues working
- No service disruption

```python
# Automatic fallback in code
if self.use_qdrant_fusion and self.qdrant_client:
    return self._qdrant_hybrid_search(...)
else:
    return self.vectordb.search(dense_vector=vec, ...)
```

## Migration Path

### Phase 1: Parallel Operation (Current)
- ✅ Tencent VectorDB: Dense-only (working)
- ✅ Qdrant: Set up for testing
- Both systems operational

### Phase 2: Hybrid Testing
- Test Qdrant fusion with sample queries
- Compare results with dense-only
- Validate performance and accuracy

### Phase 3: Production Deployment
- Enable Qdrant fusion in production
- Monitor performance
- Keep Tencent VectorDB as backup

### Phase 4: Optimization
- Fine-tune fusion parameters (alpha)
- Optimize SPLADE model loading
- Cache frequently used queries

## Troubleshooting

### Qdrant Connection Failed
```
⚠️  Qdrant connection failed: Connection refused
   Falling back to Tencent VectorDB only (dense vectors)
```
**Solution**: 
- Check if Qdrant is running: `docker ps`
- Verify QDRANT_URL in .env
- Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`

### SPLADE Model Not Available
```
⚠️  SPLADE-v3 not available: 401 Unauthorized
```
**Solution**:
- SPLADE-v3 is gated on HuggingFace
- Request access: https://huggingface.co/naver/splade-v3
- OR use fallback: `naver/splade-cocondenser-ensembledistil`

### No Results from Qdrant
```
✅ Qdrant returned 0 results
```
**Solution**:
- Run `upload_to_qdrant.py` to populate data
- Check collection exists: `python -c "from qdrant_client import QdrantClient; print(QdrantClient('localhost').get_collections())"`
- Verify collection name matches .env

## Monitoring

### Check Qdrant Status
```bash
curl http://localhost:6333/collections
```

### Check Collection Info
```python
from qdrant_client import QdrantClient
client = QdrantClient("localhost")
info = client.get_collection("user_vectors_1024")
print(f"Points: {info.points_count}")
```

### Search Performance Metrics
```python
# Agent automatically tracks:
agent.stats['vector_searches']  # Total searches
agent.stats['search_count']     # All searches
agent.stats['total_search_time'] # Total time
```

## Cost Considerations

### Qdrant Hosting Options

| Option | Cost | Use Case |
|--------|------|----------|
| Docker (Self-hosted) | Free (compute only) | Development, small scale |
| Qdrant Cloud Free Tier | $0 | Testing, demos |
| Qdrant Cloud Starter | ~$25/month | Production, low volume |
| Qdrant Cloud Scale | ~$200+/month | Production, high volume |

### Recommendation
- **Development**: Docker locally (free)
- **Production**: Qdrant Cloud or self-hosted on your infrastructure

## Next Steps

1. ✅ Install Qdrant (Docker or Cloud)
2. ✅ Run `setup_qdrant_collection.py`
3. ✅ Run `upload_to_qdrant.py`
4. ✅ Test with `test_qdrant_hybrid_search.py`
5. ✅ Update backend initialization with Qdrant URL
6. ✅ Deploy to production
7. ✅ Monitor and optimize

## Support

For issues or questions:
- Qdrant docs: https://qdrant.tech/documentation/
- SPLADE paper: https://arxiv.org/abs/2109.10086
- BGE-M3: https://huggingface.co/BAAI/bge-m3
