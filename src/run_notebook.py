import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

notebook_path = os.path.join("notebooks", "m5_eda_and_data_cleaning.ipynb")

print(f"Reading notebook from {notebook_path}...")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

print("Executing notebook cells...")
notebook_dir = os.path.abspath("notebooks")
ep.preprocess(nb, {'metadata': {'path': notebook_dir}})

print("Saving executed notebook...")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Notebook execution and output population complete!")
