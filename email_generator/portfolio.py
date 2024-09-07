import pandas as pd
import chromadb
import uuid

from custom_logger import logger

class Portfolio:
    def __init__(self, file_path="data/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('data/vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")
        self.is_loaded = self.collection.count() > 0  # Check if collection already contains data

    def load_portfolio(self):
        if not self.is_loaded:
            logger.info("Loading portfolio into Chroma for the first time.")
            for _, row in self.data.iterrows():
                self.collection.add(documents=row["Techstack"],
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])
            self.is_loaded = True  # Set flag to True to indicate that data has been loaded
            logger.info("Portfolio loaded successfully.")
        else:
            logger.info("Portfolio already loaded. Skipping reloading.")

    def query_links(self, skills):
        logger.info("Querying links in Chroma")
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])

