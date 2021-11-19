import math

import pandas as pd
import plotly.express as px

NUM = 20

#data1 = [25 + i * 30 for i in range(NUM)]
#data2 = [int(25 + i * 200 / math.sqrt((i + 10) * 1.05) - min(i ** 1.45,150)) for i in range(NUM)]

#data1 = [80 + i * 35 for i in range(NUM)]
#data2 = [int(80 + i * 205 / math.sqrt((i + 10) * 1.05) - min(i ** 1.45,150)) for i in range(NUM)]

data1 = [150 + i * 50 for i in range(NUM)]
data2 = [int(150 + i * 260 / math.sqrt((i + 10) * 1.05) - min(i ** 1.45,150)) for i in range(NUM)]

all_data = {
    'formula':['data1'] * NUM + ['data2'] * NUM,
    'x':list(range(NUM)) + list(range(NUM)),
    'y':data1 + data2
}

print(all_data)

df = pd.DataFrame(data = all_data)

fig = px.line(df, x="x", y="y", title='Upgrade cost by level', text='y')
fig.show()
