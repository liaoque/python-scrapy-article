import numpy as np
import pandas as pd

if __name__ == '__main__':

    data = {'Name': ['John', 'Helen', 'Sona', 'Ella'],
            'score': [82, 98, 82, 87],
            'option_course': ['C#', 'Python', 'Java', 'C']}
    df = pd.DataFrame(data)
    grouped = df.groupby('score')
    for _, item in grouped:
        print([ {'a': x[0], 'b': x[1]}  for x in item.sort_values(by='option_course').values ] )
