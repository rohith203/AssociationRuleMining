#Importing essential libraries
from itertools import combinations

#Reading the dataset(groceries.csv) into groceries
groceries = open('./groceries.csv')

#Minimum support 
min_support = 250

#Minimum confidence
min_confidence = 1.0

#Preprocessing of the data
data = []
for line in groceries:
    data.append(line.split(','))

for i in range(len(data)):
    data[i][len(data[i])-1] = data[i][len(data[i])-1][:-1]

#maximum number of transactions in a row which is 32
max_trans = 0
for i in data:
    if len(i) > max_trans: max_trans = len(i)


# Function to calculate the support of an item in an itemset, and returns the count
def support(item):
    c = 0
    for i in data:
        if set(item).issubset(set(i)):
            c+=1
    return c

items = []
for i in data:
    for j in i:
        items.append(j)
one_itemset = list(set(items))
for i in range(len(one_itemset)):
    one_itemset[i] = [one_itemset[i]]

final_itemset = []
one_itemset = [x for x in one_itemset if support(x)>=min_support ]

final_itemset.append(one_itemset)


"""
Function to merge two (k)-itemsets and generate a (k+1)-dataset 
"""
def merge(a,b):
    a = set(a)
    b = set(b)
    uni = a.union(b)
    if(len(uni)==len(a)+1):
        return list(uni)
    else:
        return []


maximal_itemsets = [] # The maximal frequent itemsets are stored in this list
closed_itemsets = [] # The closed frequent itemsets are stored in this list

# passing n-1 itemset
'''
creates all possible (k)-itemsets and stores them in the
n_itemset as list separated by ,
'''
def create_itemset(itemset):
    n_itemset = []
    size = len(itemset)-1
    for i in range(size):
        item_supp = support(itemset[i])
        isfreq = item_supp>=min_support
        f1 = 1
        f2 = 1
        for j in range(i+1,size+1):
            temp = merge(itemset[i],itemset[j])
            if len(temp)>0 and support(temp)>=min_support and (temp not in n_itemset):
                n_itemset.append(temp)
                supp = support(temp)
                if supp >= min_support: f1 = 0
                if supp == item_supp: f2 = 0

        if f1==1 and isfreq:
            maximal_itemsets.append(itemset[i])
        if f2==1 and isfreq:
            closed_itemsets.append(itemset[i])

    final_itemset.append(n_itemset)

for i in range(2,5):
    create_itemset(final_itemset[i-2])


def print_freq_itemsets(freq_itemsets):
    for itemset in freq_itemsets[1:]:
        for x in itemset:
            for y in x:
                print(y,end=', ')
            print(f'({support(x)})')
    print()
print_freq_itemsets(final_itemset)

print("\nMAXIMAL itemsets\n\n")

print(maximal_itemsets)
print("\nCLOSED itemsets\n")

print(closed_itemsets)


"""
Calculates and returns the confidence of two rules
"""
def confidence(a,b):
    return (support(list(set(a).union(set(b)))))/support(a)

one_item_rules = []
"""
Generates the one itemset (one consequent) rules and stores them in rules(a list)
"""
def get_one_item_rules(itemset):
    rules = []
    for item in combinations(itemset,1):
        rule = []
        rule.append(list(set(itemset)-set([item[0]])))
        rule.append([item[0]])
        conf = confidence(rule[0],rule[1])
        if conf>=min_confidence and (rule not in rules):
            rules.append(rule)
    if rules and rules not in one_item_rules:
        one_item_rules.append(rules)

for kitemset in final_itemset[1:5]:
    for itemset in kitemset:
        get_one_item_rules(itemset)

"""
Function to merge two (k-1)-length rules and make a (k)-length rule
in the form of a list called new_rule
ant->antecedent, cons->consequent
"""
def merge_rules(rule1, rule2):
    new_rule = []
    cons = set(rule1[1]).union(set(rule2[1]))
    ant = set(rule1[0]).union(set(rule2[0]))
    ant = ant - cons
    if ant and cons:
        new_rule.append(list(ant))
        new_rule.append(list(cons))
    return new_rule

#Stores the final rules of the dataset
final_rules = []
final_rules.append(one_item_rules)

for m in range(0,5):
    n_itemset_rules = []
    for rules in final_rules[m]:
        an_itemset_rules = []
        n = len(rules)
        for i in range(n-1):
            for j in range(i+1, n):
                temp = merge_rules(rules[i],rules[j])
                if len(temp)>0 and confidence(temp[0],temp[1])>=min_confidence and (temp not in an_itemset_rules):
                    an_itemset_rules.append(temp)
        if an_itemset_rules: n_itemset_rules.append(an_itemset_rules)
    final_rules.append(n_itemset_rules)

"""
Prints all the high confidence rules
"""
def print_rules():
    for k_cons_rules in final_rules:
        for itemset_rules in k_cons_rules:
            for rule in itemset_rules:
                for x in rule[0]:
                    print(x,end=', ')
                print(f'({support(rule[0])})',end='')
                print(' --->',end=' ')
                for y in rule[1]:
                    print(y,end=', ')
                print(f'({support(rule[1])})',end='')
                print(' -conf({0:0.2f})'.format(confidence(rule[0],rule[1])))

print_rules()