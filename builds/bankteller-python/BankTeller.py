#!/usr/bin/env python

# BankTeller v0.2
# Made by Matthijs Kaandorp

# Python code generates HTML code for output file.
# For each graph in output file, a function in Python code generates
# corresponding HTML code.

# The Plotly JavaScript library is used to create the graphs (Copyright (c) 2018 Plotly, Inc).

# Additional files are a Plotly JS library file (plotly-basic.min.js) to create the graphs and a categories (categories.txt) file.
# These files should be in the same directory.

import csv
import os
import sys
import timeit
try:
    from Tkinter import Tk
    import tkMessageBox as messagebox
    from tkFileDialog import askopenfilename
    from tkSimpleDialog import askstring
except ImportError:
    from tkinter import Tk, messagebox
    from tkinter.filedialog import askopenfilename
    from tkinter.simpledialog import askstring
from datetime import date, timedelta

# Global variables which hold data used for most graphs.
categories_dict_keywords = {}
# [Date, Desc, Bij/Af, Amount, DateType]
file_struct = {"date": 0, "desc": 0, "to-from": 0, "amount": 0, "datetype": -1}
data = []
list_income = []
list_expenses = []
first_date = None
last_date = None

# exp_per_date is used for multiple graphs, global to not recalculate.
exp_per_date = None

# Color scheme, twelve colors (for each month).
colors_number = ['rgb(244,67,54)', 'rgb(156,39,176)', 'rgb(63,81,181)', 'rgb(33,150,243)', 'rgb(0,188,212)', 'rgb(0,150,136)',
                 'rgb(139,195,74)', 'rgb(205,220,57)', 'rgb(255,235,59)', 'rgb(255,193,7)', 'rgb(255,152,0)', 'rgb(255,87,34)']

# Global variables set by user.
saldo = 0.0
bankfile_name = ""
curr_dir = os.path.dirname(os.path.abspath(__file__))

plotly_code = ""

# The HTML code.
html_content = """<html>
<head>
    <h1>
    <span style="color:{};">B</span>
    <span style="color:{};">a</span>
    <span style="color:{};">n</span>
    <span style="color:{};">k</span>
    <span style="color:{};">T</span>
    <span style="color:{};">e</span>
    <span style="color:{};">l</span>
    <span style="color:{};">l</span>
    <span style="color:{};">e</span>
    <span style="color:{};">r</span>
    </h1>
    <style>
    body, head {{font-family: 'Roboto', sans-serif;}}
    table {{border-collapse: collapse;}}
    th,td {{border-bottom: 1px solid #cecfd5;}}
    th,td {{padding: 10px 15px;}}
    </style>
</head>
<body>
<br>
<br>
""".format(*colors_number[:10])


# Functions used to read bank file into list of expenses and list of income and
# categories file into categories dictionary ----------------------------------------------------------------------

# Read categories file, create dictionary with categories and corresponding keywords
def read_categories():
    global categories_dict_keywords, file_struct
    try:
        with open(os.path.join(curr_dir, 'categories.txt'), 'r') as inp:
            status = 0
            # mode=0 for categories, mode=1 for filestructures
            mode = 0
            corr_struct = 0
            curr_cat = None
            for line in inp:
                if(line[0] != '#'):
                    line = line.rstrip()
                    if(status == 0):
                        if(line == ".CATEGORIES"):
                            mode = 0
                            new_status = 0
                        elif(line == ".FILESTRUCTURES"):
                            mode = 1
                            new_status = 0
                        elif(mode == 1):
                            if(line in bankfile_name):
                                corr_struct = 1
                                new_status = 1
                        elif(mode == 0):
                            curr_cat = line
                            categories_dict_keywords[curr_cat] = []
                            new_status = 1
                    elif(status == 1):
                        if(line == '{'):
                            new_status = 2
                        else:
                            print("error reading categories file")
                            break
                    elif(status == 2):
                        if(line == '}'):
                            new_status = 0
                        elif(mode == 1 and corr_struct == 1):
                            column_indices = line.split(",")
                            file_struct["date"] = int(column_indices[0])
                            file_struct["desc"] = int(column_indices[1])
                            file_struct["to-from"] = int(column_indices[2])
                            file_struct["amount"] = int(column_indices[3])
                            file_struct["datetype"] = int(column_indices[4])
                        elif(mode == 0):
                            categories_dict_keywords[curr_cat].append(line)
                    status = new_status
        categories_dict_keywords['other'] = []
    except:
        tkMessageBox.showinfo("Error", "Invalid categories.txt")


