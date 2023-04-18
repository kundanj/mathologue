import re
import statistics
import pandas as pd

regexes = [ re.compile(p) for p in [ r"(find|what.i?s)\s*(the)*\s*(?P<var_p>[0-9]{1,3})th\spe?rce?ntile\D{0,12}(?P<var_series>((\d{1,}\s?,\s?)+\s?\d+))",
                                     r"what\s*\D*percentile\s*(is|of)\s* (?P<var_p>[0-9]{1,3})\D{0,12}(?P<var_series>((\d{1,}\s?,\s?)+\s?\d+))",
                                     r"(what\s*)?(mean|median|average|standard\s*deviation|variance)\s*(of|for)\s*\D{0,12}\s*(?P<var_series>((\d{1,}\s?,\s?)+\s?\d+))",
                                     r"(construct|draw|find|what.i?s)?\s*(the)*\s*(groupe?d?\s*frequency\s*(distribution)?\s*(distribution|table))\s*(of|for)\s*\D{0,15}\s*(?P<var_series>((\d{1,}\s?,\s?)+\s?\d+))\D{0,12}((class)?\s*intervals?|groupe?d?|batche?d?)\D{0,6}(?P<var_group_fact>[0-9]+)",
                                     r"(construct|draw|find|what.i?s)?\s*(the)*\s*(frequency\s*(distribution)?\s*(distribution|table))\s*(of|for)\s*\D{0,15}\s*(?P<var_series>((\d{1,}\s?,\s?)+\s?\d+))"
                                     ] ]


def parse_numseries(series_str):
    return [float(i) for i in re.split(r'\s*[,\s]\s*', series_str.strip()) ]


def process_statistics(question, nlp):
    stmt = None
    result = 0
    for i, regex in enumerate(regexes):
        match = regex.search(question)
        if (match and i in (0,1)):
            # find the 85th percentile of {95, 88, 70, 75, 83, 70, 66, 91, 68, 76, 82}
            # what percentile is 102 from 98, 99, 99, 100, 101, 102, 104, 104, 105, 105, 107, 110, 112, 112
            vars = match.groupdict()
            var_p = int(vars.get('var_p'))
            var_series = parse_numseries(vars.get('var_series'))
            var_series.sort()
            if (i == 0):
                index = (var_p / 100) * len(var_series)
                result = var_series[round(index)]
                stmt = "{0} percentile of {1} is {2}".format(var_p, var_series, result)
            elif (i == 1):
                index = var_series.index(var_p)
                result = int((index/len(var_series)) * 100)
                stmt = "{0} is {1} percentile of {2}".format(var_p, result, var_series)
            break
        elif (match and i == 2):
            # whats mean/median  of the numbers 1,2,3,4 567
            vars = match.groupdict()
            var_series = parse_numseries(vars.get('var_series'))
            var_series.sort()
            if (question.find('mean') > -1) or (question.find('average') > -1):
                result = statistics.mean(var_series)
                stmt = "Mean is {:.2f}".format(result)
            elif (question.find('median') > -1):
                result = statistics.median(var_series)
                stmt = "Median is {:.2f}".format(result)
            elif (question.find('deviation') > -1):
                result = statistics.stdev(var_series)
                stmt = "Standard Deviation is {:.2f}".format(result)
            elif (question.find('variance') > -1):
                result = statistics.variance(var_series)
                stmt = "Variance is {:.2f}".format(result)
            break
        elif (match and i == 3):
            # whats the group frequency distribution of 1,2,3,4 567 group by 5
            vars = match.groupdict()
            var_series = parse_numseries(vars.get('var_series'))
            group_factor = int(vars.get('var_group_fact'))
            var_series.sort()
            data = pd.Series(var_series)
            if (group_factor is not None):
                df_result = pd.DataFrame({ "Range" : data.transform(lambda x: str(int(x - (x % group_factor))) + '-' + str(int(x - (x % group_factor) + group_factor))) ,
                    "Freq" : data.transform(lambda x: 1) })
                result = df_result.groupby(by='Range', sort=False)['Freq'].sum().to_dict()
                stmt = "Frequency distribution is $TABLE2COL$ ['C.I.','Freq'] {}".format(result)
            break
        elif (match and i == 4):
            # whats frequency distribution of 1,2,3,4 567
            vars = match.groupdict()
            var_series = parse_numseries(vars.get('var_series'))
            var_series.sort()
            data = pd.Series(var_series)
            result = data.value_counts(sort=False)
            stmt = "Frequency distribution is $TABLE2COL$ ['Data point','Freq'] {}".format(result.to_dict())
            break
    return "$PROBANS$ "  + stmt
