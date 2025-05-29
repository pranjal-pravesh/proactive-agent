import os
import json
import time
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'memory')
MEMORY_TXT = os.path.join(MEMORY_DIR, 'memory.txt')
MEMORY_JSON = os.path.join(MEMORY_DIR, 'memory.json')
FAISS_INDEX = os.path.join(MEMORY_DIR, 'memory.index')
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

os.makedirs(MEMORY_DIR, exist_ok=True)

class MemoryStore:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.metadata = []
        self.index = None
        self.dim = 384  # all-MiniLM-L6-v2 output dim
        self._load()

    def _load(self):
        # Load metadata
        if os.path.exists(MEMORY_JSON):
            with open(MEMORY_JSON, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []
        # Load FAISS index
        if os.path.exists(FAISS_INDEX):
            self.index = faiss.read_index(FAISS_INDEX)
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            # If metadata exists but no index, rebuild
            if self.metadata:
                embeddings = np.array([m['embedding'] for m in self.metadata]).astype('float32')
                self.index.add(embeddings)

    def _save(self):
        faiss.write_index(self.index, FAISS_INDEX)
        with open(MEMORY_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_to_knowledge_base(self, text: str, metadata: Dict[str, Any]):
        # Embed
        embedding = self.model.encode(text)
        embedding = embedding.astype('float32')
        # Add to FAISS
        self.index.add(np.expand_dims(embedding, 0))
        # Add to metadata
        entry = {
            'timestamp': metadata.get('timestamp', time.time()),
            'text': text,
            'tags': metadata.get('tags', []),
            'embedding': embedding.tolist()
        }
        self.metadata.append(entry)
        # Save
        self._save()
        # Append to readable memory.txt
        with open(MEMORY_TXT, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['timestamp']))}] {text}\n")

    def retrieve_context(self, query: str, k: int = 5) -> List[str]:
        if not self.metadata or self.index.ntotal == 0:
            return []
        query_emb = self.model.encode(query).astype('float32')
        D, I = self.index.search(np.expand_dims(query_emb, 0), k)
        results = []
        for idx in I[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx]['text'])
        return results

# Singleton instance
memory_store = MemoryStore()

def add_to_knowledge_base(text, metadata):
    memory_store.add_to_knowledge_base(text, metadata)

def retrieve_context(query, k=5):
    return memory_store.retrieve_context(query, k) 