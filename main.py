import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Function to get SQL query from user input
def get_sql_query_from_text(user_query):
    groq_sys_prompt = ChatPromptTemplate.from_template("""
    You are an AI SQL Generator specialized for Human Resources (HR) applications. 
    Your task is to translate natural language queries from HR professionals into valid, optimized SQL queries that can be executed on a structured employee database.

    ### Context:
    You are working with a SQLite database containing employee records.
    You must accurately understand and convert the user's natural language request into a syntactically correct SQL query using the schema provided below.

    ### Current User Query:
    {user_query}

    ### Database Schema:
    Table: employees

    | Column       | Type    | Description                                        |
    |--------------|---------|----------------------------------------------------|
    | emp_id       | INTEGER | Auto-incrementing primary key                      |
    | full_name    | TEXT    | Full name of the employee                          |
    | email        | TEXT    | Employees email address                           |
    | phone        | TEXT    | Employees contact number                          |
    | department   | TEXT    | Department name (e.g., HR, Engineering, Sales)    |
    | designation  | TEXT    | Employees job title or role                      |
    | hire_date    | DATE    | Date the employee was hired                        |
    | salary       | REAL    | Monthly or annual salary                           |
    | location     | TEXT    | Office location or geographic location             |

    ### Responsibilities:
    - Fully comprehend the user's HR-related query.
    - Generate only the SQL `SELECT` query required to retrieve the requested information.
    - Use correct column and table names as per the schema.
    - Handle:
      - Filters (e.g., by department, salary, hire_date, location)
      - Aggregations (e.g., COUNT, AVG, SUM)
      - Conditional logic (e.g., AND, OR, BETWEEN, LIKE)
      - Sorting and limiting results
      - Date comparisons (e.g., hired after a specific date)
    - **Avoid** joins, subqueries, or unsupported SQL syntax for SQLite.
    - **Do not** return explanations or additional text — output **only the raw SQL query string**.
                                                       
    ### Special Instructions : 
        - If the user query includes both "working remotely" and a specific location (e.g., Delhi, Bengaluru), interpret this as employees who are either working remotely OR located in that specific city.
        - Example: "working remotely and in Delhi" → `location = 'Remote' OR location = 'Delhi'`
        - If only "working remotely" is mentioned, use: `location = 'Remote'`
        - If only a city/location is mentioned, use that city value in the location condition.
        - Extract city or location names directly from the query.


    ### Output Format:
    - Return **only the raw SQL query string**.
    - No markdown, no extra explanations, no formatting. Just the SQL query.
    """)
    
    model = "llama3-8b-8192"
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=model,
    )
    chain = groq_sys_prompt | llm | StrOutputParser()
    sql_query = chain.invoke({"user_query": user_query})
    return sql_query.strip()  # Remove leading or trailing spaces/newlines

# Function to retrieve data from the database
def get_data_from_database(sql_query):
    if sql_query is None:
        raise ValueError("The generated SQL query is None or invalid.")
    
    database = "database.db"  # Your SQLite database
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.execute(sql_query)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
                return results, columns
            else:
                return [], []  # No data or not a SELECT query
    except Exception as e:
        return [], []

def main():
    st.set_page_config(page_title="AI HR Database Tool", layout="wide")

    # Customizing the Streamlit layout with CSS
    st.markdown("""
    <style>
        .stTextInput > div > input {
            font-size: 16px;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ddd;
        }
        .stButton > button {
            background-color: #ffd301;
            color: black;
            font-size: 16px;
            padding: 12px 20px;
            border-radius: 8px;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton > button:hover {
            background-color: #e5c100;
        }
        .stDataFrame table {
            font-size: 14px;
        }
        .stDataFrame th {
            background-color: #f4f4f4;
            color: #333;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar for navigation
    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose a mode", ["Home", "Run Query"])

    # Home Page
    if app_mode == "Home":
        st.title("AI-Powered HR SQL Assistant")

        st.markdown("""
        ### About This Tool
        The **AI HR Database Tool** is designed to help HR professionals and analysts interact with employee databases using simple natural language queries.

        With the power of AI and SQL generation, you can:
        - 🔎 Retrieve employee records based on department, designation, salary, location, and more.
        - 📅 Filter employees by hiring dates.
        - 📊 Perform data analysis like counts, averages, and salary insights — all without writing SQL manually.
        - ⚡️ Get instant, accurate results from your employee database.

        ### ⚡️ Example Queries You Can Try:
        - "List all employees in the Marketing department"
        - "Show employees hired after January 2023"
        - "Get average salary by department"
        - "Find employees located in Bengaluru"

        ### 👨‍💻 Technology Stack
        - **Frontend:** Streamlit
        - **Backend:** SQLite
        - **AI Integration:** Llama 3 via Groq API
        - **Language:** Python

        ---
        ### 💻  Built by Asad Ahmed
        [LinkedIn](https://www.linkedin.com/in/asad-ahmed-8437a5145/)

        <small>© 2025 Asad Ahmed.</small>
        """, unsafe_allow_html=True)

       

    # Run Query Page
    elif app_mode == "Run Query":
        st.title("Run Your Query")
        user_query = st.text_area("Please enter your query:", height=100)
        submit = st.button("Submit Query")
        
        if submit:
            sql_query = get_sql_query_from_text(user_query)
            if sql_query:
                retrieved_data, columns = get_data_from_database(sql_query)
                if retrieved_data:
                    st.subheader("SQL Query")
                    st.code(sql_query, language='sql')
                    st.subheader("Query Results")
                    st.dataframe(pd.DataFrame(retrieved_data, columns=columns))
                    
                else:
                    st.error("No data retrieved or invalid query.")
            else:
                st.error("Error generating SQL query.")

if __name__ == "__main__":
    main()
