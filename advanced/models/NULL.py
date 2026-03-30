from .model import BaseModel

class NULLModel(BaseModel):
    def __init__(self):
        super().__init__()
        
    def predict(self, df):
        return [0.0] * len(df)

    def update(self, df):
        return 0.0