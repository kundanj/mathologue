import re
import sys
import os
from tools import larkadapter
from py_expression_eval import Parser
from fractions import Fraction as frac
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = Parser()

def process_arith(input_question, nlp):
    # replace common symbols for arithmetic e.g. X by *
    stmt = None
    try:
        # am removing words > 5 chars but this could be a bug as it only prpesses log/sin etc now 3 letter ops
        question = re.sub('(what\s*i?s?|(^[A-Za-z]{5,}))','',input_question)
        mid_result = larkadapter.parse_expression(question)
        if re.search("(\d+\s*/\s*\d+)", question):
            mid_result = frac(mid_result).limit_denominator()
            stmt = '$PROBANS$ ' + str(mid_result)
        else: # other post processing here
            stmt = '$PROBANS$ ' + str(mid_result)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        return stmt
