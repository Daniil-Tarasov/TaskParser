ALTER TABLE problems ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';

CREATE INDEX IF NOT EXISTS ix_problems_tags ON problem_tags(tag);
CREATE INDEX IF NOT EXISTS ix_problems_rating ON problems(rating) WHERE rating IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_problems_cf_id ON problems(codeforces_id);

-- Тест тегов
DO $$
BEGIN
    UPDATE problems SET tags = ARRAY['test','easy'] WHERE codeforces_id LIKE '%A';
    UPDATE problems SET tags = ARRAY['math','graphs'] WHERE codeforces_id LIKE '%Cherry%';
END $$;

-- Проверка
SELECT codeforces_id, name, rating, tags FROM problems LIMIT 3;