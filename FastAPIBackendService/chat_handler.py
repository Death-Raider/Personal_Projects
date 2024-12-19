from vec_embedding_transformer import Model
import numpy as np

def vectorize_database(model:Model, dataset: list[dict])->np.ndarray: # creates dataset
    embd_dataset = [0]*len(dataset)
    for index,data in enumerate(dataset):
        prompt = data
        embd = model.getEmbeddings(prompt)
        embd_dataset[index] = embd
    return np.array(embd_dataset)

def vectorize_database_search(model: Model, query, vector_db: np.ndarray):
    if type(query) == type([]):
        if type(query[0]) == type(""):
            pass
        else:
            raise AttributeError("Query type not supported")
    elif type(query) == type(""):
        query = [query]
    else:
        raise AttributeError("Query type not supported")

    embd = model.getEmbeddings(query)
    same = model.compare(embd,vector_db).numpy()
    index = np.argmax(same,axis=1)
    return index

def sample_dataset_for_db(text: str)->list[str]:
    sentences = text.split(".")
    
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    chunks = []
    check_size = 512
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < check_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

# def test():
#     model = Model()
#     model.loadModel("paraphrase-MiniLM-L3-v2")

#     # ['chat_id', 'prompt']
#     inp = ["test", "how has bill gates helped with ai?"]

#     with open(f"database/{inp[0]}.txt",'r',encoding='utf-8') as f:
#         text = f.read()
#     chunked_sentence_db = sample_dataset_for_db(text)

#     database = np.array(chunked_sentence_db)
#     vector_db = vectorize_database(model, database)

#     index = vectorize_database_search(model,inp[1],vector_db)

#     print("Query: ", inp[1])
#     print("Responce: ", database[index])
