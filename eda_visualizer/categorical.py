from __future__ import annotations

from base import Visualizer
from typing import List, Optional, Union, Tuple
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class CategoricalVisualizer(Visualizer):
   """A visualization automator specializing in
   categorical variables.
   """
   df: Optional[pd.DataFrame]
   categorical: List[str]
   ordinal: List[str]
   numerical: List[str]

   def __init__(self) -> None:
      """Initialize the attributes.
      """
      super().__init__()

   def create_summary_table(self, cols: Union[str, List[str]]) -> pd.DataFrame:
      """Create a summary table counting the total number of 
      observations grouping by the columns in <cols>.
      """
      cols_info = self.df.groupby(by=cols, as_index=False).size()
      sorted_cols_info = cols_info.sort_values(by='size', ascending=False)
      # Update the column names
      if isinstance(cols, str):
         sorted_cols_info.columns = [cols, 'total_count']
      else:
         sorted_cols_info.columns = cols + ['total_count']

      return sorted_cols_info

   def get_visualizations(self, *args) -> Optional[go.Figure]: 
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

         try:
            # ---One Variable--- #
            if n == 1:
               return self.get_one_category(cols[0])
            # ---Two Variables--- #
            elif n == 2:
               return self.get_two_categories(cols)
            # ---Multiple Variables--- #
            else:
               return self.get_multiple_categories(cols)
         except ValueError as error:
            print(error)
         
      except ValueError:
         print("Please make sure that between 1 and 4 " + 
         "categorical column names are input. Try again.")

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
      n_levels = self.df[col].nunique()
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
         total_counts = self.create_summary_table(col)

         # create graphs
         table = self.create_plotly_table(total_counts)
         # should return as many bar graphs as the number of unique levels
         bars = self.create_bar_chart(col, total_counts)  
         pie_chart = px.pie(total_counts, names=col, values='total_count').data[0]

         # table to the first column
         fig.add_trace(table, row=1, col=1)
         # bars to the second column
         for level in range(n_levels):
            fig.add_trace(bars[level], row=1, col=2)
         # pie chart to the third column
         fig.add_trace(pie_chart, row=1, col=3)
         # update figure axes
         fig.update_xaxes(title_text=col_name, row=1, col=2)

         return fig

      else:
         # Limit the number of columns to 10 if necessary
         allowed_n_levels = min(n_levels, 10)
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
               f'Top {allowed_n_levels} Counts by {col_name}', 
               f'Cumulative Probability of {col_name} Levels'
            )
         )
         # update figure title
         fig.update_layout(title=f"Visualizations of {col_name}")
         # count total number of records under each level of <col>
         total_counts = self.create_summary_table(col)
         # make sure the number of levels are limited to at most 10
         top_total_counts = total_counts.iloc[:allowed_n_levels, :]

         # create graphs
         table = self.create_plotly_table(top_total_counts)
         # should return at most 10 bar graphs 
         bars = self.create_bar_chart(col, top_total_counts)
         cum_prob = self.create_cum_freq_plot(col, total_counts)

         # append the table to the first column
         fig.add_trace(table, row=1, col=1)
         # append the bars to the second column
         for level in range(allowed_n_levels):
            fig.add_trace(bars[level], row=1, col=2)
         # append the cumulative probability distribution plot to the third column
         fig.add_trace(cum_prob, row=1, col=3)

         # update figure axes
         fig.update_xaxes(title_text=col_name, row=1, col=2)
         fig.update_xaxes(title_text='Number of Levels', row=1, col=3)
         fig.update_yaxes(title_text='Percentage', row=1, col=3)

         return fig
      
   def get_two_categories(self, cols: List[str]) -> go.Figure:
      pass

   def get_multiple_categories(self, cols: List[str]) -> go.Figure:
      pass

   def create_plotly_table(self, df: pd.DataFrame) -> go.Table:
      """Create a plotly graph object table of the dataframe <df>.
      """
      return go.Table(
         header={"values": df.columns}, cells={'values': df.T.values}
      )

   def create_bar_chart(self, cols: Union[str, List[str]], df: pd.DataFrame) -> Tuple[go.Bar]:
      """Create a bar chart showing the total count of the top levels under
      the column <cols>. Each bar will be identified with a different color.

      Preconditions:
      - <df> has at most 10 levels under <cols>
      """
      colors = px.colors.qualitative.Plotly  # 10 colors

      if isinstance(cols, str):
         n_levels = df.shape[0]
         fig = px.bar(
            df, x=cols, y='total_count', 
            text_auto=True, 
            color=colors[:n_levels],  # each color corresponds to a bar graph
            color_discrete_map='identity'
         )
         return fig.data
      else:
         levels = df.loc[:, cols]

   def create_cum_freq_plot(self, cols: Union[str, List[str]], df: pd.DataFrame) -> go.Line:
      """Create a cumulative frequency plot showing the percentage of records 
      taken up by the unique tuple of levels in <col>. <df> is the table showing 
      the total number of records under each level sorted in descending order.

      df columns: [col, 'total_count']
      """
      if isinstance(cols, str):
         n_non_null_in_col = self.df.shape[0] - np.sum(self.df[cols].isna())
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
      else:
         pass

