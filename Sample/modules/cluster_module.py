from .clustering.wordClusterList import WordClusterList
from .clustering.parsing import parseNouns, parseVerbNet
from .utils import writeToCSV
from .datastructs.metaphor_group import MetaphorGroup
from .datastructs.metaphor import Metaphor
import csv
import ast

from tqdm import tqdm

VERBNET = "data/clustering/verbnet_150_50_200.log-preprocessed"
NOUNS = "data/clustering/200_2000.log-preprocessed"
TROFI_TAGS = "data/clustering/trofi_tags_full.csv"

RESULTS = "data/clustering/results2.csv"
# RESULTS = "../data/clustering/results.csv"

# test the result to see if it has every words
# Parse the verbnet and noun databases
def getVerbNouns(verbPath, nounPath):
    verbData = WordClusterList.fromFile(verbPath, parseVerbNet)
    #print(data1)

    nounData = WordClusterList.fromFile(nounPath, parseNouns)
    #print(data2)

    return [verbData, nounData]

# Get the  tags from a CSV file (trofi full)
def getTagsFromCSV(path):
    verbObjTags = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            verb = row["Verb"]
            noun = row["Noun"]
            verbObjTags[(verb, noun)] = ast.literal_eval(row["Labels"])
    return verbObjTags

# Get a list of all the possible verb-noun couples in the database, returns a list of pairs of 2 lists, one list of verbs from the same cluster and one list of nouns from the same cluster
def buildPairs(verbsData, nounsData):
    return [(v, n) for v in verbsData for n in nounsData]


# Main algorithm
def tagPairs(verbsData, nounsData, tags):
    pairs = buildPairs(verbsData, nounsData)
    results = []
    for p in pairs:
        literals = 0
        nonliterals = 0
        verbNounPairs = []
        for verb in p[0]:
            for noun in p[1]:
                currentPair = (verb, noun)
                verbNounPairs.append(currentPair)
                if currentPair in tags.keys():
                    for t in tags[currentPair]:
                        if t == "N":
                            nonliterals+=1
                        elif t == "L":
                            literals+=1
        total = literals+nonliterals
        if total != 0:
            for vn in verbNounPairs:
                currentResult = {}
                currentResult["verb"] = vn[0]
                currentResult["noun"] = vn[1]
                if literals/total > 0.5:
                    currentResult["tag"] = "L"
                    currentResult["confidence"] = literals/total
                else:
                    currentResult["tag"] = "N"
                    currentResult["confidence"] = nonliterals/total
                results.append(currentResult)
        else:
            for vn in verbNounPairs:
                currentResult = {}
                currentResult["verb"] = vn[0]
                currentResult["noun"] = vn[1]
                currentResult["tag"] = "L"
                currentResult["confidence"] = 0.1
                results.append(currentResult)

    return results

def buildDB():
    verbs, nouns = getVerbNouns(VERBNET, NOUNS)
    tags = getTagsFromCSV(TROFI_TAGS)
    results = tagPairs(verbs, nouns, tags)
    # writeToCSV(results, RESULTS, ["verb", "noun", "tag", "confidence"])
    writeToCSV(results, "data/clustering/results2.csv", ["verb", "noun", "tag", "confidence"])

def buildAlphabeticalDatabase():
    verbs, nouns = getVerbNouns(VERBNET, NOUNS)
    tags = getTagsFromCSV(TROFI_TAGS)
    results = tagPairs(verbs, nouns, tags)
    import pandas as pd
    results = pd.DataFrame(results)
    results = results[['verb', 'noun', 'tag', 'confidence']]
    results = results.sort_values('verb')
    results['i'] = [i for i in range(results.shape[0])]
    results = results.set_index('i', drop=True)
    print(results.iloc[5:8])

    currentLetter = results.iloc[0]['verb'][0].lower()
    index = [0]
    letters = [currentLetter]
    for i in tqdm(range(1,results.shape[0])):
        newLetter = results.iloc[i]['verb'][0].lower()
        if newLetter != currentLetter:
            index.append(i)
            letters.append(newLetter)
            currentLetter = newLetter

    for i in range(len(index)-1):
        firstIndex = index[i]
        lastIndex = index[i+1]
        results.iloc[firstIndex:lastIndex].to_csv("data/clustering/DB/" + letters[i] + ".csv", index=False)

    results.iloc[index[-1]:results.shape[0]].to_csv("data/clustering/DB/" + letters[-1] + ".csv", index=False)





    # alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    # for letter in alphabet:
    #     print('\nLetter:', letter)
    #     index = list()
    #     length = results.shape[0]
    #     for i in tqdm(range(length)):
    #         verb = results.iloc[i]['verb']
    #         verb = verb.lower()
    #         if verb.startswith(letter):
    #             index.append(i)
    #     print(results.iloc[index])
    #     results.iloc[index].to_csv("data/clustering/DB/", letter ,".csv")



def loadDB(path):
    DB = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            DB[(row["verb"], row["noun"])] = (row["tag"], float(row["confidence"]))
    return DB

def loadAlphabeticalDB(DB, path):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            DB[(row["verb"], row["noun"])] = (row["tag"], float(row["confidence"]))
    return DB

def lookUpDB(DB, verb, noun):

    # If the pair (verb, noun) is in the DB
    if (verb, noun) in DB.keys():
        result = DB[(verb, noun)]
        if result[0] == "L":
            return (False, result[1])
        else:
            return (True, result[1])
    # If the pair is not in the DB, we look for similar words
    else:
        # print("Pair not in the database")
        # from gensim.models import KeyedVectors
        # filename = './data/clustering/GoogleNews-vectors-negative300.bin'
        # model = KeyedVectors.load_word2vec_format(filename, binary=True)
        #
        # mostSimilarWords = model.wv.most_similar(positive=verb, topn=5)
        # print(mostSimilarWords)

        return (False, 0.0)

# MAIN FUNCTION
def clusteringFunction(candidates, cand_type, verbose):

    results = MetaphorGroup()
    DB = loadDB(RESULTS)

    for c in candidates:
        source = c.getSource()
        target = c.getTarget()
        if verbose:
            print("###############################################################################")
            print("SOURCE: " + source)
            print("TARGET: " + target)

        currentResult = lookUpDB(DB, source, target)
        result = currentResult[0]
        confidence = currentResult[1]

        if verbose:
            if confidence >= 0.5:
                print("RESULT: " + str(result))
                print("CONFIDENCE: " + str(confidence))
            else:
                print("RESULT: Unknown")
                print("Verb/Noun pair not in database")

        results.addMetaphor(Metaphor(c, result, confidence))

    return results

# MAIN FUNCTION OPTIMIZED
def clusteringFunction_2(candidates, cand_type, verbose):

    results = MetaphorGroup()
    DB = dict()
    path = './data/clustering/DB/'
    already_in = list()  # list of first letters to see if data is already in cache

    for c in candidates:
        source = c.getSource()
        target = c.getTarget()
        if verbose:
            print("###############################################################################")
            print("SOURCE: " + source)
            print("TARGET: " + target)

        firstLetter = source[0].lower()
        if firstLetter not in already_in:
            DB = loadAlphabeticalDB(DB, path + firstLetter + '.csv')
            already_in.append(firstLetter)

        currentResult = lookUpDB(DB, source, target)
        result = currentResult[0]
        confidence = currentResult[1]

        if verbose:
            if confidence >= 0.5:
                print("RESULT: " + str(result))
                print("CONFIDENCE: " + str(confidence))
            else:
                print("RESULT: Unknown")
                print("Verb/Noun pair not in database")

        results.addMetaphor(Metaphor(c, result, confidence))

    return results

