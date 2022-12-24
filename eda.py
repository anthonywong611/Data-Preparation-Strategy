from __future__ import annotations
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots


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

   def get_categorical_info(self, *args) -> Optional[go.Figure]:
      """Return the categorical visualizations of the columns 
      specified in the keyword arguments.
      
      -------------------------------------
      Preconditions:
      -------------------------------------
      - At least 1 keyword argument
      - Maximum of 4 keyword arguments
      - Null values should have been dealt with
      
      =============
      Two or More Variables
      =============
      - (Table, Bar)

      """
      cols = [arg for arg in args if arg in self.categorical]
      n = len(cols)
      # See if all the arguments are categorical variables
      assert n == len(args)
      try:
         # See if the number of arguments are in range
         if n == 0 or n > 4:
            raise ValueError
         # ---One Variable--- #
         if n == 1:
            return self.get_one_category(cols[0])
         # ---Two Variables--- #
         elif n == 2:
            return self.get_two_categories(cols)
         # ---Multiple Variables--- #
         else:
            return self.get_multiple_categories(cols)
      except ValueError:
         print("Please make sure that between 1 and 4 categorical column names are input. Try again.")

   def get_one_category(self, col: str) -> Optional[go.Figure]:
      """Create visualizations for the category <col> 
      depending on the number of its levels.

      Let n = # levels of category
         - if n = 1 them plot nothing
         - if 2 <= n <= 6 then (Table, Bar, Pie)
         - if n > 6 then (Table, Bar, Line)

      Conditions:
      ===============================================
      - Limit to at most 10 levels for bar chart
      - No limit for levels for line chart
      """
      n_levels = self._df[col].nunique()
      col_name = ' '.join([x.capitalize() for x in col.lower().split('_')])

      if n_levels == 1:
         print(f'There is only one level in {col}')
      elif n_levels >= 2 and n_levels <= 6:

         graphs_desc = [
            [
               {'type': 'table'}, 
               {'type': 'bar'}, 
               {'type': 'pie'}
            ]
         ] 
         fig = make_subplots(
            rows=1, 
            cols=3, 
            specs=graphs_desc, 
            subplot_titles=(
               '', 
               f'Top {n_levels} Counts by {col_name}', 
               f'Percentage of {col_name}'
            )
         )
         # update figure title
         fig.update_layout(title=f"Visualizations of {col_name}")
         # count total number of records under each level of <col>
         total_counts = self.create_count_table(col)

         # create graphs
         table = self.create_plotly_table(total_counts)
         bar_chart = self.create_bar_chart(col, total_counts)
         pie_chart = px.pie(total_counts, names=col, values='total_count').data[0]

         # append the graphs to the figure
         fig.add_trace(table, row=1, col=1)
         fig.add_trace(bar_chart, row=1, col=2)
         fig.add_trace(pie_chart, row=1, col=3)
         # update figure axes
         fig.update_xaxes(title_text=col_name, row=1, col=2)

         return fig

      else:
         graphs_desc = [
            [
               {'type': 'table'}, 
               {'type': 'bar'}, 
               {'type': 'scatter'}
            ]
         ]
         fig = make_subplots(
            rows=1, 
            cols=3, 
            specs=graphs_desc, 
            subplot_titles=(
               '', 
               f'Top {n_levels} Counts by {col_name}', 
               f'Cumulative Frequency of {col_name}'
            )
         )
         # update figure title
         fig.update_layout(title=f"Visualizations of {col_name}")
         # count total number of records under each level of <col>
         total_counts = self.create_count_table(col)
         # make sure the number of levels are limited to 10
         top_10_total_counts = total_counts.iloc[:10, :]

         # create graphs
         table = self.create_plotly_table(top_10_total_counts)
         bar_chart = self.create_bar_chart(col, top_10_total_counts)
         line_chart = self.create_line_chart(col, total_counts)

         # append the graphs to the figure
         fig.add_trace(table, row=1, col=1)
         fig.add_trace(bar_chart, row=1, col=2)
         fig.add_trace(line_chart, row=1, col=3)

         # update figure axes
         fig.update_xaxes(title_text=col_name, row=1, col=2)
         fig.update_xaxes(title_text='Number of Levels', row=1, col=3)
         fig.update_yaxes(title_text='Percentage', row=1, col=3)

         return fig
      
   def get_two_categories(self, cols: List[str]) -> go.Figure:
      pass

   def get_multiple_categories(self, cols: List[str]) -> go.Figure:
      pass

   def create_count_table(self, cols: Union[str, List[str]]) -> pd.DataFrame:
      """Create a summary table counting the total number of 
      observations grouping by the columns in <cols>.
      """
      cols_info = self._df.groupby(by=cols, as_index=False).size()
      sorted_cols_info = cols_info.sort_values(by='size', ascending=False)
      # Update the column names
      if isinstance(cols, str):
         sorted_cols_info.columns = [cols, 'total_count']
      else:
         sorted_cols_info.columns = cols + ['total_count']

      return sorted_cols_info

   def create_plotly_table(self, df: pd.DataFrame) -> go.Table:
      """Create a plotly graph object table of the dataframe <df>.
      """
      return go.Table(
         header={"values": df.columns}, cells={'values': df.T.values}
      )

   def create_bar_chart(self, cols: Union[str, List[str]], df: pd.DataFrame) -> go.Bar:
      """
      """
      if isinstance(cols, str):
         return px.bar(df, x=cols, y='total_count', text_auto=True).data[0]
      else:
         pass

   def create_line_chart(self, col: str, df: pd.DataFrame) -> go.Line:
      """Create a line chart showing the percentage of records taken up
      by the unique levels in <col>. <df> is the table showing the total 
      number of records under each level sorted in descending order.

      df columns: [col, 'total_count']
      """
      n_non_null_in_col = self._df.shape[0] - np.sum(self._df[col].isna())
      # calculate the cumulative frequency of the levels of <col>
      df['cum_freq'] = df['total_count'].cumsum() / n_non_null_in_col

      # calculate the number of top levels needed to make up for each 
      # percent of the entire dataset on a 5% increment
      percents = [percent / 100 for percent in range(10, 101, 5)]
      n_col_level = [df[df['cum_freq'] <= p].shape[0] for p in percents]

      col_percentage = pd.DataFrame(
         {
            'num_level': n_col_level, 
            'percentage': percents
         }
      )
      # Check the minimum number of levels that accounts for 95% of the entire dataset
      ninety_five = col_percentage[col_percentage['percentage'] == 0.95]

      # create the line graph
      fig = px.line(col_percentage, x='num_level', y='percentage', markers=True)

      return fig.data[0]

