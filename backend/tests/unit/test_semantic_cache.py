import pytest
from app.cache.cache_policy import CachePolicy
from app.cache.embeddings import cosine_similarity, generate_embedding
from app.cache.semantic_cache import SemanticCacheManager
from app.schemas.request import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession


def test_embeddings_and_cosine_similarity():
    v1 = generate_embedding("What is machine learning?")
    v2 = generate_embedding("What is machine learning?")
    # Identical texts must have similarity 1.0
    assert cosine_similarity(v1, v2) == 1.0

    # Similar queries
    v3 = generate_embedding("Explain machine learning")
    sim = cosine_similarity(v1, v3)
    assert sim > 0.50

    # Completely different queries
    v_diff = generate_embedding("Recipe for chocolate cake with sugar")
    sim_diff = cosine_similarity(v1, v_diff)
    assert sim_diff < 0.45


@pytest.mark.asyncio
async def test_semantic_cache_store_and_lookup(db_session: AsyncSession, test_app_and_org):
    app, _ = test_app_and_org
    cache_mgr = SemanticCacheManager()
    policy = CachePolicy(enabled=True, similarity_threshold=0.85)

    messages = [ChatMessage(role="user", content="Explain artificial intelligence in simple terms.")]
    response_text = "Artificial Intelligence (AI) refers to systems that mimic human intelligence."

    # 1. Initially cache miss
    res1 = await cache_mgr.lookup(
        application_id=app.id,
        organization_id=app.organization_id,
        messages=messages,
        policy=policy,
        db=db_session,
    )
    assert res1.hit is False

    # 2. Store response
    await cache_mgr.store(
        application_id=app.id,
        organization_id=app.organization_id,
        messages=messages,
        response_content=response_text,
        model="gpt-4o-mini",
        policy=policy,
        db=db_session,
        tokens_saved=30,
    )

    # 3. Exact query hit
    res2 = await cache_mgr.lookup(
        application_id=app.id,
        organization_id=app.organization_id,
        messages=messages,
        policy=policy,
        db=db_session,
    )
    assert res2.hit is True
    assert res2.response_content == response_text
    assert res2.similarity_score >= 0.99

    # 4. Cross-tenant isolation check: different application_id cannot see cache
    res_other_app = await cache_mgr.lookup(
        application_id="app_other_tenant",
        organization_id="org_other",
        messages=messages,
        policy=policy,
        db=db_session,
    )
    assert res_other_app.hit is False
