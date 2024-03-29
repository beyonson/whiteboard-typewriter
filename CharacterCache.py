# English Letter Frequency data obtained from: https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html

class CharacterCache:
    _RECENCYWEIGHT = 5
    _FREQUENCYMULT = 1
    def __init__(self,size=10):
        self.size = size
        self.cache = []
        self.priority = []
        self.letterFreq = {
            "E" : 12.02,
            "T" : 9.10,
            "A" : 8.12,
            "O" : 7.68,
            "I" : 7.31,
            "N" : 6.95,
            "S" : 6.28,
            "R" : 6.02,
            "H" : 5.92,
            "D" : 4.32,
            "L" : 3.98,
            "U" : 2.88,
            "C" : 2.71,
            "M" : 2.61,
            "F" : 2.30,
            "Y" : 2.11,
            "W" : 2.09,
            "G" : 2.03,
            "P" : 1.82,
            "B" : 1.49,
            "V" : 1.11,
            "K" : 0.69,
            "X" : 0.17,
            "Q" : 0.11,
            "J" : 0.10,
            "Z" : 0.07
        }
    def add(self,letter,lines):
        weight = CharacterCache._RECENCYWEIGHT + round(self.getFrequency(letter) * CharacterCache._FREQUENCYMULT)
        for i in range(len(self.cache)):
            if self.cache[i][0] == letter:
                self.priority[i] = weight
                return
        if len(self.cache) < self.size:
            self.cache.append(tuple((letter,lines)))
            self.priority.append(weight)
        else:
            min = 100
            lowest = -1
            for i in range(len(self.priority)):
                if self.priority[i] < min:
                    lowest = i
                    min = self.priority[i]
            if weight >= min:
                self.cache[lowest] = tuple((letter,lines))
                self.priority[lowest] = weight
    def poll(self,letter):
        lines = ""
        for i in range(len(self.priority)):
            if self.priority[i] > 0:
                self.priority[i] -= 1
        for lt in self.cache:
            if lt[0] == letter:
                lines = lt[1]
        return lines
    def getFrequency(self,letter):
        return self.letterFreq[letter]
    def clear(self):
        self.cache = []
        self.priority = []
    def print(self):
        contents = ""
        frequency = ""
        for i in range(len(self.cache)):
            contents += str(self.cache[i][0]) + " "
            frequency += str(self.priority[i]) + " "
        print(contents)
        print(frequency)
