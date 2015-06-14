#! /usr/bin/env python2.7
from flask import Flask, Response, json
from sys import argv
from os.path import join as path_join
from collections import defaultdict

root_path = argv[1]
log_path = path_join(root_path, 'tsung.log')

app = Flask(__name__, static_url_path='')
where = 0
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

def update_data():
    global where, data
    with open(log_path, 'r') as inp:
        inp.seek(where)
        while True:
            line = inp.readline()
            if line:
                process(data, line)
                where = inp.tell()
            else:
                break

@app.route('/all')
def all_data():
    update_data()
    return Response(json.dumps(data), status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
