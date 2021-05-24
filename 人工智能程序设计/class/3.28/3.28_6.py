class BMI:
    def __init__(self, height, weight):
        self.BMI = weight/(height*height)

    def printBMI(self):
        print('%.1f'%self.BMI)


class ChinaBMI(BMI):
    def __init__(self, height, weight):
        super().__init__(height, weight)
        if self.BMI<18.5:
            self.type = 'Skinny'
        elif self.BMI<23.9:
            self.type = 'Normal'
        elif self.BMI<26.9:
            self.type = 'Fat'
        elif self.BMI<29.9:
            self.type = 'Obesity'
        else:
            self.type = 'Severe obesity'
    def printBMI(self):
        print('Your bmi is %.1f.'%self.BMI)
        print(self.type)


x = input().split(',')
Bx = ChinaBMI(float(x[0]), float(x[1]))
Bx.printBMI()