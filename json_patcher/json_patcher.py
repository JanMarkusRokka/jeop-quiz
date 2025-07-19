import json
import sys
from pathlib import Path

if __name__ == "__main__":
    arg = sys.argv
    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for category_id in data['categories'].keys():
            for question in data['categories'][category_id]:
                if not isinstance(question, str):
                    if len(question) == 4:
                        question.append([])
                    if isinstance(question[2], str):
                        pathlib_path = Path(question[2])
                        if pathlib_path.exists() and question[2] != '':
                            question[2] = [question[2]]
                        else:
                            question[2] = []

        data_str = json.dumps(data, indent=4)
        with open('patched.json', 'w', encoding='utf-8') as f:
            f.write(data_str)
        input('Success, press enter to close (or close from the window toolbar)')