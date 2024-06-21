CREATE TABLE website (
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    execution_timestamp TIMESTAMP NOT NULL  -- Combina data e hora de execução do crawler
);

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    website_id INT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    publication_date DATE,
    author VARCHAR(100),
    description TEXT,
    categories VARCHAR(500),
    FOREIGN KEY (website_id) REFERENCES website(id) ON DELETE CASCADE
);

CREATE TABLE media (
    id SERIAL PRIMARY KEY,
    article_id INT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    title VARCHAR(500),
    description TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);
