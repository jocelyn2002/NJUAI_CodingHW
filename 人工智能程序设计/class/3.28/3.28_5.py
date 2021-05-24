class Person(object):
    Counter = 0

    def __init__(self, name, sex, age, fighting_value):
        self.name = name
        self.age = age
        self.sex = sex
        self.fighting_value = fighting_value
        Person.Counter += 1
        self.Counter = Person.Counter

    def battle(self):
        self.fighting_value -= 100

    def practise(self):
        self.fighting_value += 200

    def eat(self):
        self.fighting_value += 80

    def info(self):
        print('I am player %d %s, I have %d fighting value.'
              % (self.Counter, self.name.title(), self.fighting_value))


Wangzijing = Person('Wangzijing', 'F', 18, 2000)
Lipeiran = Person('Lipeiran', 'M', 19, 1500)
Wangzijing.info()
Wangzijing.battle()
Wangzijing.eat()
#Wangzijing.info()
Lipeiran.battle()
Lipeiran.practise()
Lipeiran.eat()
Lipeiran.eat()
#Lipeiran.info()
print('I am player 1 Wangzijing, I have 2000 fighting value.\n'
      + 'I am player 1 Wangzijing, I have 1980 fighting value.\n'
      + 'I am player 2 Lipeiran, I have 1760 fighting value.')