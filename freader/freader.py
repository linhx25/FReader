# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 21:22:16 2019

@author: Hengxu Lin
"""

'''
freader: A tool to parse filings in html format
'''
from bs4 import BeautifulSoup,Comment
import re

class freader(object):
    
    def __init__(self,path=None,text=None,file_name=None,file_type=None,test_re = False):
        if file_type is not None:
            #determine the file type by params
            self.file_type = file_type
        else:
            self.file_type = path.split('\\')[-1].split('.')[1]
        if file_name is not None:
            self.file_name = file_name
        else:
            self.file_name = path.split('\\')[-1].split('.')[0]
        
        if path==None and text != None:
            self.text = text
        else:
            with open(path,'r',errors = 'ignore') as f:
                self.text = f.read()
        
        #if we do not sure whether to parse in regular expression 
        if test_re:
            if re.search(r'(^\s*?ITEM\s+7\.?)(.*?)(?=^\s*?ITEM\s+8\.?)',self.text,flags=re.I|re.S|re.M) is None:
                #regular expression fails to extract
                self.file_type = 'htm'
                
        self.filter_tag()
        self.ex_headings()
        
        if self.file_type ==('htm' or'html'):
            self.soup = BeautifulSoup(self.text,"lxml")
#            self.soup = BeautifulSoup(open(path,errors = 'ignore'),"lxml")
#            self.ex_comments()#extracts all the comments of the file
            self.text = self.soup.get_text()
            self.ex_tables()
            
        elif self.file_type =='txt':         
                       
            if re.search(r'<html>',self.text,re.I) is not None:
                #True means this txt file could be decode by bs4 in html format
                
                self.soup = BeautifulSoup(self.text,"lxml") 
                
                self.ex_tables(ex_tableOfContent = True,use_htm = True)
                self.text = self.soup.get_text()
            else:
                self.ex_tables()
                
            
    def filter_tag(self):
        '''
        filter all tags unneccessary
        '''
        re_br=re.compile(r'<br\s*?/?>',re.I)#line sign
        re_font=re.compile(r'<font[^>]*>|</font>',re.I)#font
#        re_style=re.compile(r' style="[^"]*?"',re.I)#style
        re_htmlhead = re.compile(r'<!DOCTYPE html[^>]*>')  # HTML headings
        re_comment = re.compile(r'<!--[^>]*-->')  # HTML comments
        
        self.text = re_br.sub('\n',self.text)
        self.text = re_font.sub(' ',self.text)
#        self.text = re_style.sub('',self.text)
        self.text = re_htmlhead.sub('',self.text)
        self.text = re_comment.sub('',self.text)
    
    def ex_headings(self):
        '''
        function extracts heading information of the file
        '''
        self.text = re.sub(r'<SEC-HEADER>(.*?)</SEC-HEADER>','',
                           self.text,flags = re.S|re.I)
                
    def ex_comments(self):
        '''
        function extracts all the comments of the file
        '''
        for element in self.soup(text=lambda text: isinstance(text, Comment)):
            element.extract()
            
    def ex_tables(self,ex_tableOfContent = False,use_htm = False):
        '''
        function extracts all the tables except Table of Contents        
        '''
        if (self.file_type == ('htm' or'html'))or use_htm:  
            table_list = self.soup.find_all('table')
            n = len(table_list)
            pattern = re.compile('item\s+[0-9]',re.I)
            if ex_tableOfContent == False:#do not extract table of content
                for i in range(n):
                    m = len(table_list[i].find_all('a'))
                    # no less than 15 'a' means it is the Table of Contents
                    flag = True
                    if pattern.search(table_list[i].get_text()) is not None:flag = False
                    if m < 15 and flag:
                        table_list[i].extract()
            else:#extract table of content
                for i in range(n):
                    table_list[i].extract()
        elif (self.file_type =='txt') and (not use_htm):
            self.text = re.sub(r'<TABLE[^>]*?>(.*?)</TABLE>','',self.text,flags=re.S|re.I)

    def item(self,text):
        '''
        This return the item name in convenience
        '''
        item1 = re.compile(r'(ITEM\s+1[^AB0-9]\.?)|(Business)',flags =re.I)
        item1a = re.compile(r'(ITEM\s+1A\.?)|(Risk Factors)',flags =re.I)
        item1b = re.compile(r'(ITEM\s+1B\.?)|(UNRESOLVED STAFF)',flags =re.I)
        item2 = re.compile(r'(ITEM\s+2\.?)|(PROPERTIES)',flags =re.I)
        item3 = re.compile(r'(ITEM\s+3\.?)|(LEGAL PROCEEDINGS)',flags =re.I)
        item4 = re.compile(r'(ITEM\s+4\.?)|(MINE SAFETY DISCLOSURES)',flags =re.I)
        item5 = re.compile(r'(ITEM\s+5\.?)|(MARKET FOR REGISTRANT’S)',flags =re.I)
        item6 = re.compile(r'(ITEM\s+6\.?)|(SELECTED FINANCIAL DATA)',flags =re.I)
        item7 = re.compile(r'(ITEM\s+7[^A]\.?)|(DISCUSSION)',flags =re.I)
        item7a = re.compile(r'(ITEM\s+7A\.?)|(QUANTITATIVE)',flags =re.I)
        item8 = re.compile(r'(ITEM\s+8\.?)|(SUPPLEMENTARY DATA)',flags =re.I)
        item9 = re.compile(r'(ITEM\s+9[^AB]\.?)|(CHANGES)',flags =re.I)
        item9a = re.compile(r'(ITEM\s+9A\.?)|(CONTROLS)',flags =re.I)
        item9b = re.compile(r'(ITEM\s+9B\.?)|(OTHER INFORMATION)',flags =re.I)
        item10 = re.compile(r'(ITEM\s+10\.?)|(DIRECTORS, EXECUTIVE)',flags =re.I)
        item11 = re.compile(r'(ITEM\s+11\.?)|(EXECUTIVE COMPENSATION)',flags =re.I)
        item12 = re.compile(r'(ITEM\s+12\.?)|(SECURITY OWNERSHIP)',flags =re.I)
        item13 = re.compile(r'(ITEM\s+13\.?)|(CERTAIN RELATIONSHIPS)',flags =re.I)
        item14 = re.compile(r'(ITEM\s+14\.?)|(PRINCIPAL ACCOUNTANT)',flags =re.I)
        item15 = re.compile(r'(ITEM\s+15\.?)|(EXHIBITS)',flags =re.I)        
        
        if re.search(item1,text) is not None:return 'item1'
        elif re.search(item1a,text) is not None:return 'item1a'
        elif re.search(item1b,text) is not None:return 'item1b'
        elif re.search(item2, text) is not None:return 'item2' 
        elif re.search(item3, text) is not None:return 'item3'
        elif re.search(item4, text) is not None:return 'item4'
        elif re.search(item5, text) is not None:return 'item5'
        elif re.search(item6, text) is not None:return 'item6'
        elif re.search(item7, text) is not None:return 'item7'
        elif re.search(item7a,text) is not None:return 'item7a'
        elif re.search(item8, text) is not None:return 'item8'
        elif re.search(item9, text) is not None:return 'item9'
        elif re.search(item9a,text) is not None:return 'item9a'
        elif re.search(item9b,text) is not None:return 'item9b'
        elif re.search(item10,text) is not None:return 'item10'
        elif re.search(item11,text) is not None:return 'item11'
        elif re.search(item12,text) is not None:return 'item12'
        elif re.search(item13,text) is not None:return 'item13'
        elif re.search(item14,text) is not None:return 'item14'
        elif re.search(item15,text) is not None:return 'item15'
        else:return False
#        else:return text
        

    def create_href_list(self):
        '''
        return L1: href_list   L2: name_of_href_list
        '''
        #deep copy
        _href_list = []
        _name_of_href_list = []
        
        #find special tag through a.href, only generated in Table of Contents
        a_list = self.soup.findAll('a',href=True)
        for i in a_list:
            if i['href'] not in _href_list:#skipping repeated hrefs
                item = self.item(' '.join(i.get_text().split()))
                if item != False:
                    _href_list.append(i['href'])
                    _name_of_href_list.append(item)
        return (_href_list,_name_of_href_list)
    
    def create_href_dict(self):
        '''
        create dictionary like {name:href} of the file
        param:
            L1: href_list
            L2: name_of_href_list
        return: dictionary like, {name:href} of the file
        '''    
        re_href_list = self.href_list.copy()#reversed href_list
        re_name_of_href_list = self.name_of_href_list.copy()#reversed name_of_href_list
        #reverse in order to save searching time
        re_href_list.reverse()
        re_name_of_href_list.reverse()
        _href_dict =dict(zip(re_name_of_href_list,re_href_list))
        return _href_dict
    
    def create_txt(self):
        '''
        traverse the DOM tree to acquire text of each item
        params:
            L: list of total strings, (txts)
            D: dictionary of {name:text} like (txts_dict)
        return: void
        '''
        L=[]
        D={}
    
        last_first_link = None
        for href_str,href in self.href_dict.items():
            #href[0] is '#', we don't want it
            first_link = self.soup.find('a',attrs={'name':href[1:]})
            tmp_txts = []
            
            try:
                for txt in first_link.next_elements:
                    if txt == last_first_link:# if this part was searched,do not do repeated work
                        break#print("Meet it")
                    if txt.string not in tmp_txts:#not in txts?
                        tmp_txts.append(txt.string)
                        L.append(txt.string)        
            except AttributeError:            
#                print("Warning: 'NoneType' object has no attribute 'next_elements'")
                continue 
            D[href_str] = tmp_txts
            last_first_link = first_link
        return L,D
    
    def createStr(self,pattern):
        '''
        This function create string according tp different items,
        using regular expression pattern.
        params: regular expression pattern
        return: item's text string
        '''
        resultSet = re.findall(pattern,self.text)
        L = []
        for r in resultSet:
            for v in r:
                if v is not None:
                    L.append(' '.join(v.split()))
        return ''.join(L)
    
    def create_txtDict(self,divide = False):
        '''
        This function creates the dicionary like{name:string}
        according to different items.
        return: Dictionary(_txts_dict)
        '''
        item1 = re.compile(r'(^\s*?ITEM\s+1[^0-9]\.?)(.*?)(?=^\s*?ITEM\s+2\.?)',
                           flags =re.S|re.M|re.I)        
        item2 = re.compile(r'(^\s*?ITEM\s+2\.?)(.*?)(?=^\s*?ITEM\s+3\.?)',
                           flags =re.S|re.M|re.I)
        item3 = re.compile(r'(^\s*?ITEM\s+3\.?)(.*?)(?=^\s*?ITEM\s+4\.?)',
                           flags =re.S|re.M|re.I)
        item4 = re.compile(r'(^\s*?ITEM\s+4\.?)(.*?)(?=^\s*?ITEM\s+5\.?)',
                           flags =re.S|re.M|re.I)
        item5 = re.compile(r'(^\s*?ITEM\s+5\.?)(.*?)(?=^\s*?ITEM\s+6\.?)',
                           flags =re.S|re.M|re.I)
        item6 = re.compile(r'(^\s*?ITEM\s+6\.?)(.*?)(?=^\s*?ITEM\s+7\.?)',
                           flags =re.S|re.M|re.I)
        item7 = re.compile(r'(^\s*?ITEM\s+7\.?)(.*?)(?=^\s*?ITEM\s+8\.?)',
                           flags =re.S|re.M|re.I)        
        item8 = re.compile(r'(^\s*?ITEM\s+8\.?)(.*?)(?=^\s*?ITEM\s+9\.?)',
                           flags =re.S|re.M|re.I)
        item9 = re.compile(r'(^\s*?ITEM\s+9\.?)(.*?)(?=^\s*?ITEM\s+10\.?)',
                           flags =re.S|re.M|re.I)        
        item10 = re.compile(r'(^\s*?ITEM\s+10\.?)(.*?)(?=^\s*?ITEM\s+11\.?)',
                            flags =re.S|re.M|re.I)
        item11 = re.compile(r'(^\s*?ITEM\s+11\.?)(.*?)(?=^\s*?ITEM\s+12\.?)',
                            flags =re.S|re.M|re.I)
        item12 = re.compile(r'(^\s*?ITEM\s+12\.?)(.*?)(?=^\s*?ITEM\s+13\.?)',
                            flags =re.S|re.M|re.I)
        item13 = re.compile(r'(^\s*?ITEM\s+13\.?)(.*?)(?=^\s*?ITEM\s+14\.?)',
                            flags =re.S|re.M|re.I)
        item14 = re.compile(r'(^\s*?ITEM\s+14\.?)(.*?)(?=((^\s*?ITEM\s+15\.?)|(^\s*?SIGNATURES)))',flags =re.S|re.M|re.I)
        item15 = re.compile(r'(^\s*?ITEM\s+15\.?)(.*?)(?=^\s*?SIGNATURES)',
                            flags =re.S|re.M|re.I)        
        
        if divide:
            item1 = re.compile(r'(^\s*?ITEM\s+1[^AB0-9]\.?)(.*?)(?=(^\s*?ITEM\s+2\.?)|(^\s*?ITEM\s+1A\.?))',flags =re.S|re.M|re.I)
            item1a = re.compile(r'(^\s*?ITEM\s+1A\.?)(.*?)(?=^\s*?ITEM\s+1B\.?)',flags =re.S|re.M|re.I)
            item1b = re.compile(r'(^\s*?ITEM\s+1B\.?)(.*?)(?=^\s*?ITEM\s+2\.?)',flags =re.S|re.M|re.I)
            item7 = re.compile(r'(^\s*?ITEM\s+7[^A]\.?)(.*?)(?=(^\s*?ITEM\s+8\.?)|(^\s*?ITEM\s+7A\.?))',flags =re.S|re.M|re.I)
            item7a = re.compile(r'(^\s*?ITEM\s+7A\.?)(.*?)(?=(^\s*?ITEM\s+8\.?))',flags =re.S|re.M|re.I)
            item9 = re.compile(r'(^\s*?ITEM\s+9[^AB]\.?)(.*?)(?=(^\s*?ITEM\s+10\.?)|(^\s*?ITEM\s+9A\.?))',flags =re.S|re.M|re.I)
            item9a = re.compile(r'(^\s*?ITEM\s+9A\.?)(.*?)(?=^\s*?ITEM\s+9B\.?)',flags =re.S|re.M|re.I)
            item9b = re.compile(r'(^\s*?ITEM\s+9B\.?)(.*?)(?=^\s*?ITEM\s+10\.?)',flags =re.S|re.M|re.I)        
        
        
        _txts_dict = {}
        _txts_dict['item1'] = self.createStr(item1)        
        _txts_dict['item2'] = self.createStr(item2)
        _txts_dict['item3'] = self.createStr(item3)
        _txts_dict['item4'] = self.createStr(item4)
        _txts_dict['item5'] = self.createStr(item5)
        _txts_dict['item6'] = self.createStr(item6)
        _txts_dict['item7'] = self.createStr(item7)        
        _txts_dict['item8'] = self.createStr(item8)
        _txts_dict['item9'] = self.createStr(item9)        
        _txts_dict['item10'] = self.createStr(item10)
        _txts_dict['item11'] = self.createStr(item11)
        _txts_dict['item12'] = self.createStr(item12)
        _txts_dict['item13'] = self.createStr(item13)
        _txts_dict['item14'] = self.createStr(item14)
        _txts_dict['item15'] = self.createStr(item15) 
        
        if divide:
            #divide the text into more detail items
            _txts_dict['item1a'] = self.createStr(item1a)
            _txts_dict['item1b'] = self.createStr(item1b)
            _txts_dict['item7a'] = self.createStr(item7a)
            _txts_dict['item9a'] = self.createStr(item9a)
            _txts_dict['item9b'] = self.createStr(item9b)
        _txts_dict['text'] = ' '.join(self.text.split())
#        text = ''
#        for v in _txts_dict.values():
#            text = ''.join([text,v])
#        _txts_dict['text'] = text
            
        return _txts_dict
    
    def join_txt(self):
        """
        join the txt into a string.
        #TODO:This process really consuming time
        #Solved: do not traverse the dictionary by keys(), it is a list, O(n)
        """
        _txt_d = {}
        for k,v in self.txts_dict.items():
            join_str = []
            for s in v:
                if s is not None:
                    join_str.append(' '.join(s.split()))#remove unwanted char
            _txt_d.setdefault(k,''.join(join_str))
        _txt_d['text'] = ' '.join(self.text.split())
        return _txt_d
    
    def dict_to_txt(self,using_str = True):
        '''
        write the {name:text}dictionary to txt file
        D: dictionary like(txts_dict)
        L: name_of_href_list
        '''
        with open(self.file_name+'.txt','w',encoding='utf-8') as f:        
            
            if using_str:#join the text
                L = self.name_of_href_list
                D = self._txts_dict
                for k in L:
                    try:
                        f.write(k)
                        f.write('*~')#delimiter='*~'
                        f.write(D[k])
                    except:continue
                    f.write('\n')
            else:#do not join the text, for time comsuming sake
                L = self.name_of_href_list
                D = self.txts_dict
                for k in L:
                    try:
                        n =len(D[k])
                    except:continue
                    try:#TODO: check the necessity
                        f.write(k)
                    except:continue
                    f.write('*~')#delimiter='*~'
                    for v in range(n-1):
                        if(D[k][v] is None):continue
                        f.write(D[k][v])
                        f.write(' ')
                    try:
                        f.write(D[k][n-1])
                    except:continue
                    f.write('\n')             

        print('"'+self.file_name+'_text.txt"have been saved.')
        
    def to_csv(self,path = None):
        '''
        write the dictionary to csv file
        '''
        if path is None:
            path = self.file_name+'.csv'
        import pandas as pd
        
        series = pd.Series(self._txts_dict,index =self._txts_dict.keys(),name='content')
        series.to_csv(path,header = ['content'],encoding = 'utf-8')
            
    @property
    def txts(self):
        '''
        list of total strings
        '''
        return self.create_txt()[0]
    
    @property
    def txts_dict(self):
        '''
        dictionary of {name:text} like
        '''
        return self.create_txt()[1]   

    @property
    def _txts_dict(self):
        '''
        dictionary of {name:text_string} like
        '''
        if self.file_type == ('htm'or 'html'):
            return self.join_txt()
        elif self.file_type == 'txt':
            return self.create_txtDict(divide=True)
        
    @property
    def href_list(self):
        '''
        list of href
        '''
        return self.create_href_list()[0]
    
    @property
    def name_of_href_list(self):
        '''
        list of name of the node with special href
        For writing to txt file's convinience
        '''
        return self.create_href_list()[1]
    
    @property
    def href_dict(self):
        '''
        dictionary like, {name:href} of the file
        '''
        return self.create_href_dict()
    
  
import string
from pyphen import Pyphen
import math
from collections import Counter

    
class Textstat(object):    
        
    text_encoding = 'utf-8'
    
    def char_count(self,text,ignore_spaces = True):
        """
        Function to return total character counts in a text.
        params:
            text: string
            ignore_spaces: boolean, whether ignore whitespaces
        return: total count of characters of the text
        """
        if isinstance(text,list):
            # ignoring all space
            tmp = []
            for s in text:
                if s is not None:
                    tmp.append(''.join(s.split()))
            return len(''.join(tmp))            
        else:
            if ignore_spaces:
                text = text.replace(' ','')
            return len(text)
    
    def letter_count(self,text,ignore_spaces = True):
        """
        Function to return total letter amount in a text,
        params:
            text: string
            ignore_spaces: boolean, whether ignore whitespaces
        return: total count of letters of the text   
        """
        if isinstance(text,list):
            # ignoring all space
            tmp = []
            for s in text:
                if s is not None:
                    tmp.append(''.join(s.split()))
            s = ''.join(tmp)
            return len(self.remove_punctuation(s))
        else:
            if ignore_spaces:
                text = text.replace(' ','')
            return len(self.remove_punctuation(text))
    
    @staticmethod
    def remove_punctuation(text):
        """
        Funtion to remove puntuations of the text
        return: text after removing punctuations
        """
        return "".join(c for c in text if c not in string.punctuation)
    
    def lexicon_count(self, text, remove_punct=True):
        """
        Function to return total lexicon (words in lay terms) counts in a text
        """
        if isinstance(text,list):
            tmp = []
            for t in text:
                if t is not None:                    
                    tmp.extend(
                            [self.remove_punctuation(r) for r in t.split()])
            return len(tmp)                    
        else:
            if remove_punct:
                text = self.remove_punctuation(text)
            count = len(text.split())
            return count
    
    def syllable_count(self,text,lang ='en_US'):
        """
        Function to calculate syllable words in a text.
        return: counts of syllable words
        """
        if isinstance(text,bytes):
            text = text.decode(self.text_encoding)
        try:
            text = text.lower()
        except:pass
        text = self.remove_punctuation(text)
        
        if not text:#None
            return 0
        dic= Pyphen(lang =lang)
        count = 0
        for word in text.split(' '):
            word_hyphenated = dic.inserted(word)
            count +=max(1,word_hyphenated.count("-")+1)
        return count
    
    def sentence_count(self,text):
        """
        Function to count sentences of a text
        return: number of sentences
        """
#        ignore_count = 0
        sentences = re.split(r' *[\.\?!][\'"\)\]]*[ |\n](?=[A-Z])', text)
#        for sentence in sentences:
#            if self.lexicon_count(sentence) <= 2:
#                ignore_count += 1
#        return max(1, len(sentences)-ignore_count)
        return max(1, len(sentences))

    @staticmethod
    def legacy_round(number, points=4):
        p = 10 ** points
        return float(math.floor((number * p) + math.copysign(0.5, number))) / p
       
    def avg_sentence_length(self, text):
        """
        return the average words of the sentences.
        """
        try:
            asl = float(self.lexicon_count(text) / self.sentence_count(text))
            return self.legacy_round(asl, 4)
        except ZeroDivisionError:
            return 0.0
        
    def avg_syllables_per_word(self,text):
        """
        return the average syllables per word.
        """
        n_syllable = self.syllable_count(text)
        n_words = self.lexicon_count(text)
        try:
            syllables_per_word = float(n_syllable)/float(n_words)
            return self.legacy_round(syllables_per_word,4)
        except ZeroDivisionError:
            return 0.0
    
    def avg_character_per_word(self,text):
        """
        return the average characters per word.
        """
        try:
            chars_per_word = float(
                    self.char_count(text)/self.lexicon_count(text))
            return self.legacy_round(chars_per_word,4)
        except ZeroDivisionError:
            return 0.0
    
    def avg_letter_per_word(self,text):
        """
        return the average letters per word.(without puntuations)
        """
        try:
            letters_per_word = float(
                    self.letter_count(text)/self.lexicon_count(text))
            return self.legacy_round(letters_per_word,4)
        except ZeroDivisionError:
            return 0.0
    
    def avg_sentence_per_word(self,text):
        """
        return average sentences per word.
        """
        try:
            sentence_per_word = float(
                    self.lexicon_count(text)/self.sentence_count(text))
            return self.legacy_round(sentence_per_word,4)
        except ZeroDivisionError:
            return 0.0
        
    def flesch_reading_ease(self, text):
        """
        #TODO
        return the flesch reading ease index
        """
        sentence_length = self.avg_sentence_length(text)
        syllables_per_word = self.avg_syllables_per_word(text)
        flesch = (
            206.835
            - float(1.015 * sentence_length)
            - float(84.6 * syllables_per_word)
        )
        return self.legacy_round(flesch, 4)

    def flesch_kincaid_grade(self, text):
        """
        #TODO
        return the flesch-kincaid grade index
        """
        sentence_lenth = self.avg_sentence_length(text)
        syllables_per_word = self.avg_syllables_per_word(text)
        flesch = (
            float(0.39 * sentence_lenth)
            + float(11.8 * syllables_per_word)
            - 15.59)
        return self.legacy_round(flesch, 4)
    
    def polysyllabcount(self, text):
        count = 0
        for word in text.split():
            wrds = self.syllable_count(word)
            if wrds >= 3:
                count += 1
        return count
    
    def smog_index(self, text):
        """
        #TODO: not yet check the formula
        return the Smog index of the text
        """
        sentences = self.sentence_count(text)

        if sentences >= 3:
            try:
                poly_syllab = self.polysyllabcount(text)
                smog = (
                    (1.043 * (30 * (poly_syllab / sentences)) ** .5)
                    + 3.1291)
                return self.legacy_round(smog, 4)
            except ZeroDivisionError:
                return 0.0
        else:
            return 0.0
        
    def coleman_liau_index(self, text):
        """
        #TODO
        return the Coleman-Liau index of the text
        """
        letters = self.legacy_round(self.avg_letter_per_word(text)*100, 4)
        sentences = self.legacy_round(self.avg_sentence_per_word(text)*100, 4)
        cli = float((0.0588 * letters) - (0.296 * sentences) - 15.8)
        return self.legacy_round(cli, 4)
    
    def automated_readability_index(self, text):
        """
        #TODO
        return the Automated Readability index of the text
        """
        chrs = self.char_count(text)
        words = self.lexicon_count(text)
        sentences = self.sentence_count(text)
        try:
            a = float(chrs)/float(words)
            b = float(words) / float(sentences)
            readability = (
                (4.71 * self.legacy_round(a, 4))
                + (0.5 * self.legacy_round(b, 4))
                - 21.43)
            return self.legacy_round(readability, 4)
        except ZeroDivisionError:
            return 0.0
        
    def linsear_write_formula(self, text):
        #TODO
        easy_word = 0
        difficult_word = 0
        text_list = text.split()[:100]

        for word in text_list:
            if self.syllable_count(word) < 3:
                easy_word += 1
            else:
                difficult_word += 1

        text = ' '.join(text_list)

        number = float(
            (easy_word * 1 + difficult_word * 3)
            / self.sentence_count(text))

        if number <= 20:
            number -= 2

        return number / 2
    
    def difficult_words(self, text,syllable_threshold=3):
        ltext = ''
        try:
            ltext = text.lower()
        except:
            ltext = str(text)        
        text_list = re.findall(r"[\w\='‘’]+", ltext)
        count = 0
#        diff_words_set  =[]
        for value in text_list:
#            if value not in easy_word_set:
            if self.syllable_count(value) >= syllable_threshold:
                count += 1
        return count
    
    def dale_chall_readability_score(self, text):
        word_count = self.lexicon_count(text)
        count = word_count - self.difficult_words(text)

        try:
            per = float(count) / float(word_count) * 100
        except ZeroDivisionError:
            return 0.0

        difficult_words = 100 - per
        
        score = (
            (0.1579 * difficult_words)
            + (0.0496 * self.avg_sentence_length(text)))

        if difficult_words > 5:
            score += 3.6365
        return self.legacy_round(score, 4)
    
    def gunning_fog(self, text):
        try:
            per_diff_words = (
                (self.difficult_words(text,syllable_threshold=3) / self.lexicon_count(text) * 100))

            grade = 0.4 * (self.avg_sentence_length(text) + per_diff_words)
            return self.legacy_round(grade, 4)
        except ZeroDivisionError:
            return 0.0
        
    def lix(self, text):
        words = text.split()

        words_len = len(words)
        long_words = len([wrd for wrd in words if len(wrd) > 6])

        per_long_words = (float(long_words) * 100) / words_len
        asl = self.avg_sentence_length(text)
        lix = asl + per_long_words

        return self.legacy_round(lix, 4)
    
    @staticmethod
    def get_grade_suffix(grade):
        """
        Select correct ordinal suffix
        """
        ordinal_map = {1: 'st', 2: 'nd', 3: 'rd'}
        teens_map = {11: 'th', 12: 'th', 13: 'th'}
        return teens_map.get(grade % 100, ordinal_map.get(grade % 10, 'th'))
    
    def text_standard(self, text, float_output=None):

        grade = []

        # Appending Flesch Kincaid Grade
        lower = self.legacy_round(self.flesch_kincaid_grade(text))
        upper = math.ceil(self.flesch_kincaid_grade(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Flesch Reading Easy
        score = self.flesch_reading_ease(text)
        if score < 100 and score >= 90:
            grade.append(5)
        elif score < 90 and score >= 80:
            grade.append(6)
        elif score < 80 and score >= 70:
            grade.append(7)
        elif score < 70 and score >= 60:
            grade.append(8)
            grade.append(9)
        elif score < 60 and score >= 50:
            grade.append(10)
        elif score < 50 and score >= 40:
            grade.append(11)
        elif score < 40 and score >= 30:
            grade.append(12)
        else:
            grade.append(13)

        # Appending SMOG Index
        lower = self.legacy_round(self.smog_index(text))
        upper = math.ceil(self.smog_index(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Coleman_Liau_Index
        lower = self.legacy_round(self.coleman_liau_index(text))
        upper = math.ceil(self.coleman_liau_index(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Automated_Readability_Index
        lower = self.legacy_round(self.automated_readability_index(text))
        upper = math.ceil(self.automated_readability_index(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Dale_Chall_Readability_Score
        lower = self.legacy_round(self.dale_chall_readability_score(text))
        upper = math.ceil(self.dale_chall_readability_score(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Linsear_Write_Formula
        lower = self.legacy_round(self.linsear_write_formula(text))
        upper = math.ceil(self.linsear_write_formula(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Gunning Fog Index
        lower = self.legacy_round(self.gunning_fog(text))
        upper = math.ceil(self.gunning_fog(text))
        grade.append(int(lower))
        grade.append(int(upper))

        # Finding the Readability Consensus based upon all the above tests
        d = Counter(grade)
        final_grade = d.most_common(1)
        score = final_grade[0][0]

        if float_output:
            return float(score)
        else:
            lower_score = int(score) - 1
            upper_score = lower_score + 1
            return "{}{} and {}{} grade".format(
                lower_score, self.get_grade_suffix(lower_score),
                upper_score, self.get_grade_suffix(upper_score)
            )
    
    
if __name__ == '__main__':
    file_path = 'D:\\w\\annual_report\\'
    file_name = '67514-NATIONAL WATERWORKS INC-2005-3-3.txt'
    path = file_path + file_name    
    
    import time
    t1 = time.time()
    f = freader(path)
#    f.ex_tables()        
#    f.dict_to_txt()
    t2 = time.time()
#    print(f._txts_dict['item2'])
    print(len(f._txts_dict['item7']))
    t3 = time.time()
    print('Using time:%.2fs'%(t2-t1))
    print('Using time2:%.2fs'%(t3-t2))
    

    
    
    
    
    
    
    
        