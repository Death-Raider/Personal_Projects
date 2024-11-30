import requests
import xml.etree.ElementTree as ET
import re

class ResearchPapers:
    def __init__(self,keywords=["period pain"],max_results=5):
        self.papers_euro = self.get_papers_europePubMedCentral(max_results= max_results, keywords= keywords)
        self.papers_arXiv = self.get_papers_arXiv(max_results= max_results, keywords= keywords)

    def get_link(self,x):
        formats = ['doi', "pmid",'pmcid']
        for form in formats:
            if form in x:
                return form
        return False

    def get_papers_europePubMedCentral(self,keywords,max_results):
        def generate_query_europePubMedCentral(kw_list: list, joining: str = "AND", openAccess: bool = False) -> str:
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            query = "?query=" + f"+{joining}+".join(kw_list) + ('%20OPEN_ACCESS:"Y"' if openAccess else '') + f"&format=json&resultType=core"
            return url+query

        openAccess = True

        url = generate_query_europePubMedCentral(
            kw_list = keywords,
            joining="OR",
            openAccess=openAccess
        )

        data = requests.get(url)
        data = data.json()
        papers = []

        for entry in data['resultList']['result']:
            if max_results > 0:
                data = {
                    "title": entry['title'],
                    "link": entry[list(filter(self.get_link,entry.keys()))[-1]],
                    "summary": entry["abstractText"] if "abstractText" in entry.keys() else ''
                }
                papers.append(data)
                max_results-=1
            else:
                break
        return papers
    
    def get_papers_arXiv(self,keywords,max_results):
        def generate_query_arXiv(kw_list: list, joining:str = "AND", max_results: int = 1, sortBy: str = "relevance", sortOrder: str = "descending") -> str:
            url = 'http://export.arxiv.org/api/query'
            processed_keywords = map(lambda x: "all:" + f'"{x}"',kw_list)
            query = "?search_query="+f"+{joining}+".join(processed_keywords) + f"&max_results={max_results}" + f"&sortBy={sortBy}" + f"&sortOrder={sortOrder}"
            return url + query

        url = generate_query_arXiv(
            kw_list = keywords,
            joining="OR",
            max_results = max_results
        )
        data = requests.get(url)
        root = ET.fromstring(data.text)
        xmlns = ''
        m = re.search('{.*}', root.tag)
        if m:
            xmlns = m.group(0)

        entries = root.findall(xmlns + "entry")
        papers = []
        for entry in entries:
            data = {
                "title": entry.find(xmlns + "title").text,
                "link": entry.find(xmlns + "id").text,
                "summary": entry.find(xmlns + "summary").text
            }
            papers.append(data)
        return papers