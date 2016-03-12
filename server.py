#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import re
import socket
import asyncio
import argparse
from asyncio import get_event_loop
from jedi.api import Script


def _to_complete_item(c) -> dict:
    return dict(word=c.name, abbr=c.name, menu=c.description,
                info=c.docstring(), icase=1,)


async def find_completes(text, line, col, path, word):
    if word:
        return await fuzzy_match(text, line, col, path, word)
    else:
        return await normal_match(text, line, col, path)


async def fuzzy_match(text, line, col, path, word:str):
    s = Script('\n'.join(text), line=line, column=col - len(word) - 1,
               path=path)
    await asyncio.sleep(0)
    result = []
    exact_re = re.compile(r'^' + word)
    icase_re = re.compile(r'^' + word, re.I)
    fuzzy_re = re.compile(r'^' + r'.*'.join(word), re.I)
    exact_match = []
    icase_match = []
    fuzzy_match = []
    for c in s.completions():
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
    await asyncio.sleep(0)
    return result


async def normal_match(text, line, col, path):
    s = Script('\n'.join(text), line=line, column=col - 1, path=path)
    await asyncio.sleep(0)
    result = [_to_complete_item(c) for c in s.completions()]
    await asyncio.sleep(0)
    return result


async def complete(msg, transport):
    handle = msg[0]
    info = msg[1]
    col = info['col']
    line = info['line']
    text = info['text']
    path = info['path']
    cur_line = text[line - 1][:col]
    match = re.search(r'\w+$', cur_line)
    if match:
        word = match.group(0)
    else:
        word = ''
    start_col = col - len(word)
    resp = [start_col]

    result = await find_completes(text, line, col, path, word)
    if result:
        resp.append(result)
        transport.write(json.dumps([handle, resp]).encode('utf-8'))
    else:
        # print('No result, close connection')
        transport.close()

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=0)

_tasks = []


class IOServer(asyncio.Protocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_data = ''
        self.task = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        while _tasks:
            _tasks.pop().cancel()

        msg = json.loads(data.decode('utf-8'))
        self.task = asyncio.ensure_future(complete(msg, self.transport))
        _tasks.append(self.task)

    def eof_received(self):
        if self.task in _tasks and not self.task.done():
            _tasks.remove(self.task)
            self.task.cancel()
        return None


async def run():
    options = parser.parse_args()
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
