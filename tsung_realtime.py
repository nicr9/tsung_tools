#! /usr/bin/env python2.7
from flask import Flask, Response, json
from sys import argv
from os.path import join as path_join
from os.path import isfile
from os import walk as path_walk
from collections import defaultdict

root_path = argv[1]
log_path = path_join(root_path, 'tsung.log')

app = Flask(__name__, static_url_path='')
where = defaultdict(int)
timestamp = 0
data = defaultdict(dict)

def process(data, line):
    global timestamp
    if line[0] == '#':
        timestamp = line.split(' ')[-1]
    else:
        results= line.split(' ')
        if results[0] == 'stats:':
            if len(results) == 4:
                data[results[1]+'_count'][timestamp] = results[2]
                data[results[1]+'_total'][timestamp] = results[3]
            elif len(results) == 9:
                data[results[1]+'_10count'][timestamp] = results[2]
                data[results[1]+'_10mean'][timestamp] = results[3]
                data[results[1]+'_stddev'][timestamp] = results[4]
                data[results[1]+'_max'][timestamp] = results[5]
                data[results[1]+'_min'][timestamp] = results[6]
                data[results[1]+'_mean'][timestamp] = results[7]
                data[results[1]+'_count'][timestamp] = results[8]
            else:
                print line, '|', results

def update_data(path):
    global where, data
    full_path = path_join(path, log_path)
    with open(full_path, 'r') as inp:
        inp.seek(where[path])
        while True:
            line = inp.readline()
            if line:
                process(data, line)
                where[path] = inp.tell()
            else:
                break

def is_tsung_results(path):
    return isfile(path_join(path, 'tsung.log'))

def links(details):
    elems = ['<li><a href=%s/all>%s</a></li>' % (href, path)
            for href, path in details.iteritems()]
    joined = '\n'.join(elems)
    return '<ul>%s</ul>' % joined

@app.route('/')
def index():
    dirs = next(path_walk('.'))[1]
    tsung_hrefs = {path:path for path in dirs if is_tsung_results(path)}
    return Response(
            links(tsung_hrefs),
            status=200,
            mimetype='text/html'
            )

@app.route('/<path:path>/all')
def all_data(path):
    update_data(path)
    return Response(json.dumps(data), status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
