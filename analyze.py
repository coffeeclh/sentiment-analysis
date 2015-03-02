import sys
import re
import json

def main(argv):
    # Load the positive and negative words
    words = {}
    with open("words/positive.txt") as file:
        for line in file:
            words[line.rstrip()] = 1

    with open("words/negative.txt") as file:
        for line in file:
            words[line.rstrip()] = -1

    colors = {1: '\033[92m', -1: '\033[91m'}
    END_COLOR = '\033[0m'

    # Perform the sentiment analysis
    for jsonObject in sys.stdin:
        data = json.loads(jsonObject)
        # normalize newlines
        message = data["body"].replace('\r\n','\n')
        score = 0
        found = 0
        disp = ""
        for w in message.split():
            # Only keep alphanumeric and some punctuation characters
            w = re.sub(r'[^\-\'+\w]', '', w).lower()
            if w in words:
                score += words[w]
                found += 1
                disp += colors[words[w]] + w + END_COLOR + " "

        print("{}\t{:.2f}\t{}{}".format(data["id"], score / float(found) if found != 0 else 0.0, disp, message.replace('\n',' ')))

if __name__ == "__main__":
    main(sys.argv[1:])
