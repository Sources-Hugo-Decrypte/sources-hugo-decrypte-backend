
# main functions to execute requests on internet

# from bs4 import BeautifulSoup
import requests, logging, json
import urllib.request, urllib.error
import http.client

httpStatus = {  # details on : https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
  "1": "Informational",
  "100": "Continue",
  "101": "Switching Protocols",
  "2": "Successful",
  "200": "OK",
  "201": "Created",
  "202": "Accepted",
  "203": "Non-Authoritative Information",
  "204": "No Content",
  "205": "Reset Content",
  "206": "Partial Content",
  "3": "Redirection",
  "300": "Multiple Choices",
  "301": "Moved Permanently",
  "302": "Found",
  "303": "See Other",
  "304": "Not Modified",
  "305": "Use Proxy",
  "306": "(Unused)",
  "307": "Temporary Redirect",
  "4": "Error Client",
  "400": "Bad Request",
  "401": "Unauthorized",
  "402": "Payment Required",
  "403": "Forbidden",
  "404": "Not Found",
  "405": "Method Not Allowed",
  "406": "Not Acceptable",
  "407": "Proxy Authentication Required",
  "408": "Request Timeout",
  "409": "Conflict",
  "410": "Gone",
  "411": "Length Required",
  "412": "Precondition Failed",
  "413": "Request Entity Too Large",
  "414": "Request-URI Too Long",
  "415": "Unsupported Media Type",
  "416": "Requested Range Not Satisfiable",
  "417": "Expectation Failed",
  "5": "Error Server",
  "500": "Internal Server Error",
  "501": "Not Implemented",
  "502": "Bad Gateway",
  "503": "Service Unavailable",
  "504": "Gateway Timeout",
  "505": "HTTP Version Not Supported"
}

def webScrappingAllHTML(url, parsing='html.parser'):
    """
    Do a research on internet and return full html code of the page founded
    :param url: string of the url
    :return: all html code of the founded page (BeautifulSoup object)
    """
    # Header to fake a browser in the request. This is to force request for websites which are blocking the python agent for http requests :
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    response = requests.get(url, headers=header, verify=False, stream=True)
    httpStatusValue = str(response).split('[')[1].replace(']>','')
    if httpStatusValue[0] in httpStatus.keys() and httpStatusValue in httpStatus.keys():
        print("HTTP request status : " + httpStatus[httpStatusValue[0]] + " (" + httpStatus[httpStatusValue] + ")")
    return BeautifulSoup(response.content, parsing)


def webDownloadPicture(url, filePath):
    """
    Download a picture from url
    :param url: url of the picture
    :param filePath: path and file name where to save the picture
    :return: 0 if no error
    """
    # Header to fake a browser in the request. This is to force request for websites which are blocking the python agent for http requests :
    #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    header = {'User-Agent': 'Chrome/39.0.2171.95'}
    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    response = requests.get(url, headers=header, verify=False, stream=True)
    httpStatusValue = str(response).split('[')[1].replace(']>', '')
    if httpStatusValue[0] in httpStatus.keys() and httpStatusValue in httpStatus.keys():
        print("HTTP request status : " + httpStatus[httpStatusValue[0]] + " (" + httpStatus[httpStatusValue] + ")")
    file = open(filePath, 'wb')
    file.write(response.content)
    file.close()
    return 0

def OLD_checkUrls(urlList, returnErrors=True):
    """
    If errors detected returns {"HTTPError": [{"url"     : url,
                                              "Exception": e},
                                              {"url"     : url,
                                              "Exception": e},
                                              ...],
                                "URLError" : [{"url"     : url,
                                              "Exception": e},
                                              {"url"     : url,
                                              "Exception": e},
                                              ...],
                                "Others"   : [{"url"     : url,
                                              "Exception": e},
                                              {"url"     : url,
                                              "Exception": e},
                                              ...]
                                }
    """
    HTTPError = []
    URLError = []
    OtherError = []
    for url in urlList:
        try:
            assert urllib.request.urlopen(url).getcode() == 200, "Website unreachable | url : %s" % url
        except urllib.error.HTTPError as e:
            HTTPError.append({"url": url, "Exception": str(e)})
        except urllib.error.URLError as e:
            URLError.append({"url": url, "Exception": str(e)})
        except Exception as e:
            OtherError.append({"url": url, "Exception": str(e)})
            # raise Exception(str(e) + "\nurl : %s" % url)
    finalDic = {"HTTPError": HTTPError,
                "URLError" : URLError,
                "OtherError": OtherError}
    if returnErrors: return finalDic
    else:
        if len(HTTPError)!=0 or len(URLError)!=0 or len(OtherError)!=0:
            raise Exception(str(finalDic))

def checkUrl(url):
    """
    If errors detected returns "TYPE : <ExceptionType> | "+str(e)
    Else return "OK"
    """
    try:
        status = urllib.request.urlopen(url).getcode()
        if status == 200:
            return "OK", "OK"
        else:
            text = f"Unexpected HTTP status returned : {status}"
            if status in httpStatus.keys(): text += f" ({httpStatus[status]})"
            return "StatusError", text
    except urllib.error.HTTPError as e:
        return "HTTPError", str(e)
    except urllib.error.URLError as e:
        return "URLError", str(e)
    except Exception as e:
        return "OtherError", str(e)

