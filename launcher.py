from Dataset import Dataset
from datetime import datetime

start_time = datetime.now()
print(f"Start time: {start_time}")
dataset = Dataset("Dataset/SerieA-2018-2019.json", "SerieA.csv")
dataset.create()

end_time = datetime.now()
print(f"Execution time {end_time - start_time}")
## Execution time 0:30:24.180171
