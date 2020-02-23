import pickle

with open(r"punctuation_pos_pickle", "rb") as input_file:
    punctuation_pos = pickle.load(input_file)
punctuation_pos += "."


with open(r"texts/raw_text", "rb") as input_file:
    lines = input_file.read().splitlines()
# print(lines)
count = 0
text = ""

for line in lines:
    # print(line)
    text += line.decode('utf-8').strip()
    text += punctuation_pos[count]
    count += 1

print(text)
