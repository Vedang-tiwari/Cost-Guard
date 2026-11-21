from datetime import UTC, datetime

from app.cache.cache_keys import generate_cache_key
from app.cache.cache_policy import CachePolicy, compute_expiration
from app.cache.embeddings import cosine_similarity, generate_embedding
from app.database.models.cache_entry import CacheEntry
from app.schemas.request import ChatMessage
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CacheLookupResult(BaseModel):
    hit: bool = False
    response_content: str | None = None
    model: str | None = None
    similarity_score: float = 0.0
    matched_entry_id: str | None = None
    tokens_saved: int = 0


class SemanticCacheManager:
    """Manages semantic similarity caching and deterministic key caching."""

    async def lookup(
        self,
        application_id: str,
        organization_id: str,
        messages: list[ChatMessage],
        policy: CachePolicy,
        db: AsyncSession,
    ) -> CacheLookupResult:
        now = datetime.now(UTC)
        exact_key = generate_cache_key(application_id=application_id, messages=messages)

        # 1. Check exact key match first
        exact_stmt = select(CacheEntry).where(
            CacheEntry.application_id == application_id,
            CacheEntry.cache_key == exact_key,
            CacheEntry.expires_at > now,
        ).limit(1)
        res = await db.execute(exact_stmt)
        exact_match = res.scalar_one_or_none()

        if exact_match:
            return CacheLookupResult(
                hit=True,
                response_content=exact_match.response_content,
                model=exact_match.model,
                similarity_score=1.0,
                matched_entry_id=exact_match.id,
                tokens_saved=int(exact_match.tokens_saved),
            )

        # 2. Semantic vector similarity search
        query_text = " ".join([m.content for m in messages if m.role == "user"])
        if not query_text:
            return CacheLookupResult(hit=False)

        query_vec = generate_embedding(query_text)

        # Fetch recent unexpired cache entries in this application namespace
        semantic_stmt = select(CacheEntry).where(
            CacheEntry.application_id == application_id,
            CacheEntry.expires_at > now,
        ).order_by(CacheEntry.created_at.desc()).limit(100)

        candidates_res = await db.execute(semantic_stmt)
        candidates = candidates_res.scalars().all()

        best_entry: CacheEntry | None = None
        best_similarity: float = 0.0

        for candidate in candidates:
            if not candidate.embedding:
                continue
            sim = cosine_similarity(query_vec, candidate.embedding)
            if sim > best_similarity:
                best_similarity = sim
                best_entry = candidate

        if best_entry and best_similarity >= policy.similarity_threshold:
            return CacheLookupResult(
                hit=True,
                response_content=best_entry.response_content,
                model=best_entry.model,
                similarity_score=best_similarity,
                matched_entry_id=best_entry.id,
                tokens_saved=int(best_entry.tokens_saved),
            )

        return CacheLookupResult(hit=False, similarity_score=best_similarity)

    async def store(
        self,
        application_id: str,
        organization_id: str,
        messages: list[ChatMessage],
        response_content: str,
        model: str,
        policy: CachePolicy,
        db: AsyncSession,
        tokens_saved: int = 0,
    ) -> CacheEntry:
        query_text = " ".join([m.content for m in messages if m.role == "user"])
        cache_key = generate_cache_key(application_id=application_id, messages=messages)
        embedding = generate_embedding(query_text)
        expires_at = compute_expiration(policy.ttl_seconds)

        entry = CacheEntry(
            application_id=application_id,
            organization_id=organization_id,
            cache_key=cache_key,
            embedding=embedding,
            query_text=query_text,
            response_content=response_content,
            model=model,
            tokens_saved=tokens_saved,
            expires_at=expires_at,
        )
        db.add(entry)
        await db.commit()
        return entry


_cache_instance: SemanticCacheManager | None = None


def get_semantic_cache() -> SemanticCacheManager:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SemanticCacheManager()
    return _cache_instance
