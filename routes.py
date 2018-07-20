from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os
import sys, getopt
import re
import json

#converts pdf, returns its text content as a string
#from https://www.binpress.com/tutorial/manipulating-pdfs-with-python/167
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

#creates textfile from pdf conversion
def pdf2txt(filename):
    content = convert(filename)
    # print(content)
    newfilename = filename + ".txt"
    newfile = open(newfilename, "w")
    newfile.write(content)
    newfile.close()

    return newfilename

#reads first few lines of file to get which state the permit is from
def permitState(newfilename,state_list):

    read_newfile = open(newfilename, 'r')

    while read_newfile:
        nline = ((read_newfile.readline()).strip()).split()
        for i in nline:
            if i in list(state_list.values()):
                return i



#searches entire documents for highway names and returns the route in a list
def readRoutes(filename, state_abbr):
    highway_regex = "([A-Z]{1,2}\-\d{2,4} (NE|SW|NW|SE|se|nw|sw|ne" \
                    "|BUS|WB|SB|NB|EB|B|[nwseNWSE]))|" \
                    "([A-Z]{1,2}\d{2,4} (NE|SW|NW|SE|se|nw|sw|ne" \
                    "|BUS|WB|SB|NB|EB|B|[nwseNWSE]))|" \
                    "([A-Z]{1,2}\d{2,4}WFR (NE|SW|NW|SE|se|nw|sw|ne" \
                    "|BUS|WB|SB|NB|EB|B|[nwseNWSE]))|" \
                    "([A-Z]{1,2}\d{2,4}NFR (NE|SW|NW|SE|se|nw|sw|ne" \
                    "|BUS|WB|SB|NB|EB|B|[nwseNWSE]))|" \
                    "([A-Z]{1,2}\d{2,4} Ramp (NE|SW|NW|SE|se|nw|sw|ne" \
                    "|BUS|WB|SB|NB|EB|B|[nwseNWSE]))"

    highways = []

    with open(filename, "r") as fp:
        new_line = fp.readline()
        while new_line:
            new_line = new_line.strip()
            
            m = re.split(highway_regex, new_line)
            m = filter(None, m)

            for v in m:
                n = re.match(highway_regex, v)
                if n:
                    #print(n.group(0))
                    highways.append(n.group(0))
                    
            for i, item in enumerate(highways):
                if item[0:2] == 'SL':
                    highways[i] = 'Loop ' + item[2:]

                if item[0:2] == 'SH':
                    highways[i] = state_abbr + item[2:]

                if item[0:2] == 'IH':
                    highways[i] = 'I-' + item[2:]

            for i, item in enumerate(highways):
                if 'WFR' in item:
                    highways[i] = item.replace("WFR", "")

                if 'NFR' in item:
                    highways[i] = item.replace("NFR", "")
            
            new_line = fp.readline()

    highways = [hw.upper() for hw in highways]

    return highways

#makes sure the highways in the list are unique
def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def main():

    statePermitRoute = {}
    state_abbr = ''

    newfilename = pdf2txt("2- KS PERMIT 805.pdf")

    state_list = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }

    state = permitState(newfilename, state_list)

    for abbr, full in state_list.items():
        if full == state:
            state_abbr = abbr
            print(state + ' State, ' + abbr + ' Permit Route:')

    highways = readRoutes(newfilename, state_abbr)

    highways = unique(highways)
    print(highways)

    print()

    statePermitRoute[state] = highways
    print(statePermitRoute)

    with open(newfilename+'.json', 'w') as outfile:
        json.dump(statePermitRoute, outfile)





main()