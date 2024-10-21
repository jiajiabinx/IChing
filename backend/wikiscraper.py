# scrape wikipeida
import wikipediaapi
from tqdm import tqdm
from sentence_transformers import SentenceTransformer,util
import pickle
from glob import glob


def get_all_sections(sections,level=0):
    result = []
    for s in sections:
        result.append("%s: %s - %s" % ("*" * (level + 1), s.title, s.text))
        result.extend(get_all_sections(s.sections, level + 1))
    return result

def embed_page_by_sections(wiki_page, _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")):
    sections = get_all_sections(wiki_page.sections)
    results = _model.encode(sections,convert_to_tensor=True)
    return results


def get_all_page_level_members(categorymembers, level=0, max_level=5):
    results = []
    for c in categorymembers.values():
        if c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level:
            results.extend(get_all_page_level_members(c.categorymembers, level=level + 1, max_level=max_level))
        elif c.ns == wikipediaapi.Namespace.CATEGORY:
            continue
        else:
            results.append(c.title)
    return results




if __name__ == "__main__":
    wiki = wikipediaapi.Wikipedia("iching",'en')
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    cat = wiki.page('Category:Lists_of_people_by_university_or_college_in_the_United_States_by_state')
    alumni_lists= get_all_page_level_members(cat.categorymembers)
    n_downloaded_lists = len(glob("data/*.obj"))
    
    for title in tqdm(alumni_lists[n_downloaded_lists:]):
        reference_data = []
        list = wiki.page(title)
        links = list.links
        for t in tqdm(sorted(links.keys())):
            page = links[t]
            if page.ns ==0:
                result = {"number_sections": len(page.sections),
                        "sections_embedded_tensor": embed_page_by_sections(page),
                        'wiki_page':page,
                        'wiki_page_title':t
                        }
                reference_data.append(result)
        file_name = "data/%s.obj" % "_".join(title.split(" "))
        with open(file_name,"wb") as file:
            pickle.dump(reference_data,file)