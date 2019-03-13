import urllib
import backoff

def fatal_http_code(e):
    return 400 <= e.code < 500

@backoff.on_exception(backoff.expo,
                        urllib.error.HTTPError,
                        max_tries=3,
                        giveup=fatal_http_code)
def request_with_retry(img_url):
    return urllib.request.urlopen(img_url)
