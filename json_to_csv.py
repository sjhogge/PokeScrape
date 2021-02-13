import pandas as pd

def json_to_csv(filename):
    filename = filename[:-5]
    filename_json = filename + ".json"
    filename_csv = filename + ".csv"
    df = pd.read_json(filename_json)
    df.to_csv(filename_csv, index=None)
    print("Data converted to CSV")

if __name__ == "__main__":
    filename = "AllSetsData.json"
    json_to_csv(filename)