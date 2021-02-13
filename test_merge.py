import json
from json_to_csv import json_to_csv

file1 = "SetData/Base Set.json"
file2 = "SetData/Team Rocket.json"
testfilename = "testfile.json"

f1 = open(file1)
f2 = open(file2)

data1 = json.load(f1)
data2 = json.load(f2)

data3 = data1 + data2
dataf = json.dumps(data3, indent=2)
f = open(testfilename, "w")
f.write(dataf)
f.close()
json_to_csv("testfile")