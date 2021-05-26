# ML model (assumption)
# y = 100 + x1*5 + x2*3 + ... + x25*5

# y.predict(temp[x1], temp[x2], ..., temp[x25])
import random


class IRFS:

    @staticmethod
    def fake_score(temp, features):
        y = 100

        for feature in features:
            # print(feature)
            # print(temp[feature])
            coef = random.randint(1, 15)
            y += coef * int(temp[feature])

        return y
