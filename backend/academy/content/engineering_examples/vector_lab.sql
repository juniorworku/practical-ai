-- Dedicated synthetic lab database only. 3D vectors are labeled fixtures,
-- not real text embeddings. Change the schema/dimension for your chosen model.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS engineering_chunks (
 id text PRIMARY KEY, owner_id text NOT NULL, source_revision text NOT NULL,
 locator text NOT NULL, body text NOT NULL, embedding vector(3) NOT NULL,
 embedding_model text NOT NULL,
 search tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED
);
CREATE INDEX IF NOT EXISTS engineering_chunks_scope ON engineering_chunks(owner_id,source_revision);
CREATE INDEX IF NOT EXISTS engineering_chunks_text ON engineering_chunks USING gin(search);
INSERT INTO engineering_chunks(id,owner_id,source_revision,locator,body,embedding,embedding_model) VALUES
 ('acme-returns','acme','v1','page:1','Unopened items within 14 days. Opened excluded.','[1,0,0]','fixture-v1'),
 ('other-returns','other','v1','page:1','Private policy for another owner.','[1,0,0]','fixture-v1'),
 ('acme-shipping','acme','v1','time:00:01-->00:04','Shipping takes five days.','[0,1,0]','fixture-v1')
 ON CONFLICT (id) DO NOTHING;
-- Production parameters come from authenticated server state, never a prompt.
SELECT id, locator, body FROM engineering_chunks
 WHERE owner_id='acme' AND source_revision='v1' AND embedding_model='fixture-v1'
 ORDER BY embedding <=> '[1,0,0]'::vector, id LIMIT 2;
SELECT id, ts_rank_cd(search,plainto_tsquery('english','unopened items')) AS lexical_score
 FROM engineering_chunks WHERE owner_id='acme' AND source_revision='v1'
 AND search @@ plainto_tsquery('english','unopened items') ORDER BY lexical_score DESC,id LIMIT 5;
-- Compare exact search above to ANN on a representative larger dataset;
-- do not infer recall/index speed from these three rows.
CREATE INDEX IF NOT EXISTS engineering_chunks_ann ON engineering_chunks USING hnsw (embedding vector_cosine_ops);