# Read the bank file into a 2d list.
def read_bank_file(bankfile_name):
    global data
    try:
        bank_file = open(bankfile_name+'.csv', 'r')
        data = list(csv.reader(bank_file))
    except UnicodeDecodeError:
        bank_file = open(bankfile_name+'.csv', 'r', encoding="latin-1")
        data = list(csv.reader(bank_file))
    data = data[1:]


# Checks for each entry if it's an expense or income, call corresponding function.
def check_bankfile():
    global data
    for row in data:
        if(row[file_struct["to-from"]] == "Af" or row[file_struct["to-from"]][0] == '-'):
            check_expense(row)
        elif(row[file_struct["to-from"]] == "Bij" or row[file_struct["to-from"]][0] == '+'):
            check_income(row)


# Adds an expense to a list of expenses, adds categorie and keyword
def check_expense(row):
    global total_expenses, all_keywords, categories_dict_cash, categories_dict_res, categories_dict_keywords
    cash_amount = row[file_struct["amount"]]
    if(cash_amount[0] == '+' or cash_amount[0] == '-'):
        cash_amount = cash_amount[1:]
    cash_amount = float(cash_amount.replace(",", "."))
    date = convert_date_to_pythonic(row[file_struct["date"]])
    description = row[file_struct["desc"]]
    curr_keyword = None
    for keyw in categories_dict_keywords:
        curr_keyword = my_any(description, categories_dict_keywords[keyw])
        if curr_keyword:
            list_expenses.append(
                [date, description, cash_amount, curr_keyword, keyw])
            break
    if(curr_keyword == None):
        list_expenses.append([date, description, cash_amount, None, 'other'])


# Adds income to a list of income.
def check_income(row):
    global list_income
    cash_amount = row[file_struct["amount"]]
    if(cash_amount[0] == '+' or cash_amount[0] == '-'):
        cash_amount = cash_amount[1:]
    cash_amount = float(cash_amount.replace(",", "."))
    date = row[file_struct["date"]]
    description = row[file_struct["desc"]]
    list_income.append(
        [convert_date_to_pythonic(date), description, cash_amount])


# Helper functions ------------------------------------------------------------------------------------

# Checks if any el in list1 is equal to el y in list2, returns equal el.
def my_any(list1, list2):
    for x in list2:
        curr_list = [x]
        if any(y in list1.lower() for y in curr_list):
            return x
    return None


# Groups a 2d list my_list by elements with index index_group, sums the elements
# with index sum, and creates a list of the elements with indices_list.
def group_by(my_list, index_group, index_sum, indices_list):
    new_list = []
    #print transpose(my_list)[0]
    my_list = sorted(my_list, key=lambda x: x[index_group])
    #print my_list
    curr = my_list[0][index_group]
    new_list.append([curr, 0, []])
    count = 0
    for entry in my_list:
        if(entry[index_group] != curr):
            new_list.append([entry[index_group], 0, []])
            curr = entry[index_group]
            count += 1
        new_list[count][1] += entry[index_sum]
        temp_list = []
        for i in indices_list:
            temp_list.append(entry[i])
        new_list[count][2].append(temp_list)
    return new_list


# Transposes a 2d list
def transpose(my_list):
    return map(list, zip(*my_list))


# Creates a date in date() format from a natural date.
def convert_date_to_pythonic(my_date):
    if(file_struct["datetype"] == 0):
        return date(int(my_date[:4]), int(my_date[4:6]), int(my_date[6:]))
    if(file_struct["datetype"] == 1):
        return date(int(my_date[:4]), int(my_date[5:7]), int(my_date[8:]))


