#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import re
import socket
import asyncio
import argparse
import logging
from asyncio import get_event_loop
from jedi.api import Script

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=0)
parser.add_argument('--include-detail', action='store_true')
options, unknown_args = parser.parse_known_args()
if unknown_args:
    logging.warn('Get unknown arguments: {}'.format(' '.join(unknown_args)))

_tasks = []
_cache = {}


def _to_complete_item(c, include_detail=options.include_detail) -> dict:
    d = dict(
        word=c.name,
        abbr=c.name,
        icase=1,
    )
    if include_detail:
        # To obtain these information, sometimes jedi takes TOO LONG TIME.
        d.update(dict(
            menu=c.description,  # for item selection menu
            info=c.docstring(),  # for preview window
        ))
    return d


async def fuzzy_match(completions, word: str):
    result = []
    exact_re = re.compile(r'^' + word)
    icase_re = re.compile(r'^' + word, re.I)
    fuzzy_re = re.compile(r'^' + r'.*'.join(word), re.I)
    exact_match = []
    icase_match = []
    fuzzy_match = []
    for c in completions:
        name = c.name
        if exact_re.match(name):
            exact_match.append(_to_complete_item(c))
        elif icase_re.match(name):
            icase_match.append(_to_complete_item(c))
        elif fuzzy_re.match(name):
            fuzzy_match.append(_to_complete_item(c))
    result.extend(exact_match)
    result.extend(icase_match)
    result.extend(fuzzy_match)
    return result


def normal_match(completions):
    result = [_to_complete_item(c) for c in completions]
    return result


async def complete(msg, transport):
    handle = msg[0]
    info = msg[1]
    col = info['col']
    line = info['line']
    text = info['text']
    path = info['path']
    root = info.get('root')
    if root and root not in sys.path:
        sys.path.append(root)
    cur_line = text[line - 1][:col-1]
    match = re.search(r'\w+$', cur_line)
    if match:
        word = match.group(0)
    else:
        word = ''
    start_col = col - 1 - len(word)
    line_text = cur_line[:start_col]
    resp = [start_col+1]
    if not (path == _cache.get('path') and line == _cache.get('line') and
            len(text) == len(_cache.get('text')) and
            line_text == _cache.get('line_text')):
        script = Script('\n'.join(text), line=line, column=start_col)
        completions = tuple(script.completions())
        _cache.update(path=path, line=line, text=text, line_text=line_text,
                      completions=completions)
    else:
        completions = _cache.get('completions')

    if word:
        result = await fuzzy_match(completions, word)
    else:
        result = normal_match(completions)

    if result:
        resp.append(result)
        resp.append(path)
        if not transport._closing:
            transport.write(json.dumps([handle, resp]).encode('utf-8'))
    del result


class IOServer(asyncio.Protocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_data = ''
        self.task = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        while _tasks:
            _t = _tasks.pop()
            _t.cancel()

        msg = json.loads(data.decode('utf-8'))
        if msg[1].get('clear_cache'):
            _cache.clear()
        else:
            self.task = asyncio.ensure_future(complete(msg, self.transport))
            _tasks.append(self.task)

    def eof_received(self):
        if self.task in _tasks and not self.task.done():
            _tasks.remove(self.task)
            self.task.cancel()
        return None


async def run():
    loop = asyncio.get_event_loop()
    server = await loop.create_server(
        IOServer, host='localhost', port=options.port)
    return server


def main():
    loop = get_event_loop()
    server = loop.run_until_complete(run())
    for sock in server.sockets:
        if sock.family == socket.AF_INET:
            port = sock.getsockname()[1]
            print('{}\n'.format(port))
            sys.stdout.flush()
            break
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.stop()


if __name__ == '__main__':
    main()
