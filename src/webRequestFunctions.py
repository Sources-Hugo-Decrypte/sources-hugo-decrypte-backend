# functions to test urls

import urllib.request, urllib.error


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

def checkUrl(url):
    """
    If errors detected returns (<ExceptionType>, <error>)
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

