import glob

def read_data(pattern):
    data = []
    files = glob.glob(pattern)
    for name in files:
        f = open(name, 'r')
        label = list(next(f).strip())
        features = [[int(b) for b in c.split()] for c in f]
        data.append((label, features))
    
    return data

def print_model(theta, state_file, trans_file):
    files = [state_file, trans_file]
    for (params, name) in zip(theta, files):
        f = open(name, 'w')
        for row in params:
            for cell in row:
                f.write(str(cell)+" ")
            f.write("\n")
        f.close()

def read_model(model_dir):
    theta = []
    files = ['state-params.txt', 'transition-params.txt']
    for name in files:
        f = open(model_dir + '/' + name, 'r')
        params = [[float(d) for d in line.split()] for line in f]
        theta.append(params)

    return theta

def score(predictions, data):
    true_count = sum([sum([c1 == c2 for c1, c2 in zip(prediction, label)])
                      for prediction, (label, _) in zip(predictions, data)])
    total_count = sum([len(prediction) for prediction in predictions])
    accuracy = 1.0 * true_count / total_count

    return accuracy