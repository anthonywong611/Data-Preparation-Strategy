from typing import List, Union

import pandas as pd


class Visualizer:
   """A visualization automator of a dataset.
   """
   _df: pd.DataFrame
   categorical: List[str]
   numerical: List[str]

   def __init__(self, data=pd.DataFrame) -> None:
      """Initialize the dataset and classify the columns
      based on their data types.
      """
      self._df = data
      self.categorical = []
      self.numerical = []

      for column in data.columns:
         if data[column].dtype == int:
            self.numerical.append(column)
         elif data[column].dtype == float:
            self.numerical.append(column)
         elif data[column].dtype == str:     
            self.categorical.append(column)
         elif data[column].dtype == bool:
            self.categorical.append(column)
         elif data[column].dtype == object:
            self.categorical.append(column)

   def create_summary_table(self, cols: Union[str, List[str]]) -> pd.DataFrame:
      """Create a summary table for the set of variables indicated by <cols>.
      """
      raise NotImplementedError