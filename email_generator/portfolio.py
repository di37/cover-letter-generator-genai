import os

import pandas as pd
import chromadb
import uuid

from custom_logger import logger


class Portfolio:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.chroma_client = chromadb.PersistentClient(
            os.path.join(data_dir, "vectorstore")
        )
        self.collections = {}

    def load_portfolio(self, file_name=None, df=None):
        if file_name is None and df is None:
            raise ValueError("Either file_name or df must be provided")

        if file_name:
            file_path = os.path.join(self.data_dir, file_name)
            collection_name = os.path.splitext(file_name)[0]
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found")
            df = pd.read_csv(file_path)
        else:
            collection_name = "temp_collection"

        # Check if collection exists
        existing_collections = self.chroma_client.list_collections()
        if any(
            collection.name == collection_name for collection in existing_collections
        ):
            # Delete the existing collection
            self.chroma_client.delete_collection(name=collection_name)
            logger.info(f"Existing collection '{collection_name}' deleted.")

        # Create a new collection
        collection = self.chroma_client.create_collection(name=collection_name)

        logger.info(f"Loading portfolio '{collection_name}' into Chroma.")
        for _, row in df.iterrows():
            collection.add(
                documents=row["Techstack"],
                metadatas={"links": row["Links"]},
                ids=[str(uuid.uuid4())],
            )

        self.collections[collection_name] = collection
        logger.info(f"Portfolio '{collection_name}' loaded successfully.")

    def query_links(self, skills, collection_name=None):
        if collection_name is None and len(self.collections) == 1:
            collection = next(iter(self.collections.values()))
        elif collection_name in self.collections:
            collection = self.collections[collection_name]
        else:
            raise ValueError(f"Collection '{collection_name}' not found")

        logger.info(f"Querying links in collection '{collection.name}'")
        return collection.query(query_texts=skills, n_results=2).get("metadatas", [])

    def list_portfolios(self):
        return list(self.collections.keys())


portfolio = Portfolio()
