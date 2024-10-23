from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from bson.objectid import ObjectId
import json
from utils import create_rule, evaluate_rule, combine_rules, node_decoder
from datetime import datetime, timezone
from database import mongo

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/create_rule', methods=['POST'])
def api_create_rule():
    rule_string = request.form['rule']
    ast = create_rule(rule_string)
    serialized_ast = json.dumps(ast.to_dict())
    rule_data = {
        "rule_string": rule_string,
        "ast": serialized_ast,
        "created_at": datetime.now(timezone.utc)
    }
    mongo.db.rules.insert_one(rule_data)
    return redirect(url_for('main.index'))  # Ensure this is 'main.index'

@main.route('/evaluate')
def evaluate():
    rules = list(mongo.db.rules.find())
    return render_template('evaluate.html', rules=rules)

@main.route('/show_rules', methods=['GET', 'POST'])
def show_rules():
    rules = list(mongo.db.rules.find())
    for rule in rules:
        rule['ast'] = json.loads(rule['ast'])

    if request.method == 'POST':
        selected_rules = request.form.getlist('selected_rules')
        if not selected_rules:
            return "No valid rules selected", 400
        selected_rule_data = mongo.db.rules.find({"_id": {"$in": [ObjectId(rule_id) for rule_id in selected_rules]}})
        rule_strings = [rule['rule_string'] for rule in selected_rule_data]
        combined_ast = combine_rules(rule_strings)
        serialized_combined_ast = json.dumps(combined_ast.to_dict())
        combined_rule_data = {
            "rule_string": "Combined Rule",
            "ast": serialized_combined_ast,
            "created_at": datetime.utcnow()
        }
        mongo.db.rules.insert_one(combined_rule_data)
        return redirect(url_for('main.evaluate'))  # Ensure this is 'main.evaluate'

    return render_template('show_rules.html', rules=rules)

@main.route('/api/evaluate', methods=['POST'])
def api_evaluate_rules():
    age = int(request.form['age'])
    department = request.form['department']
    salary = int(request.form['salary'])
    experience = int(request.form['experience'])

    data = {
        "age": age,
        "department": department,
        "salary": salary,
        "experience": experience
    }

    results = []
    for rule in mongo.db.rules.find({}):
        ast = json.loads(rule['ast'], object_hook=node_decoder)
        result, reasons = evaluate_rule(ast, data)
        results.append({
            'rule_id': str(rule['_id']),
            'rule_string': rule['rule_string'],
            'result': result,
            'reasons': reasons
        })

    return jsonify(results)

@main.route('/rules', methods=['GET'])
def display_rules():
    rules = list(mongo.db.rules.find())
    ast_list = [json.loads(rule['ast']) for rule in rules]
    return render_template('rules.html', asts=ast_list)

@main.route('/delete_selected_rules', methods=['POST'])
def delete_selected_rules():
    selected_rule_ids = request.form.getlist('selected_rules')
    
    if selected_rule_ids:
        object_ids = [ObjectId(rule_id) for rule_id in selected_rule_ids]
        mongo.db.rules.delete_many({"_id": {"$in": object_ids}})

    return redirect(url_for('main.show_rules')) 

@main.route('/delete_rule/<rule_id>', methods=['POST'])
def delete_rule(rule_id):
    mongo.db.rules.delete_one({"_id": ObjectId(rule_id)})
    return redirect(url_for('main.show_rules'))  

@main.route('/delete_all_rules', methods=['POST'])
def delete_all_rules():
    mongo.db.rules.delete_many({})
    return redirect(url_for('main.show_rules'))  

@main.route('/combine_selected_rules', methods=['POST'])
def combine_selected_rules():
    selected_rule_ids = request.form.getlist('selected_rules')
    
    if not selected_rule_ids:
        return "No valid rules selected", 400

    rule_strings = []
    for rule_id in selected_rule_ids:
        rule_data = mongo.db.rules.find_one({"_id": ObjectId(rule_id)})
        if rule_data:
            rule_strings.append(rule_data['rule_string'])

    combined_ast = combine_rules(rule_strings)
    serialized_combined_ast = json.dumps(combined_ast.to_dict())

    combined_rule_string = " AND ".join(rule_strings)

    combined_rule_data = {
        "rule_string": combined_rule_string,
        "ast": serialized_combined_ast,
        "created_at": datetime.utcnow()
    }

    mongo.db.rules.insert_one(combined_rule_data)

    return redirect(url_for('main.show_rules'))  