from typing import List, Union, Optional

import pandas as pd
import plotly.graph_objects as go


class Visualizer:
   """A visualization automator of a dataset.
   """
   df: Optional[pd.DataFrame]
   categorical: List[str]
   ordinal: List[str]
   numerical: List[str]

   def __init__(self) -> None:
      """Initialize the dataset and classify the columns
      based on their data types.
      """
      self.df = None
      self.categorical = []
      self.ordinal = []
      self.numerical = []

   def is_empty(self) -> bool:
      """Check if the visualizer currently reads a dataset
      """
      return self.df is None

   def read_data(self, data=pd.DataFrame, ordinal: Optional[List[str]] = None) -> None:
      """Initialize the dataset and classify the columns
      based on their data types.

      - All columns in <data> must already be in the appropriate data type
      - Need to manually specify which categorical variables are ordinal
      """
      # Clean the visualizer if already read a dataset
      if not self.is_empty():
         self.__init__()
         
      self.df = data
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

      if ordinal is not None:
         # Make sure the ordinal variables are already in the categorical list
         try:
            for col in ordinal:
               assert col in self.categorical
            # Initialize the ordinal variable list
            self.ordinal = ordinal
         except AssertionError as error: 
            print('The ordinal list is not yet registered as categorical. ' +
            'Make sure all variables are string or object before registering it as ordinal.')

   def create_summary_table(self) -> pd.DataFrame:
      """Create a summary table for the set of variables indicated by <cols>.
      """
      raise NotImplementedError

   def get_visualizations(self) -> Optional[go.Figure]:
      """Create the visualizations of variables info.
      """
      raise NotImplementedError