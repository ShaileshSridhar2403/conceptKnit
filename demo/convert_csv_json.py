import csv
import json

with open('../data/spaEN_test.csv', 'r') as file:
    reader = csv.reader(file)
    examples = []
    count = 0
    for row in reader:
        count += 1
        if (count == 1000):
            break
        if count == 1:
            continue
        correct_sentence = row[0]
        incorrect_sentence = row[1]
        error_index = int(row[2])
        if error_index == -1:
            continue
        error = row[3]
        if incorrect_sentence[-1] == '.' or incorrect_sentence[-1] == '?':
            sent_tokens = incorrect_sentence[:-1].split()
        else:
            sent_tokens = incorrect_sentence.split()
#        print(sent_tokens)
        error_index = sent_tokens.index(error)
        examples.append([error, sent_tokens[0:error_index], sent_tokens[error_index+1:]])
    print(examples)
    with open('../data/spaEN_test.json', 'w') as f:
        json.dump(examples, f)
