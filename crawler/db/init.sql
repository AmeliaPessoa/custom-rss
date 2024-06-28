CREATE TABLE website (
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    inserted_at TIMESTAMP NOT NULL
);

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    website_id INT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    publication_date TIMESTAMP,
    author VARCHAR(100),
    description TEXT,
    categories VARCHAR(500),
    inserted_at TIMESTAMP NOT NULL,
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
