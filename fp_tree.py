from itertools import combinations

# input
groceries = open('./groceries.csv')

# set minimum support and minimum confidence values
min_support = 220  # Min frequency of itemsets to be generated.
min_confidence = 0.35  # Min confidence of rules to be generated.

print(f'Minimum Support: {min_support}\nMinimum Confidence: {min_confidence}\n')

# taking data from file
data = []
for line in groceries:
    data.append(line.split(','))

# Data Preprocessing
#   Every last item in each transaction has a new line character at it's end.
#   The new line characters are removed.
for i in range(len(data)):
    data[i][len(data[i])-1] = data[i][len(data[i])-1][:-1]

# Each transaction is converted into a frozenset so that transactions are hashable.
for i in range(len(data)):
    data[i] = frozenset(sorted(data[i]))

# Dictionary having each transaction as key
transactions_dict = {}
for transaction in data:
    transactions_dict[transaction] = 1


# Class for a Node in FP Tree
class TreeNode:
    def __init__(self, Node_name,counter,parentNode):
        self.name = Node_name
        self.count = counter
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}
        
    def increment_counter(self, counter):
        self.count += counter


"""
    FP Tree construction
"""
def construct_FPtree(dataset, minSupport):
    header_table = {}  # A dictionary that stores all unique items as keys and their supports as values.
    for transaction in dataset:
        for item in transaction:
            # accumulating the support of each item in the dataset
            header_table[item] = header_table.get(item,0) + dataset[transaction]
    # Pruning the items which have support less than the minimum support.
    for k in list(header_table):
        if header_table[k] < minSupport:
            del(header_table[k])

    freq_items = set(header_table.keys())   #  A set that contains all unique items.

    if len(freq_items) == 0:
        return None, None

    for k in header_table:
        header_table[k] = [header_table[k], None]

    # create the root node of FP tree
    root = TreeNode('Null Set',1,None)

    # traversing each item in each transaction
    for transaction,count in dataset.items():
        freq_transaction = {}
        for item in transaction:
            if item in freq_items:
                freq_transaction[item] = header_table[item][0]  # adding frequent items of a transaction to freq_transaction dictionary
        if freq_transaction:
            # to get ordered itemset from each transaction
            sorted_transaction = [v[0] for v in sorted(freq_transaction.items(), key=lambda p: p[1], reverse=True)]
            # adding ordered itemset from each transaction to FP tree
            add_transaction(sorted_transaction, root, header_table, count)
    return root, header_table



def add_transaction(itemset, root, header_table, count):
    if itemset[0] in root.children:
        # incrementing count of node if it already exists in the tree.
        root.children[itemset[0]].increment_counter(count)
    else:
        # else a new Node is created
        root.children[itemset[0]] = TreeNode(itemset[0], count, root)

        if header_table[itemset[0]][1] == None:
            # if there is no Node link for first item its children dict is assigned as Node_link
            header_table[itemset[0]][1] = root.children[itemset[0]]
        else:
            # else if there is a Node Link update it.
            update_NodeLink(header_table[itemset[0]][1], root.children[itemset[0]])


    if len(itemset) > 1:
        # recurse for remaining items in the transaction.
        add_transaction(itemset[1::], root.children[itemset[0]], header_table, count)



def update_NodeLink(Test_Node, Target_Node):
    while (Test_Node.nodeLink != None):
        Test_Node = Test_Node.nodeLink

    Test_Node.nodeLink = Target_Node


"""
    FP Tree Traversal (Mining frequent itemsets)
"""

# Traverse the tree upwards from a leaf node. The path is appended to prefix path
def FPTree_uptraversal(leaf_Node, prefixPath):
    if leaf_Node.parent != None:
        prefixPath.append(leaf_Node.name)
        FPTree_uptraversal(leaf_Node.parent, prefixPath)

# Finds the conditinal pattern bases for an itemset
def find_prefix_path(TreeNode):
    Conditional_patterns_base = {}

    while TreeNode != None:
        prefixPath = []
        FPTree_uptraversal(TreeNode, prefixPath)
        if len(prefixPath) > 1:
            Conditional_patterns_base[frozenset(prefixPath[1:])] = TreeNode.count
        TreeNode = TreeNode.nodeLink

    return Conditional_patterns_base


# function to get the frequent itemsets from the FP tree
def Mine_Tree(root, header_table, minSupport, prefix, freq_items):
    # get all items in the header_table into a list
    LIST = [v[0] for v in sorted(header_table.items(),key=lambda p: p[1][0])]
    for base_pattern in LIST:
        new_frequentset = prefix.copy()
        new_frequentset.add(base_pattern)
        # add frequent itemset to final list of frequent itemsets
        freq_items.append(new_frequentset)
        # get all conditional pattern bases for item or itemsets
        Conditional_pattern_bases = find_prefix_path(header_table[base_pattern][1])
        # call FP Tree construction to make conditional FP Tree
        Conditional_FPTree, Conditional_header = construct_FPtree(Conditional_pattern_bases,minSupport)

        if Conditional_header != None:
            Mine_Tree(Conditional_FPTree, Conditional_header, minSupport, new_frequentset, freq_items)



root, header_table = construct_FPtree(transactions_dict, min_support)
freq_items = []
Mine_Tree(root, header_table, min_support, set([]), freq_items)
freq_items = sorted(freq_items, key = lambda x:len(x))


final_itemsets = []  # Stores all the frequent itemsets that are generated

# store itemsets of lengths 1,2,3... in final_itemsets list
for i in range(1,10):
    kitemsets = []
    for itemset in freq_items:
        if(len(itemset)==i):
            kitemsets.append(itemset)
    if kitemsets:
        final_itemsets.append(kitemsets)

# finds the support of an itemset
def support(itemset):
    count = 0
    for i in data:
        if itemset.issubset(i):
            count+=1
    return count

# Printing all the frequent itemsets
def print_freq_itemsets(freq_itemsets):
    print("*****FREQUENT ITEMSETS*****\n")
    for itemset in freq_itemsets:
        for x in itemset:
            for y in x:
                print(y,end=', ')
            print(f'({support(x)})')
    print()
print_freq_itemsets(final_itemsets)


'''
    *****   Rule Generation   *****
'''


def confidence(a,b):
    return (support(a.union(b)))/support(a)


one_item_rules = []
"""
Generates the one itemset rules and stores them in rules(a list)
"""
def get_one_item_rules(itemset):
    rules = []
    for item in combinations(itemset,1):
        rule = []
        rule.append(set(itemset)-set([item[0]]))
        rule.append(set([item[0]]))
        conf = confidence(rule[0],rule[1])
        if conf>=min_confidence and (rule not in rules):
            rules.append(rule)
    if rules and rules not in one_item_rules:
        one_item_rules.append(rules)



for kitemset in final_itemsets[1:5]:
    for itemset in kitemset:
        get_one_item_rules(itemset)

"""
Function to merge two (k-1)-length rules and make a (k)-length rule
in the form of a list called new_rule
ant->antecedent, cons->consequent
"""
def merge_rules(rule1, rule2):
    new_rule = []
    cons = rule1[1].union(rule2[1])
    ant = rule1[0].union(rule2[0])
    ant = ant - cons
    if ant and cons:
        new_rule.append(ant)
        new_rule.append(cons)
    return new_rule
        

final_rules = []
final_rules.append(one_item_rules)


#Stores the final rules of the dataset
for m in range(0,5):
    n_itemset_rules = []
    for rules in final_rules[m]: #one_item_rules:
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
    print("*****GENERATED ASSOCIATION RULES*****\n")
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