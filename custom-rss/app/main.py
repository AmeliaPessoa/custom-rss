from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/custom-rss")
def custom_rss(data_source: str):
  xml_data = """
    <rss version="2.0">
        <channel>
            <title>Exemplo RSS</title>
            <link>http://www.example.com</link>
            <description>Exemplo de RSS</description>
            <item>
                <title>Item 1</title>
                <description>Descrição do item 1</description>
            </item>
            <item>
                <title>Item 2</title>
                <description>Descrição do item 2</description>
            </item>
        </channel>
    </rss>
    """
  response = Response(content=xml_data, media_type="application/xml")
  return response