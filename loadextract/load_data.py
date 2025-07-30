from datasets import load_dataset

dataset = load_dataset("VTSNLP/vietnamese_curated_dataset")

print(dataset)
# print(dataset[train][0])

dataset['train'].to_csv("vietnamese_curated_dataset.csv")
