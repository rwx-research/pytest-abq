import os
import sys
import json

def sanitize_results(results):
    for result_list in results:
        for result in result_list:
            result["result"]["runtime"]["Nanoseconds"] = "STRIPPED"
            result["result"]["stderr"] = "STRIPPED"
            result["result"]["stdout"] = "STRIPPED"
            result["result"]["timestamp"] = "STRIPPED"
    return results

def sanitize_manifest(results):
    return results

file = sys.argv[1]
if 'results' in file:
    strategy = sanitize_results
else:
    strategy = sanitize_manifest

file = os.path.realpath(file)

with open(file, 'r+') as f:
    data = json.load(f)
    output = strategy(data)
    f.seek(0)
    json.dump(output, f, indent=2)
    f.truncate()
