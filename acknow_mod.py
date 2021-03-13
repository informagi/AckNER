import csv
import glob
import spacy
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdfminer.pdfparser import PDFSyntaxError
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
nlp = spacy.load("en_core_web_sm")
from datetime import datetime



def extract_page(f):
    """
    Extracts the page containing the acknowledgements/funding section
    :param f: the file
    :return: (page(str), page_number)
    """
    page = ()
    count = 0
    for page_layout in extract_pages(f): # the method from pdfminer.six library
        count +=1
        s = ""
        for element in page_layout:
            if isinstance(element, LTTextContainer): # if is instance of the text
                s += element.get_text()
        x = re.search(r'(acknowledge?ments?)', s, re.IGNORECASE)
        y = re.search(r'(Funding|FUNDING)', s)
        if x or y:
            page = (s,count)
    return page


def extract_sentences(page):
    """
    Extracts the sentences that contain funding information
    :param page: tuple(page_text, page_number)
    :return: list of the sentences with necessary lemmas in
    """
    l = []
    if page:
        st = page[0].replace("\U0010fc2f","(")
        st = st.replace("\U0010fc30",")")
        st = st.replace("-\n", "")  # remove going to the next line with hyphens
        st = st.replace("\n", " ")  # remove going to next line
        st = re.sub(r'[Nn]o\.? ', "No.", st)
        #all the parentheses in order not to disrupt the syntactic structure
        st = st.replace("  "," ") # remove all the excessive spaces
        st = st.replace("- ", "")
        l_s = sent_tokenize(st)
        l_lemma = ["funding", "financial", "finance", "fund", "support","auspex","sponsor"]
        for el in l_s:
            sent = nlp(el)
            for token in sent: # keep the sentences where there lemmas linked to funding
                if token.lemma_ in l_lemma:
                    s = sent.text
                    if s[-1]  != ".":
                        s += "."
                    s = s.replace("this","that")
                    s = s.replace("This","That")
                    if "their" in s or "his" in s:
                        pass
                    else:
                        if s not in l:
                            l.append(s)
    return l


def parsing(l_sent):
    """
    Extracts the necessary named entities
    :param
    l_sent: list of necessary sentences
    :return: the list of named entities for the doc
    """
    li_ne = []
    s = ""
    l_d = []
    beg = False  # flag: beginning of the entity
    l_beg = ["compound", "nmod", "nummod", "amod","csubj"]  # beginning of the ne
    l_mid = ["compound", "poss", "punct","case", "conj", "nmod", "preconj","nummod", "cc", "amod"]  # middle of the ne
    l_root = ["dobj", "pobj","attr"]  # end of the ne
    l_prep = ["of","for","on"] # the prepositions that can be inside words
    if l_sent:
        for el in l_sent:
            el = re.sub(r'\(.*?\)', "", el, re.DOTALL)  # remove everything between parantheses, including \n
            le = len(el.split(" "))
            doc = nlp(el)  # applying spacy to sentences
            for i in range(len(doc)):
                if doc[i].dep_ in l_beg:
                    s += doc[i].text
                    s += " "
                    beg = True  # flag: true
                elif beg and doc[i].dep_ in l_mid:
                    s += doc[i].text  # continue adding
                    s += " "
                elif beg and doc[i].text in l_prep:
                    s += doc[i].text  # continue adding
                    s += " "
                elif doc[i].dep_ in l_root:
                    if s:
                        if doc[i+1].text in l_prep: # if the next token is a preposition that can be inside word groups
                            s += doc[i].text # keep adding
                            s += " "
                        else:
                            s += doc[i].text
                            s += " "
                            if s.rstrip() not in li_ne and s != s.lower():
                                li_ne.append(s.rstrip()) # else add to the list
                            beg = False  # end adding
                            s = ""
                else:
                    beg = False # we did not get the right pattern so we put the string to "".
                    s = ""
    return li_ne


def extract_cga(l_sent):
    """
    Extracts contracts, grants and abbreviations
    :param page: string
    :return: the list of contracts, grants and abbreviations
    """
    y = ""
    l_cga = []
    if l_sent:
        for s in l_sent:
            s = s.replace("-\n", "-")  # remove going to the next line with hyphens by a hyphen because it can be part of a contract
            s = s.replace("\n", " ")  # remove going to next line
            s = re.sub(r'[Nn]o\.? ', "No.", s)
            s = re.sub(r'[Nn]r. ', "No.", s)
            s = re.sub(r'[Nn]umber ', "No.", s)
            s = re.sub(r'[Nn]o: ', "No.", s)
            pattern_c = r'[Cc]ontract (No\.)?[A-Za-z0-9-]+'
            regex = re.compile(pattern_c)
            for match in regex.finditer(s):
                if match.group(0) not in l_cga:
                    l_cga.append(match.group(0))
            pattern_g = r'[Gg]rant ?([Aa]greement)? (No\.)?[A-Z0-9-–\.\/\\]+'
            regex = re.compile(pattern_g)
            for match in regex.finditer(s):
                if match.group(0).rstrip(".") not in l_cga:
                    l_cga.append(match.group(0).rstrip("."))
            pattern_ab = r'[A-Z]{3,10}[ \.)]+'
            regex = re.compile(pattern_ab)
            for match in regex.finditer(s):
                s = match.group(0)
                s = s[:-1]
                if s[-1] == ")":
                    s = s[:-1]
                if s not in l_cga:
                    l_cga.append(s)
    return l_cga

def to_csv(path):
    """
    Goes through all the pdf documents and extracts the named entities
    linked to the funding information to a csv file.
    :param path of the files
    adds named entities to a csv file in the format [path,page_number,ne,type_ne]
    adds paths of the articles where there were no matches to a separate text file.
    """
    nm = open("/data/output/no_matches.txt",'w') # open the file for articles with no matches
    with open("/data/output/ne.csv", 'w') as file: # open the file for named entities
        file.write('path,page_n,ne,type_ne\n')# write the names of the columns
    with open("/data/output/ne.csv", 'a', newline='') as ner:
        writer = csv.writer(ner)
        for filename in glob.iglob(path + '**/**', recursive=True):
            if filename.endswith(".pdf"):
                try:
                    l_fn = []
                    start_time = datetime.now()
                    f = filename
                    if f not in l_fn:
                        l_fn.append(f)
                        page = extract_page(f)
                        if page:
                            page_n = page[1]
                        li = extract_sentences(page)
                        l_ne = parsing(li)
                        li_cga = extract_cga(li)
                        if not l_ne: # if the list is empty (no ne), write the name of the file in "no_matches"
                            nm.write(f'item: {f}'+"\n")
                        end_time = datetime.now()
                        print(f)
                        print('Duration: {}'.format(end_time - start_time))
                        for ne in l_ne:
                            writer.writerow([f,page_n,ne])# write information in csv
                        for cga in li_cga:
                            writer.writerow([f, page_n, cga])  # write information in csv
                    else:
                        pass
                except PDFSyntaxError:
                    print(filename," IS NOT A PDF")
                except Exception as e:
                    print("Failed to parse %s" % (filename))
                    print(e)
                else:
                    print("reading: %s" % (filename))
        nm.close()

c = to_csv("/data/articles")
