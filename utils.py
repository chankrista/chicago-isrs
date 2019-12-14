import pandas as pd
from bokeh.palettes import Viridis, Category20
from bokeh.plotting import figure, output_file, show



def time_graph(isrs, column=None):
    
    p = figure(x_axis_type="datetime")
    isrs['month_year'] = pd.to_datetime(isrs['month_year'])
    if column:
        by_month = pd.DataFrame(isrs.groupby(
        [column, 'month_year']).size()).reset_index().rename(
            {0: "isr_count"}, axis=1)
        for color, val in zip(Category20[8], by_month[column].unique()):
            df = by_month.loc[by_month[column] == val]
            p.line(df['month_year'], df['isr_count'],\
                   line_width=2, color=color, alpha=0.8, legend_label=str(val))
    else:
        by_month = pd.DataFrame(isrs.groupby(
            'month_year').size()).reset_index().rename(
            {0: "isr_count"}, axis=1)
        p.line(by_month['month_year'], by_month['isr_count'],\
                   line_width=2, alpha=0.8, legend_label=str("ISRs"))

    show(p)