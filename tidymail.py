#!/usr/bin/env python

import email
import email.parser
import email.generator
import sys
import re

sig = """--
Rob Hague | http://rob.rho.org.uk
Filtered by tidymail (http://github.com/robhague/tidymail)
"""

quoteLinesRe = re.compile('^(>(\s*>)*)?(.*)$')

def subfn(regexpstr, replacement, flags = 0):
    regexp = re.compile(regexpstr, flags)
    return lambda X: re.sub(regexp, replacement, X)

def eliminateQuotedSignatures(msg):
    quote, isSig, result = "", False, []
    for line in msg.split('\n'):
        m = quoteLinesRe.match(line)
        newQuote = m.group(1)
        isSig = newQuote and (
            (isSig and newQuote == quote) or (m.group(3).strip() == '--'))
        if not isSig:
            result.append(line)
        quote = newQuote
    return '\n'.join(result)+'\n'
            

substitutions = [
    # Normalise line ends
    subfn(r'\r\n?', '\n'),

    # Eliminate quoted signatures
    eliminateQuotedSignatures,

    # Eliminate trailing quoted lines
    subfn(r'^(>\s*)+?\n(?!^>)\n*', '\n', re.MULTILINE),

    # Replace signature
    subfn(r'^--$.*\Z', sig, re.MULTILINE | re.DOTALL),

    # Enforce RFC 2822 line ends
    subfn(r'\n','\r\n')
    ]

def filter_message(msg, isfirst, islast):
    if (msg.is_multipart()):
        msg['X-TidyMail'] = 'Yes-MultiPart'
        p = msg.get_payload()
        if len(p) > 1:
            filter_message(p[0], True, False)
            map(lambda m: filter_message(m, False, False), p[1:-1])
            filter_message(p[-1], False, True)
        else:
            filter_message(p[0], True, True)
    elif msg.get_content_type() == "text/plain":
        payload = msg.get_payload()
        for fn in substitutions:
             payload = fn(payload)
        if isfirst:
            payload = payload.lstrip()
        if islast:
            payload = payload.rstrip()+'\r\n'
        msg.set_payload(payload)
        msg['X-TidyMail'] = 'Yes'
                   
if __name__ == '__main__':
    msg = email.parser.Parser().parse(sys.stdin)
    mailer = msg['X-Mailer'] or ''
    if mailer.find('iPhone') > -1 or mailer.find('iPad') > -1:
        filter_message(msg, True, True)
    email.generator.Generator(sys.stdout).flatten(msg)
