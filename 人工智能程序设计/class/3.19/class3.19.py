poem = 'Life can be good, Life can be sad, Life is mostly cheerful, But sometimes sad.'
word_list = {}

for item in poem.split():
    if item[-1] in ',.':
        item = item[:-1]
    if item not in word_list.keys():
        word_list[item] = 1
    else:
        word_list[item] += 1
print(word_list)