# Adds the missing dates to a list created by group_by. Adds the dates between
# first_date and last_date
def add_missing_dates(my_list):
    dates = list(transpose(my_list))[0]
    d = [first_date, last_date + timedelta(days=1)]
    all_dates = list(sorted(set(d[0] + timedelta(x)
                                for x in range((d[-1] - d[0]).days))))
    for x in all_dates:
        if x not in dates:
            my_list.append([x, 0, []])
    return sorted(my_list)


# Sets global variables first_date and last_date to the first and last date
# found in the bankfile
def get_first_last_date():
    global first_date, last_date
    sorted_list_expenses = sorted(list_expenses, key=lambda x: x[0])
    sorted_list_income = sorted(list_income, key=lambda x: x[0])
    first_date = sorted_list_expenses[0][0]
    if(sorted_list_income[0][0] < first_date):
        first_date = sorted_list_income[0][0]
    last_date = sorted_list_expenses[len(list_expenses)-1][0]
    if(sorted_list_income[len(list_income)-1][0] > last_date):
        last_date = sorted_list_income[len(list_income)-1][0]


# Helper functions for HTML --------------------------------------------------

# Converts a list of lists to a list of Strings in HTML format.
def list_lists_to_list_strings(my_list, sort_index, max_ret):
    new_list = []
    for x in my_list:
        temp_string = ""
        if(sort_index != -1):
            x = sorted(x, key=lambda k: k[sort_index], reverse=True)[:max_ret]
        for y in x:
            for z in y:
                if(isinstance(z, date)):
                    z = z.strftime('%d-%m-%Y')
                temp_string = temp_string + format(str(z), '<20')
            temp_string = temp_string + "<br>"
        new_list.append(temp_string)
    return new_list


# Converts a python list to a list which can be used by plotly.
def list_to_plotly(my_list):
    my_list = str(my_list)
    my_list = my_list[:0] + '[' + my_list[1:]
    my_list = my_list[:-1] + ']'
    return my_list


# Converts a list of dates in python format to a list of dates in natural format
def convert_date_list(my_date_list):
    new_date_list = []
    for my_date in my_date_list:
        new_date_list.append(my_date.strftime('%d-%m-%Y'))
    return new_date_list


# Returns a colorlist based on the elements in my_list. If the elements are
# dates, the corresponding color for each date is inserted.
def get_colorlist(my_list):
    global colors_number
    colorlist = []
    counter = 0
    for el in my_list:
        if(isinstance(el, date)):
            colorlist.append(colors_number[el.month - 1])
        else:
            colorlist.append(colors_number[counter])
            counter = counter + 1
    return colorlist


# Functions to get data for HTML ----------------------------------------------

# Returns expenses per date. All data expense grouped by date, with cash amount
# summed and description and cash amount in list.
def get_exp_per_date():
    global list_expenses
    return list(transpose(add_missing_dates(sorted(group_by(list_expenses, 0, 2, [2, 1])))))


# Returns income per date. All income data grouped by date, with cash amount
# summed and description and cash amount in list.
def get_inc_per_date():
    global list_income
    return list(transpose(add_missing_dates(sorted(group_by(list_income, 0, 2, [2, 1])))))


# Returns expenses per categorie. All data expense grouped by categorie, with
# cash amount summed and description and cash amount and date in list.
def get_exp_per_cat():
    global list_expenses
    return list(transpose(sorted(group_by(list_expenses, 4, 2, [0, 1, 2]), key=lambda x: x[1], reverse=True)))


# Calculates saldo per date from expenses per date and income per date, and
# creates list with the individual transactions.
def get_saldo_per_date(exp_per_date, inc_per_date):
    global saldo
    res_per_date = []
    desc_per_date = []
    saldo_per_date_rev = []
    curr_saldo = saldo
    for x in range(len(exp_per_date[0])):
        res_per_date.append(inc_per_date[1][x] - exp_per_date[1][x])
        desc_per_date.append([inc_per_date[2][x], exp_per_date[2][x]])
    res_per_date_rev = res_per_date[::-1]
    for x in range(len(exp_per_date[0])):
        saldo_per_date_rev.append(curr_saldo)
        curr_saldo = curr_saldo - res_per_date_rev[x]
    saldo_per_date = saldo_per_date_rev[::-1]
    return saldo_per_date, desc_per_date


