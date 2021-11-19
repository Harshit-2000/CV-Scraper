from pdfminer.high_level import extract_text
import nltk
import re

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


class Extract():
    text = ''
    info = ''

    def __init__(self, filepath, info):
        try:
            with open(filepath, 'rb') as f:
                self.text = extract_text(f)
        except Exception as e:
            print(e)
            self.text = ''

        self.getName(self.text, infoDict=info)
        self.getEmail(self.text, infoDict=info)

    def preprocess(self, document):
        lines = nltk.sent_tokenize(document)
        lines = [nltk.word_tokenize(el) for el in lines]
        lines = [nltk.pos_tag(el) for el in lines]

        return lines

    def getName(self, inputString, infoDict):
        '''
        Given an input string, returns possible matches for names. Uses regular expression based matching.
        Needs an input string, a dictionary where values are being stored, and an optional parameter for debugging.
        Modules required: clock from time, code.
        '''

        # Reads Indian Names from the file, reduce all to lower case for easy comparision [Name lists]
        indianNames = open("data/names.txt", "r").read().lower()
        # Lookup in a set is much faster
        indianNames = set(indianNames.split())

        otherNameHits = []
        nameHits = []
        name = None

        try:
            # tokens, lines, sentences = self.preprocess(inputString)
            lines = self.preprocess(inputString)

            # Try a regex chunk parser
            grammar = r'NAME: {<NN.*><NN.*>|<NN.*><NN.*><NN.*>}'
            # grammar = r'NAME: {<NN.*><NN.*><NN.*>*}'
            # Noun phrase chunk is made out of two or three tags of type NN. (ie NN, NNP etc.) - typical of a name. {2,3} won't work, hence the syntax
            # Note the correction to the rule. Change has been made later.
            chunkParser = nltk.RegexpParser(grammar)
            all_chunked_tokens = []
            for tagged_tokens in lines:
                # Creates a parse tree
                if len(tagged_tokens) == 0:
                    continue  # Prevent it from printing warnings
                chunked_tokens = chunkParser.parse(tagged_tokens)
                all_chunked_tokens.append(chunked_tokens)
                for subtree in chunked_tokens.subtrees():
                    #  or subtree.label() == 'S' include in if condition if required
                    if subtree.label() == 'NAME':
                        for ind, leaf in enumerate(subtree.leaves()):
                            if leaf[0].lower() in indianNames and 'NN' in leaf[1]:
                                # Case insensitive matching, as indianNames have names in lowercase
                                # Take only noun-tagged tokens
                                # Surname is not in the name list, hence if match is achieved add all noun-type tokens
                                # Pick upto 3 noun entities
                                hit = " ".join(
                                    [el[0] for el in subtree.leaves()[ind:ind+3]])
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
            pattern = re.compile(r'\S*@\S*')
            # Gets all email addresses as a list
            matches = pattern.findall(inputString)
            email = matches
            print(email)
        except Exception as e:
            print(e)

        infoDict['email'] = email

        return email


if __name__ == "__main__":
    info = {}
    Extract('data/sample.pdf', info)
