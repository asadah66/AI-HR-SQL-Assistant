import sqlite3

# Database Creation
conn = sqlite3.connect('database.db')

#Cursor Creation
cursor = conn.cursor()

create_table ="""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    department TEXT,
    designation TEXT,
    hire_date TEXT,
    salary REAL,
    location TEXT
);
"""

cursor.execute(create_table)

# Insert Records
insert_query = '''
INSERT INTO employees (
    full_name, email, phone, department, designation, hire_date, salary, location
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
'''

# Define the values to insert
employee_values = [
    ('Anita Sharma', 'anita.sharma@example.com', '9876543210', 'HR', 'HR Manager', '2021-06-15', 75000.00, 'Bengaluru'),
    ('Rohan Mehta', 'rohan.mehta@example.com', '9123456789', 'Tech', 'Software Engineer', '2022-01-10', 90000.00, 'Remote'),
    ('Priya Desai', 'priya.desai@example.com', '9988776655', 'Marketing', 'Marketing Executive', '2023-03-01', 65000.00, 'Mumbai'),
    ('Arjun Verma', 'arjun.verma@example.com', '9012345678', 'Tech', 'Senior Developer', '2020-09-20', 110000.00, 'Bengaluru'),
    ('Neha Kapoor', 'neha.kapoor@example.com', '9876012345', 'Finance', 'Accountant', '2021-12-05', 70000.00, 'Delhi'),
    ('Vikram Rao', 'vikram.rao@example.com', '9001122334', 'Operations', 'Operations Manager', '2019-08-12', 85000.00, 'Chennai'),
    ('Simran Kaur', 'simran.kaur@example.com', '9877776655', 'HR', 'Recruiter', '2022-11-01', 60000.00, 'Remote'),
    ('Rahul Nair', 'rahul.nair@example.com', '9090909090', 'Tech', 'DevOps Engineer', '2023-07-10', 95000.00, 'Bengaluru')
]

# Execute insertion
cursor.executemany(insert_query, employee_values)
conn.commit()

data = cursor.execute("SELECT * FROM employees")

for row in data :
    print(row)

if conn:
    conn.close()