# Splits a list of dates, a list of saldo per date and a list of descriptions
# per date into multiple lists for each month.
def split_data_per_month(dates, saldo_per_date, desc_per_date):
    curr_month = dates[0].month
    list_of_datelists = []
    list_of_saldolists = []
    list_of_textlists = []
    temp_datelist = []
    temp_saldolist = []
    temp_textlist = []
    for x in range(len(dates)):
        if(dates[x].month != curr_month):
            if(x < (len(dates)-1)):
                temp_datelist.append(dates[x])
                temp_saldolist.append(saldo_per_date[x])
                temp_textlist.append(desc_per_date[x])
            list_of_datelists.append(temp_datelist)
            list_of_saldolists.append(temp_saldolist)
            list_of_textlists.append(temp_textlist)
            curr_month = dates[x].month
            temp_datelist = []
            temp_saldolist = []
            temp_textlist = []
        temp_datelist.append(dates[x])
        temp_saldolist.append(saldo_per_date[x])
        temp_textlist.append("Bij <br>" + list_lists_to_list_strings([desc_per_date[x][0]], 0, 15)[
                             0] + "<br> Af <br>" + list_lists_to_list_strings([desc_per_date[x][1]], 0, 15)[0])
    list_of_datelists.append(temp_datelist)
    list_of_saldolists.append(temp_saldolist)
    list_of_textlists.append(temp_textlist)
    return list_of_datelists, list_of_saldolists, list_of_textlists


# Functions which return the HTML code for a module-------------------------------

# Returns html code with the first and last date.
def get_dates_html():
    my_string = """
    <h2>Overview transactions</h2>
    <h3>From {} to {}</h3>
    """.format(convert_date_list([first_date])[0], convert_date_list([last_date])[0])
    return my_string


# Returns html code of total income and expenses.
def get_total_amounts_html():
    my_string = """
    <p>Total income: {:0.2f}</p>
    <p>Total expenses: {:0.2f}</p>
    """.format(sum(list(transpose(list_income))[2]), sum(list(transpose(list_expenses))[2]))
    return my_string


# Returns the html code for a bar chart.
def get_bar_chart():
    global exp_per_date
    if(exp_per_date == None):
        exp_per_date = get_exp_per_date()
    bar_dates, bar_exp_per_date, bar_text_per_date = convert_date_list(
        exp_per_date[0]), exp_per_date[1], list_lists_to_list_strings(exp_per_date[2], 0, 20)
    bar_colors = get_colorlist(exp_per_date[0])
    my_string = """
    <div id="barChart"></div></br>
    <script>
        var trace1 = {{
            x: {},
            y: {},
            marker: {{
                color:{}
            }},
            type: 'bar',
            text: {}
        }}
        var data = [trace1]
        var layout = {{
            title: 'Expenses per date',
            xaxis: {{
                tickangle: -90
            }},
            font: {{
                family: 'Roboto, sans-serif'
            }},
            hoverlabel:{{
                font: {{
                    family: 'Roboto, sans-serif'
                }}
            }}
        }}
        Plotly.newPlot('barChart', data, layout)
    </script>
        """.format(list_to_plotly(bar_dates), list_to_plotly(bar_exp_per_date), list_to_plotly(bar_colors), list_to_plotly(bar_text_per_date))

    return my_string


# Returns the HTML code for a pie chart.
def get_pie_chart():
    exp_per_cat = get_exp_per_cat()
    pie_cats, pie_exp_per_cat, pie_text_per_cat = exp_per_cat[0], exp_per_cat[1], list_lists_to_list_strings(
        exp_per_cat[2], 2, 5)
    pie_colors = get_colorlist(pie_cats)
    my_string = """
    <div id="pieChart"></div></br>
    <script>
        var trace2 = {{
            values: {},
            labels: {},
            marker: {{
                colors:{}
            }},
            type: 'pie',
            text: {},
            textinfo: 'none'
        }}
        var data2 = [trace2]
        var layout2 = {{
            title: 'Expenses per category',
            autosize: true,
            font: {{
                family: 'Roboto, sans-serif'
            }},
            hoverlabel:{{
                font: {{
                    family: 'Roboto, sans-serif'
                }}
            }}
        }}
        Plotly.newPlot('pieChart', data2, layout2)
    </script>
    """.format(list_to_plotly(pie_exp_per_cat), list_to_plotly(pie_cats), list_to_plotly(pie_colors), list_to_plotly(pie_text_per_cat))

    return my_string


