# scrape wikipeida
from sentence_transformers import SentenceTransformer,util
import torch
import faiss
from dotenv import load_dotenv
from tqdm import tqdm
import pickle
from glob import glob
load_dotenv()


if __name__ == "__main__":
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    model.tokenizer.clean_up_tokenization_spaces = True
    with open('temp.pkl','rb') as file:
        cleaned_sections= pickle.load(file)
    file_path ="data/*.obj" 
    device='cuda' if torch.cuda.is_available() else 'cpu'

    meta_data=[]
    files = glob(file_path)

    index = faiss.IndexFlatIP(384)

    for file in files:
        meta_data_list = []
        with open(files[0],'rb') as file:
            objs= pickle.load(file)
            for o in objs:     
                n_sections=len(o['sections_embedded_tensor'])
                obj_meta_data = [o['wiki_page']]*n_sections
                cpu_embeddings=o['sections_embedded_tensor'].to(device).cpu().numpy().astype('float32')
                if len(cpu_embeddings)== 0: 
                    continue
                else:
                    index.add(cpu_embeddings)
                print(index.ntotal)
                meta_data.extend(obj_meta_data)

            
    cpu_queries = model.encode(cleaned_sections[0],convert_to_tensor=True,device=device).cpu().numpy().astype('float32')
    index.search(cpu_queries, 5)
