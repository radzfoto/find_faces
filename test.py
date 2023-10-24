class MyIterator:
    def __init__(self, end):
        self.current = 0
        self.end = end

    def __iter__(self):
        return self.generator()

    def generator(self):
        while self.current < self.end:
            yield self.current
            self.current += 1

# Usage:
it = MyIterator(3)
for i in it:
    print(i)  # Output: 0 1 2
