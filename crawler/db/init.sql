CREATE TABLE website_articles (
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    publication_date DATE,
    category VARCHAR(100),
    crawler_execution_date DATE NOT NULL,
    crawler_execution_time TIME NOT NULL
);

-- Table for media (images and videos)
CREATE TABLE media (
    id SERIAL PRIMARY KEY,
    website_article_id INT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    description TEXT,
    FOREIGN KEY (website_article_id) REFERENCES website_articles(id) ON DELETE CASCADE
);