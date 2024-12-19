from sentence_transformers import SentenceTransformer
import pandas as pd

class Model:
    def __init__(self):
        self.model = None
        self.model_list = pd.DataFrame([
            'all-mpnet-base-v2,69.57,57.02,63.30,2800,420 MB'.split(","),
            'multi-qa-mpnet-base-dot-v1,66.76,57.60,62.18,2800,420 MB'.split(","),
            'all-distilroberta-v1,68.73,50.94,59.84,4000,290 MB'.split(","),
            'all-MiniLM-L12-v2,68.70,50.82,59.76,7500,120 MB'.split(","),
            'multi-qa-distilbert-cos-v1,65.98,52.83,59.41,4000,250 MB'.split(","),
            'all-MiniLM-L6-v2,68.06,49.54,58.80,14200,80 MB'.split(","),
            'multi-qa-MiniLM-L6-cos-v1,64.33,51.83,58.08,14200,80 MB'.split(","),
            'paraphrase-multilingual-mpnet-base-v2,65.83,41.68,53.75,2500,970 MB'.split(","),
            'paraphrase-albert-small-v2,64.46,40.04,52.25,5000,43 MB'.split(","),
            'paraphrase-multilingual-MiniLM-L12-v2,64.25,39.19,51.72,7500,420 MB'.split(","),
            'paraphrase-MiniLM-L3-v2,62.29,39.19,50.74,19000,61 MB'.split(","),
            'distiluse-base-multilingual-cased-v1,61.30,29.87,45.59,4000,480 MB'.split(","),
            "distiluse-base-multilingual-cased-v2,60.18,27.35,43.77,4000,480 MB".split(",")
        ], columns=['Model Name', 'Performance Sentence Embeddings (14 Datasets)', 'Performance Semantic Search (6 Datasets)', 'Avg. Performance', 'Speed', 'Model Size '])
    
    def listModels(self):
        print("Sentence Transformer available:\n")
        print(self.model_list)

    def loadModel(self,model):
        self.model = SentenceTransformer(model)

    def getEmbeddings(self,prompt:list[str]):
        query_embedding = self.model.encode(prompt)
        return query_embedding
    
    def compare(self,emb1,emb2):
        similarity = self.model.similarity(emb1, emb2)
        return similarity