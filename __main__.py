import csv
import collections
import numpy
import re
from datetime import datetime
from matplotlib import pyplot as plt
import mpld3
import urllib
from string import Template

csv_source = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv"
treshold = 100

table_row_template = """\
<tr>
<td>
$plot_left
</td>
<td>
$plot_right
</td>
</tr>\
"""

table_row_single_template = """\
<tr>
<td>
$plot_left
</td>
<td></td>
</tr>\
"""

html_template = """
<!DOCTYPE html>
<html>
<head>
<title>Corona Statistics</title>
</head>
<body>
<table style="width:100%">
$table_rows
</table>
</br>
<a href="$csv_source">Source - Johns Hopkins</a>
</body>
</html>
"""


def process_country(country, data_dict):
    print "process country {}".format(country)
    dates_dict = {}

    # filter data
    for k, v in data_dict.iteritems():
        if (re.match('\d+/\d+/\d+', k) and float(v) > treshold):
            date_time = datetime.strptime(k, '%m/%d/%y')
            dates_dict[date_time] = float(v)

    # sort data
    dates_dict = collections.OrderedDict(sorted(dates_dict.items()))

    lists = sorted(dates_dict.items())
    d, number_of_deseases = zip(*lists)
    number_of_new_deseases = [0] + list(numpy.diff(number_of_deseases))

    # calculate doubling rate
    rate = numpy.divide(number_of_deseases[1:], number_of_deseases[:-1])
    log2_vector = numpy.full((len(rate)), numpy.log(2))
    doubling_rate = [0.0] + list(numpy.divide(log2_vector, numpy.log(rate)))

    labelx = -0.12

    # total number of deseases
    ax1 = plt.subplot(411)
    plt.title(country)
    plt.ylabel("Number of corona")
    plt.grid(True)
    plt.plot(d, number_of_deseases)
    plt.gcf().autofmt_xdate()
    ax1.yaxis.set_label_coords(labelx, 0.5)

    # total number of deseases
    ax2 = plt.subplot(412, sharex=ax1)
    plt.grid(True)
    plt.yscale("log")
    plt.plot(d, number_of_deseases)
    plt.gcf().autofmt_xdate()
    ax2.yaxis.set_label_coords(labelx, 0.5)

    # new deseases
    ax3 = plt.subplot(413, sharex=ax1)
    plt.ylabel("Delta")
    plt.grid(True)
    plt.bar(d, number_of_new_deseases, width=0.4)
    plt.gcf().autofmt_xdate()
    ax3.yaxis.set_label_coords(labelx, 0.5)

    # doubling rate
    ax4 = plt.subplot(414, sharex=ax1)
    plt.ylabel("Doubl.-Rate")
    plt.grid(True)
    plt.bar(d, doubling_rate, width=0.4)
    plt.gcf().autofmt_xdate()
    ax4.yaxis.set_label_coords(labelx, 0.5)

    result = mpld3.fig_to_html(plt.gcf())
    plt.clf()
    return result


if __name__ == "__main__":
    file_name = "data.csv"
    print "get {}".format(file_name)
    urllib.urlretrieve(csv_source, filename=file_name)
    with open(file_name) as csvfile:
        dict_reader = csv.DictReader(csvfile, delimiter=',')
        countries = ['Austria', 'Italy', 'Germany', 'Spain', 'Turkey']
        html_graphs = []
        processed_countries = []
        for data_dict in dict_reader:
            current_country = data_dict['Country/Region']
            if current_country in countries:
                current_country_html = process_country(current_country, data_dict)
                processed_countries.append(current_country)
                html_graphs.append(current_country_html)
        if sorted(countries) != sorted(processed_countries):
            print "Error: could not process all countries. Not found: {}".format(list(set(countries) - set(processed_countries)))

        table_rows = ""

        def chunks(l, n):
            n = max(1, n)
            return (l[i:i + n] for i in range(0, len(l), n))

        for chunk in chunks(html_graphs, 2):
            plot_left = chunk[0]
            plot_right = chunk[1] if len(chunk) > 1 else ""
            if len(chunk) > 1:
                used_template = table_row_template
            else:
                used_template = table_row_single_template
            table_rows = table_rows + Template(used_template).substitute(**locals()) + "\n"

        html_content = Template(html_template).substitute(**locals())
        open("index.html", "w").write(html_content)

    print "done"