# Returns the HTML code for a linechart.
def get_line_chart():
    global exp_per_date
    if(exp_per_date == None):
        exp_per_date = get_exp_per_date()
    inc_per_date = get_inc_per_date()
    saldo_per_date, desc_per_date = get_saldo_per_date(
        exp_per_date, inc_per_date)
    line_dates, line_saldos, line_descs = split_data_per_month(
        exp_per_date[0], saldo_per_date, desc_per_date)

    res_string = """
    <div id="lineDiv"></div></br>
    <script>
    """
    line_list = ""
    counter = 1
    for x in range(len(line_dates)):
        res_string = res_string + """
        var {} = {{
            x: {},
            y: {},
            line: {{
                color:'{}'
            }},
            hoverinfo: 'x + y + text',
            mode: 'lines',
            text: {}
        }}


        """.format("line" + str(counter), convert_date_list(line_dates[x]), line_saldos[x], colors_number[(line_dates[x][0].month)-1], line_descs[x])
        line_list = line_list + "line" + str(counter) + ","
        counter = counter + 1
    line_list = line_list[:-1]
    res_string = res_string + """
    var line_data = [{}]
    var line_layout = {{
        hovermode: 'closest',
        showlegend: false,
        title: 'Saldo per date',
        xaxis: {{
            tickangle: -90
        }},
        font: {{
            family: 'Roboto, sans-serif'
        }},
        hoverlabel:{{
            font: {{
                family: 'Roboto, sans-serif'
            }}
        }}
    }}
    Plotly.newPlot('lineDiv', line_data, line_layout)
    </script>
    """.format(line_list)
    return res_string


# Prototype function for adding new graph.
'''
def get_new_chart():
    data = get_data()
    html_code = """
    """.format(data)
    return html_code
'''


# HTML Functions ---------------------------------------------------------------------------------------

# Creates the output HTML.
def create_output():
    add_to_html(plotly_code)
    add_to_html(get_dates_html())
    add_to_html(get_total_amounts_html())
    add_to_html(get_bar_chart())
    if(categories_dict_keywords):
        add_to_html(get_pie_chart())
    add_to_html(get_line_chart())
    # add_to_html(get_new_chart())
    write_html()


# Adds HTML code to html_content
def add_to_html(element):
    global html_content
    html_content = html_content + element


# Writes the HTML file.
def write_html():
    global html_content
    html_name = os.path.join(curr_dir, bankfile_name + ".html")
    f = open(html_name, 'w')
    html_content = html_content + """
    </br></br>
    <footer>
    <p>BankTeller v0.2</p>
    <p>Matthijs Kaandorp, 2018</p>
    </footer>
    </body>
    </html>
    """
    f.write(html_content)
    f.close()
    string_saved = "Results saved in {}".format(
        os.path.join(curr_dir, bankfile_name+".html"))
    messagebox.showinfo("Succes", string_saved)



# Main
if __name__ == "__main__":
    global bankfile_name, plotly_code, saldo

    Tk().withdraw()
    # Read bankfile csv.
    try:
        bankfile_name = askopenfilename(filetypes=[("CSV File", "*.csv")])
        bankfile_name = bankfile_name[:-4]
        read_bank_file(bankfile_name)
    except:
        messagebox.showinfo("Error", "Invalid csv file")
        sys.exit(1)
    # Read plotly file.
    try:
        plotlyfile_name = open(os.path.join(curr_dir, 'plotly-basic.min.js'))
        plotly_code = "<script> " + plotlyfile_name.read() + " </script>"
    except:
        messagebox.showinfo("Error", "Invalid Plotly file")
        sys.exit(1)
    # Ask user for current saldo.
    try:
        u_saldo = askstring(
            "Saldo", "Huidig saldo (of op laatst beschikbare datum)")
        saldo = float(u_saldo.replace(",", "."))
    except:
        saldo = 0.0

    read_categories()
    check_bankfile()
    get_first_last_date()
    create_output()
