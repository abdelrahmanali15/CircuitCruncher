import numpy as np

def save_table_html(df_table, output_html):
    with open(output_html+'.html', 'w') as file:
        file.write(
            df_table.style.set_table_styles([
                {'selector': 'thead th', 'props': [('background-color', '#aec6cf'), ('color', 'black'), ('text-align', 'center')]},
                {'selector': 'tbody td', 'props': [('text-align', 'center'), ('padding', '10px'), ('border', '2px solid #ddd')]},
                {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
                {'selector': 'tbody tr:hover', 'props': [('background-color', '#ffcccc')]}
            ]).set_caption(output_html)
            .set_table_attributes('class="dataframe minimalist-table"')
            .hide(axis='index')
            .to_html()
        )
    print(f"Table saved as {output_html}.html")

    # Save table as TXT
def save_table_txt(table, output_txt):
    with open(output_txt+'.txt', 'w') as file:
        file.write(str(table))
    print(f"Table saved as {output_txt}.txt")



def format_value(val):
        if np.isnan(val):
            return "NaN"
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"{val/1e12:.2f}T"
        elif abs_val >= 1e9:
            return f"{val/1e9:.2f}G"
        elif abs_val >= 1e6:
            return f"{val/1e6:.2f}M"
        elif abs_val >= 1e3:
            return f"{val/1e3:.2f}k"
        elif abs_val >= 1:
            return f"{val:.2f}"
        elif abs_val >= 1e-3:
            return f"{val*1e3:.2f}m"
        elif abs_val >= 1e-6:
            return f"{val*1e6:.2f}μ"
        elif abs_val >= 1e-9:
            return f"{val*1e9:.2f}n"
        elif abs_val >= 1e-12:
            return f"{val*1e12:.2f}p"
        elif abs_val >= 1e-15:
            return f"{val*1e15:.2f}f"
        else:
            return f"{val*1e18:.2f}a"