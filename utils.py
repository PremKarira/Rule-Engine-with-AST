import re
import json
from datetime import datetime, timezone
from bson.objectid import ObjectId
from models import Node

def wrap_with_parentheses_if_needed(rule_string):
    # Split the rule by AND and OR to find where parentheses might be missing
    tokens = tokenize(rule_string)
    
    # Automatically wrap conditions around AND/OR
    final_rule_string = ""
    open_paren = False
    
    for i, token in enumerate(tokens):
        if token in ("AND", "OR"):
            if not open_paren:
                final_rule_string = f"({final_rule_string}"
                open_paren = True
            final_rule_string += f" {token} "
        else:
            final_rule_string += token
        
        # Close the parentheses after each group
        if i + 1 < len(tokens) and tokens[i + 1] in ("AND", "OR"):
            continue
        elif open_paren:
            final_rule_string += ")"
            open_paren = False

    return final_rule_string

def tokenize(rule_string):
    tokens = re.findall(r'\(|\)|AND|OR|>|<|=|\'[^\']*\'|\w+', rule_string)
    return tokens

def parse_condition(attribute, operator, value):
    attribute_node = Node("attribute", value=attribute)
    operator_node = Node("operator", value=operator)
    value_node = Node("value", value=value)
    return Node("comparison", left=attribute_node, right=value_node, value=operator_node)

def validate_brackets(rule_string):
    stack = []
    for char in rule_string:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack.pop() != '(':
                return False
    return not stack 

def parse_tokens(tokens):
    print("Tokens:", tokens)

    def parse_expression(index):
        token = tokens[index]
        if token == '(':
            expr, index = parse_expression(index + 1)
            if tokens[index] == ')':
                index += 1  # Skip closing parenthesis
                return expr, index
            operator = tokens[index]
            right_expr, index = parse_expression(index + 1)
            index += 1  
            return Node("operator", left=expr, right=right_expr, value=operator), index

        if re.match(r'[a-zA-Z_]+', token):  
            attribute = token
            operator = tokens[index + 1]
            value = tokens[index + 2].strip("'")
            return parse_condition(attribute, operator, value), index + 3

        return None, index

    def parse_expression_stack(tokens):
        stack = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == '(':
                expr, index = parse_expression(index)
                stack.append(expr)
            elif token == ')':
                index += 1 
                break
            elif token in ("AND", "OR"):
                stack.append(token)
                index += 1
            else:  # Attribute condition
                cond, index = parse_expression(index)
                stack.append(cond)

        while "AND" in stack:
            i = stack.index("AND")
            left = stack[i - 1]
            right = stack[i + 1]
            stack = stack[:i - 1] + [Node("operator", left=left, right=right, value="AND")] + stack[i + 2:]

        while "OR" in stack:
            i = stack.index("OR")
            left = stack[i - 1]
            right = stack[i + 1]
            stack = stack[:i - 1] + [Node("operator", left=left, right=right, value="OR")] + stack[i + 2:]

        return stack[0] 
    
    rule_string = " ".join(tokens)
    if not validate_brackets(rule_string):
        raise ValueError("Mismatched parentheses in rule string.")
    ast = parse_expression_stack(tokens)
    return ast

def create_rule(rule_string):
    tokens = tokenize(rule_string)
    ast = parse_tokens(tokens)
    return ast

def evaluate_rule(ast, data):
    if ast.type == "operator":
        left_val, left_reasons = evaluate_rule(ast.left, data)
        right_val, right_reasons = evaluate_rule(ast.right, data)

        if ast.value == "AND":
            combined_reasons = left_reasons + right_reasons
            if not left_val:
                return False, combined_reasons
            if not right_val:
                return False, combined_reasons
            return True, combined_reasons + ["Both conditions met."]

        elif ast.value == "OR":
            if left_val:
                return True, ["1st condition met:"] + left_reasons + right_reasons
            if right_val:
                return True, ["2nd condition met:"] + left_reasons + right_reasons
            return False, left_reasons + right_reasons

    elif ast.type == "comparison":
        attribute = ast.left.value
        operator = ast.value.value
        value = ast.right.value

        if isinstance(value, str) and value.isdigit():
            value = int(value)

        if attribute in data:
            data_value = data[attribute]

            if isinstance(data_value, str) and data_value.isdigit():
                data_value = int(data_value)
            
            if operator == ">":
                if data_value > value:
                    return True, [f"{attribute} ({data_value}) > {value}"]
                else:
                    return False, [f"{attribute} ({data_value}) is not greater than {value}"]
            elif operator == "<":
                if data_value < value:
                    return True, [f"{attribute} ({data_value}) < {value}"]
                else:
                    return False, [f"{attribute} ({data_value}) is not less than {value}"]
            elif operator == "=":
                if data_value == value:
                    return True, [f"{attribute} ({data_value}) = {value}"]
                else:
                    return False, [f"{attribute} ({data_value}) is not equal to {value}"]

    return False, ["Condition not evaluated properly."]

def combine_rules(rules):
    asts = [create_rule(rule) for rule in rules]
    combined_ast = None
    for ast in asts:
        if combined_ast is None:
            combined_ast = ast
        else:
            combined_ast = Node("operator", left=combined_ast, right=ast, value="AND")
    return combined_ast

def node_decoder(d):
    if 'type' in d:
        return Node(d['type'], d.get('left'), d.get('right'), d.get('value'))
    return d
