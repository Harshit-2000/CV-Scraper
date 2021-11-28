from pdfminer.high_level import extract_text
import nltk
import re
import time

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('words')


class Extract():
    text = ''
    info = ''

    words = []
    sentences = []

    def __init__(self, filepath, info, keywordFile):

        try:
            with open(filepath, 'rb') as f:
                self.text = extract_text(f)
        except Exception as e:
            print(e)
            self.text = ''

        self.sentences, self.words = self.preprocess(self.text)

        self.getName(self.text, infoDict=info)
        self.getEmail(self.text, infoDict=info)
        self.getPhoneNo(self.text, infoDict=info)
        self.getExperience(self.text, infoDict=info)
        cleanedText = self.cleanText(self.text, infoDict=info)
        self.checkKeywords(self.text, cleanedText=cleanedText,
                           infoDict=info, file=keywordFile)

    def preprocess(self, document):
        """
            Args :
                document : text extracted from pdf.
            Returns :
                sentences : A list with words with tags.
                words : A list sentences containing list words without tags.
        """

        sentences = nltk.sent_tokenize(document)
        sentences = [nltk.word_tokenize(el) for el in sentences]
        words = sentences
        sentences = [nltk.pos_tag(el) for el in sentences]

        temp = []
        for word in words:
            temp += word
        words = temp

        return sentences, words

    def getName(self, inputString, infoDict):
        '''
        Given an input string, returns possible matches for names. Uses regular expression based matching.
        Needs an input string, a dictionary where values are being stored, and an optional parameter for debugging.
        '''
        # Read newNames files from files
        newNames = open("data/names/newNames.txt", "r").read().lower()
        newNames = set(newNames.split())

        # Reads Indian Names from the file, reduce all to lower case for easy comparision [Name lists]
        indianNames = open("data/names/names.txt", "r").read().lower()
        # Covert to set as lookup in set is faster.
        indianNames = set(indianNames.split())

        # joining both sets - indianNames + newNames

        indianNames = indianNames | newNames

        otherNameHits = []
        nameHits = []
        name = None

        try:
            # Regex chunk parser
            grammar = r'NAME: {<NN.*><NN.*>|<NN.*><NN.*><NN.*>}'
            # Noun phrase chunk is made out of two or three tags of type NN. (ie NN, NNP etc.) - typical of a name.

            chunkParser = nltk.RegexpParser(grammar)
            all_chunked_tokens = []

            for tagged_tokens in self.sentences:
                # Creates a parse tree
                if len(tagged_tokens) == 0:
                    continue  # Prevent it from printing warnings
                chunked_tokens = chunkParser.parse(tagged_tokens)
                all_chunked_tokens.append(chunked_tokens)

                for subtree in chunked_tokens.subtrees():
                    if subtree.label() == 'NAME':
                        for ind, leaf in enumerate(subtree.leaves()):
                            if leaf[0].lower() in indianNames and 'NN' in leaf[1]:

                                # Case insensitive matching, as indianNames have names in lowercase
                                # Take only noun-tagged tokens
                                # Surname is not in the name list, hence if match is achieved add all noun-type tokens
                                # Pick upto 2 noun entities
                                hit = " ".join(
                                    [el[0] for el in subtree.leaves()[ind:ind+2]])
                                # Check for the presence of commas, colons, digits - usually markers of non-named entities
                                if re.compile(r'[\d,:]').search(hit):
                                    continue
                                nameHits.append(hit)
                                # Need to iterate through rest of the leaves because of possible mis-matches

            # Going for the first name hit
            if len(nameHits) > 0:
                nameHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip()
                            for el in nameHits]
                name = " ".join([el[0].upper()+el[1:].lower()
                                for el in nameHits[0].split() if len(el) > 0])
                otherNameHits = nameHits[1:]

        except Exception as e:
            print(e)

        infoDict['name'] = name
        infoDict['otherNameHits'] = otherNameHits

        return name, otherNameHits

    def getEmail(self, inputString, infoDict):

        email = None
        try:
            # pattern = re.compile(r'\S*@\S*')
            pattern = re.compile(
                r'[a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+')

            matches = pattern.findall(inputString)
            matches = ['[' + match.lower() + ']' for match in matches]
            email = matches

        except Exception as e:
            print(e)

        infoDict['email'] = email
        return email

    def getPhoneNo(self, inputString, infoDict):
        """
        Given an input string return possible matches for phone numbers using regex matching.
        Needs a inputSting and a dict to store the output.
        """

        phone = None

        try:
            pattern = re.compile(
                r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
            match = pattern.findall(inputString)

            # removing number with less than 10 digits and more than 13
            match = [re.sub(r'[\D]', '', el)
                     for el in match if len(re.sub(r'[\D]', '', el)) > 9 and len(re.sub(r'[\D]', '', el)) < 13]

            phone = match

        except Exception as e:
            print(e)

        infoDict['phoneNo'] = phone

        return phone

    def checkKeywords(self, inputString, cleanedText, infoDict, file):
        """
        Checks for common words in keywords and inputstring.
        Returns a list of words in both keywords and inputString.
        """

        found = []
        keywords = ['']
        no_of_match = 0
        try:
            if file == '1':
                keywords = open("uploads/keyword1.txt", "r").read().lower()
            elif file == '2':
                keywords = open("uploads/keyword2.txt", "r").read().lower()
            elif file == '3':
                keywords = open("uploads/keyword3.txt", "r").read().lower()
            else:
                keywords = ''

            keywords = set(keywords.split(','))
            keywords = [word.lower().strip() for word in keywords]

            for word in keywords:
                match = re.findall(word, cleanedText)
                no_of_match += len(match)
                if len(match) > 0:
                    found.append(word)

        except Exception as e:
            print(e)

        totalWords = [el.strip() for el in cleanedText.split(' ')]

        infoDict['foundKeywords'] = found
        infoDict['numberOfMatch'] = no_of_match
        infoDict['percentageMatch'] = round(
            (no_of_match / len(totalWords)) * 100)

        return found

    def getExperience(self, inputString, infoDict):
        experience = []

        try:
            pattern = re.compile(r'\S*\s?(years|yrs)')

            for i in range(len(self.words)):
                if self.words[i].lower() == 'experience':
                    sen = self.words[i-5: i+6]
                    sen = " ".join([word.lower() for word in sen])
                    experience = pattern.search(sen)
                    if experience:
                        break

        except Exception as e:
            print(e)

        if experience:
            infoDict['experience'] = experience.group()
        else:
            infoDict['experience'] = '-'

        return experience

    def cleanText(self, inputString, infoDict, save=True):
        """
        Takes in resume text and return cleaned text.
        """

        cleaned_data = re.sub(
            r'(\s+)', ' ', inputString)  # remove extra white space

        if save:
            infoDict['original_text'] = cleaned_data  # saving as original text

        cleaned_data = re.sub(
            r'(\S*\d{2,}\S*|\S*@\S*|\S+.com\W\S*|\w{15,})', '', cleaned_data)
        # remove emails, alphanumerical with more than 2 numbers ,urls and words with length more than 15.

        # remove punctuation
        cleaned_data = re.sub(r'\s\d+\s', ' ', cleaned_data)  # remove numbers
        cleaned_data = re.sub("[^0-9A-Za-z ]", "", cleaned_data)
        # convert into lowercase.
        cleaned_data = "".join([word.lower() for word in cleaned_data])

        # Removing stopwords and performing lemmatization
        stopwords = open('data/stopwords/stopwords.txt', mode='r').read()
        stopwords = set(stopwords.split(','))
        stopwords = [word.lower().strip() for word in stopwords]

        cleaned_data = nltk.tokenize.word_tokenize(cleaned_data)
        # wn = nltk.WordNetLemmatizer() # not lemmatizing due to time constrains

        cleaned_data = " ".join(
            [word for word in cleaned_data if word not in stopwords and len(word) > 1])  # removing words with length 1 and stopwords

        if save:
            infoDict['cleaned_text'] = cleaned_data

        return cleaned_data


if __name__ == "__main__":
    info = {}
    start = time.time()
    Extract('data/sample.pdf', info, 'data')
    end = time.time()
    print("Time Elapsed :", end - start)
    print(info)
