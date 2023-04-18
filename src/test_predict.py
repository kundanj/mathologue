from ml.predict import predict_response
import pandas as pd

test_bed = [
('from 3000 I need 3%','percentages',''),
('what % is 30 from 400','percentages',''),
('how many different ways can I arrange letters of the word ROCK','permutation',''),
('how many permutations can be formed from the numbers 1,2,3,4','permutation',''),
('price of a pair of trousers was decreased by 22% to 30. What was the original price of the trousers?','percentages',''),
('-x+2y-3 =0 , 3x+4y-11=0','linearequations',''),
('3 + 1/4','arithmetic',''),
('4.5 + 3 - 10.56','arithmetic',''),
('cost of pant was increased from 35 to 50 what is % change','percentages',''),
('pricE was up from 35 to 50 what is % change','percentages',''),
('from among the 36 students in a class, 1 leader and 1 representative are to be appointed. In how many ways can this be done?','permutation',''),
('10 participants are participating in a competition. In how many ways can the first 3 prizes be won?','permutation',''),
('In how many ways can I arrange 10 people in a line','permutation',''),
('how many choices of 3 guys can I select from 10 guys','combination',''),
('from a group of 6 men and 4 women how can you form a committee of 3 men and 2 women','combination',''),
('from group of 7 men  4 women how many groups of 5 guys','combination',''),
('if we have a group of 6 men  and 4 women how many ways can you form a committee of 5 people','combination',''),
('A certain sum amounts to $ 7200 in 2 years at 6% per annum compound interest, compounded annually. Find the sum?','interest',''),
('how many ways can 5 players be chosen from 8 players','combination',''),
('find the sum that amounts to $ 7200 in 2 years at 6% per annum compound interest compounded annually','interest',6408),
('what is the principal that amounts to Rs  4913 in 3 years at 6.25%','interest','4096'),
('what sum will amount to rs 8788 in 3 years at rate of 4% p.a. compounded annually','interest',''),
('whats the sum that amounts to $ 72900 in 2 years at 8% per annum compound interest, compounded annually','interest',62500),
('find the simple interest on Rs. 68,000 at 16.66% per annum for a period of 9 months?','interest',8500),
('if you deposit an  4000 into an for 5 years at 6% compounded quarterly how much final amount will I get','interest',''),
('certain sum amounts to $ 7200 in 2 years at 20% per annum compound interest compounded annually. find the sum','interest',''),
('construct the group frequency distribution for 20, 6, 23, 19, 9, 14, 15, 3, 1, 12, 10, 20, 13, 3, 17, 10, 11, 6, 21, 9, 6, 10, 9, 4, 5, 1, 5, 11, 7, 24 with group of 5','statistics',''),
('what percentile is 102 from 98, 99, 99, 100, 101, 102, 104, 104, 105, 105, 107, 110, 112, 112','statistics',''),
('find the frequency table of 4, 3, 6, 5, 2, 4, 3, 3, 6, 4, 2, 3, 2, 2, 3, 3, 4, 5, 6, 4, 2, 3, 4','statistics',''),
('calculate  standard deviation of the sequence 100, 121, 123, 145, 151.','statistics',''),
('whats the median  of the numbers 42, 51, 62, 47, 38, 50, 54, 44','statistics',''),
('log log 6','arithmetic','-0.1089'),
('sin of sin 30','arithmetic','-0.8349'),
('3x2 – 6x +x3 – 18','polynomial','2.449'),
('whats the side of a right triangle when other side is 300 and the opposite angle is 30','trigonometry','519.61'),
('find the hypotenuse of a right triangle if the length of one side is 3 and measure of the angle adjacent to that side is 60','trigonometry','2.449'),
('if area of an isosceles triangle is 300 what is length of its side if the base is 20','trigonometry','519.61')
]

'''
{
    "Question" : [],
    "Act Cat": [],
    "Sol": [],
    "Response": [],
    "Pred Cat": [],
})
'''
list = []
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

i = 1
for (ques, cat, sol) in test_bed:
    (response, tag) = predict_response('AAA2001' + str(i), ques, True)
    i = i + 1
    #df.append({"Question" : ques, "Act Cat": cat, "Sol": sol, "Response": response, "Pred Cat": ""}, ignore_index=True) this shit does not wrk in pandas!!!
    list.append({"Question" : ques, "Act Cat": cat, "Sol": sol, "Response": response, "Pred Cat": tag})

print('-------------------------------------------------------')
print('-------------------------------------------------------')
df = pd.DataFrame(list)
print(df['Act Cat'] == df['Pred Cat'])
print(df)
