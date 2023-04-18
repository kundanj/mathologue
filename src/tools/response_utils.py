import json

def process_explain(subcont):
    response = None
    if subcont['ques_code'] in ['int-ci','int-prin','int-amt','trig-side1','trig-hyp1','trig-ang1']:
        response = '$EXPLAIN$ ' + json.dumps(subcont)
    return response
