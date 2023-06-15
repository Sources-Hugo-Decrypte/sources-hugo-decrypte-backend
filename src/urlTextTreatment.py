# generic text parsing functions

from tldextract import extract
from urlextract import URLExtract


def getAllUrlsFromDescription(textDesc, removeDuplicates=True):
    assert isinstance(textDesc, str), f"Given desc should be a string. Given : {textDesc}"
    extractor = URLExtract()
    listUrls = extractor.find_urls(textDesc)
    # Fixing 'spotify case' known issue :
    for i in range(len(listUrls)):
        if listUrls[i][:13] == "n.spotify.com": listUrls[i] = "https://ope" + listUrls[i]
    # Consider that 'www.test.com/mypage/' is equal to 'www.test.com/mypage':
    for i in range(len(listUrls)):
        if listUrls[i][-1] == '/': listUrls[i] = listUrls[i][:-1]
    # Remove duplicates :
    if removeDuplicates:
        listUrls = list(dict.fromkeys(listUrls))
    return listUrls

def getShortUrl(url):
    subdomain, domain, suffix = extract(url)
    if subdomain not in [None, ''] and domain not in [None, ''] and suffix not in [None, '']:
        return f"{subdomain}.{domain}.{suffix}"
    elif domain not in [None, ''] and suffix not in [None, '']:
        return f"{domain}.{suffix}"
    else:
        return url

def getDomainUrl(url):
    subdomain, domain, suffix = extract(url)
    if domain not in [None, ''] and suffix not in [None, '']:
        return f"{domain}.{suffix}"
    else:
        return url

