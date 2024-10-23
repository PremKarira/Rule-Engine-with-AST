# Rule Engine Application

This is a Rule Engine application built with Flask, MongoDB, and Python. The application allows users to create, evaluate, combine, and manage rules using an intuitive web interface. It supports displaying Abstract Syntax Trees (AST) for visualizing rules and provides functionality to delete or combine selected rules.

## Features

- **Create Rules**: Add new rules with custom conditions.
- **Show Rules**: View all existing rules with options to show their AST.
- **Combine Rules**: Select multiple rules and combine them into a single rule.
- **Delete Rules**: Remove individual or all rules from the database.
- **AST Visualization**: Display the Abstract Syntax Tree for each rule to understand its structure.

## Technologies Used

- **Backend**: Flask
- **Database**: MongoDB
- **Frontend**: HTML, CSS (no Bootstrap)
- **JavaScript**: For dynamic interaction (show/hide AST)

## Getting Started

### Prerequisites

- Python 3.6+
- MongoDB
- pip (Python package installer)

### Running the Application

1. Clone the repository:
   - `git clone https://github.com/PremKarira/Rule-Engine-with-AST`
   - `cd rule-engine`

2. Install the required packages:
   - `pip install -r requirements.txt`

3. Set up your MongoDB database. Update your MongoDB URI in a `.env` file:
   - `MONGO_URI=mongodb://localhost:27017/yourdbname`

4. Run the Flask application:
   - `python app.py`


## Usage

- Use the provided web interface to create, view, combine, and delete rules.
- You can visualize each rule's AST by clicking the "Show AST" button next to each rule.

## Optimizing Combine Logic

The current implementation of the combine rules feature is functional but can be optimized for better performance and reducing comparisons. 
  
- **Improved AST Construction**: We will explore more efficient algorithms for constructing the Abstract Syntax Tree (AST) when combining rules, minimizing memory usage and improving response times.



