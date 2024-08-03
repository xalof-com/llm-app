from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate

def react_tools_chat_prompt(react_repeat:int=3):
    system_messages = [
        "You are a good assistant. "
        "You must use Vietnamese to answer the question. "
        # "Do NOT reformulate the question. "
        "You have to access the following tools to answer the question:"
        "\n\n"
        "{tools}"
        "\n\n"
        "To use the tools, you MUST follow the format:\n\n"
        "Question: The input question you must answer.\n"
        "Thought: You should always think about what to do.\n"
        # "Thought: Do I need to use a tool? Yes.\n"
        "Action: The action to take, it should be one of [{tool_names}].\n"
        "Action Input: The input the the action.\n"
        "Observation: the result of the action.\n"
        # f"... (This Thought/Action/Action Input/Observation can repeat {react_repeat} times)"
        "\n\n"
        "If the question related to SQL query,  do NOT convert to SQL format, just keep it as it is."
        "When you have the best answer to say to the Human, you MUST use the format:\n\n"
        "Thought: Now, I've got the final answer.\n"
        "Final Answer: The final answer to the original input question. "
        "Additionally, only include the source, page of the answer if any."
        # "Final Answer: [your final answer to the original input question here]"
        # "Final Answer: [your response here]"
        "\n\n"
        "If you don't know the answer, just say that you don't know.\n"
        "Always say: 'Cảm ơn bạn đã hỏi nha!' after the answer."
        "\n\n"
        "Begin!"
        "\n\n"
        "Conversation history:\n"
        "{chat_history}"
        "\n\n"
        "Question: {input}\n"
        "{agent_scratchpad}"
    ]
    # print("".join(system_messages))

    return PromptTemplate(
        template="".join(system_messages),
        input_variables=["tools", "tool_names", "chat_history", "input", "agent_scratchpad"]
    )

def write_sql_prompt():
    
    # system_messages = [
    #     'You are a MySQL expert. Given an input question, '
    #     'first create a syntactically correct MySQL query to run, '
    #     'then look at the results of the query and return the answer to the input question. '
    #     'Unless the user specifies in the question a specific number of examples to obtain, '
    #     'query for at most {top_k} results using the LIMIT clause as per MySQL. '
    #     'You can order the results to return the most informative data in the database. '
    #     'Pay attention to use only the column names you can see in the tables below. '
    #     'Be careful to not query for columns that do not exist. '
    #     'Also, pay attention to which column is in which table. '
    #     'Pay attention to use CURDATE() function to get the current date, if the question involves "today".'
    #     '\n\n'
    #     'Use the following format:'
    #     '\n\n'
    #     'Question: Question here\n'
    #     'SQLQuery: SQL Query to run\n'
    #     'SQLResult: Result of the SQLQuery\n'
    #     'Answer: Final answer here'
    #     '\n\n'
    #     'Only use the following tables:\n'
    #     '{table_info}'
    #     '\n\n'
    #     'Question: {input}\n'
    #     'SQLQuery:'
    # ]

    system_messages = [
        "You are a MySQL expert. Given an input question, "
        "create a syntactically correct MySQL query to run, "
        "then look at the results of the query and return the answer to the input question. "
        "Unless the user specifies in the question a specific number of examples to obtain, "
        "query for at most {top_k} results using the LIMIT clause as per MySQL. "
        "Pay attention to use only the column names you can see in the tables below. "
        "Be careful to not query for columns that do not exist. "
        "Also, pay attention to which column is in which table. "
        "Pay attention to use CURDATE() function to get the current date, if the question involves \"today\"."        
        # "\n\n"
        # 'Use the following format:'
        # '\n\n'
        # 'Question: Question here\n'
        # 'SQLQuery: SQL Query to run\n'
        # 'SQLResult: Result of the SQLQuery\n'
        # 'Answer: Final answer here'

        "\n\n"
        "Only use the following tables:\n"
        "{table_info}"
        "\n\n"
        # "Question: {question}\n"
        "Question: {input}\n"
        "SQL Query:"
    ]


    return PromptTemplate.from_template(template="".join(system_messages))

def sql_few_shot_prompt():
    prefix_messages = [
        "You are a MySQL expert. "
        "Given an input question, "
        "create a syntactically correct MySQL query to run. "
        "Unless otherwise specificed, do not return more than {top_k} rows."
        "\n\n"
        "Here is the relevant table info:\n"
        "{table_info}"
        "\n\n"
        "Below are a number of examples of questions and their corresponding SQL queries."
    ]

    suffix_messages = [
        "User input: {input}\n"
        "SQL query: "
    ]

    sql_examples = [
        {
            "input": "Có bao nhiêu kênh (channel) bán hàng",
            "query": "SELECT COUNT(*) FROM channels"
        },
        {
            "input": "Có bao nhiêu kênh (chanels) của sàn (exchange) SHOPEE, LAZADA",
            "query": "SELECT exchange, COUNT(id) FROM channels WHERE exchange IN ('SHOPEE', 'LAZADA') GROUP BY exchange"
        },
        {
            "input": "Có bao nhiêu đơn hàng của tất cả sàn",
            "query": "SELECT ch.exchange, COUNT(o.id) FROM orders AS o JOIN channels AS ch ON o.channel_id = ch.id GROUP BY ch.exchange"
        },
        {
            "input": "Có bao nhiêu đơn hàng thành công (complete) của tất cả sàn từ 2022-01-01 đến 2022-08-30",
            "query": "SELECT ch.exchange, COUNT(o.id) FROM orders AS o JOIN channels AS ch ON o.channel_id = ch.id WHERE o.created_at BETWEEN '2022-01-01' AND '2022-08-30' GROUP BY ch.exchange"
        },
        {
            "input": "Có bao nhiêu đơn hàng thành công (complete) của sàn SHOPEE, LAZADA",
            "query": "SELECT ch.exchange, COUNT(o.id) FROM orders AS o JOIN channels AS ch ON o.channel_id = ch.id WHERE ch.exchange IN ('SHOPEE', 'LAZADA') AND o.order_status IN ('COMPLETED', 'complete', 'delivered') GROUP BY ch.exchange"
        },
        {
            "input": "Doanh thu theo từng sàn",
            'query': "SELECT ch.exchange, SUM(oi.qty_ordered * oi.price) FROM (order_items AS oi JOIN orders AS o ON o.order_sn = oi.order_sn) JOIN channels AS ch ON o.channel_id = ch.id WHERE o.order_status IN ('COMPLETED', 'complete', 'delivered') GROUP BY ch.exchange"
        },
        {
            "input": "Tổng doanh thu của tất cả các sàn",
            'query': "SELECT SUM(oi.qty_ordered * oi.price) AS total_revenue FROM (order_items AS oi JOIN orders AS o ON o.order_sn = oi.order_sn) JOIN channels AS ch ON o.channel_id = ch.id WHERE o.order_status IN ('COMPLETED', 'complete', 'delivered')"
        },
        {
            "input": "Doanh thu của từng sàn từ 2022-01-01 đến 2022-08-30",
            'query': "SELECT ch.exchange, SUM(oi.qty_ordered * oi.price) AS revenue FROM (order_items AS oi JOIN orders AS o ON o.order_sn = oi.order_sn) JOIN channels AS ch ON o.channel_id = ch.id WHERE o.order_status IN ('COMPLETED', 'complete', 'delivered') AND o.created_at BETWEEN '2022-01-01' AND '2022-08-30' GROUP BY ch.exchange"
        }
    ]

    sql_example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
    prompt = FewShotPromptTemplate(
        examples=sql_examples,
        example_prompt=sql_example_prompt,
        prefix="".join(prefix_messages),
        suffix="".join(suffix_messages),
        input_variables=["input", "top_k", "table_info"],
    )

    return prompt


def answer_sql_prompt():
    system_messages = [
        'Given the following user question, '
        'corresponding SQL query, and SQL result, '
        'write a natural language answer.'
        '\n\n'
        'Question: {question}\n'
        'SQL Query: {query}\n'
        'SQL Result: {result}'
    ]

    return PromptTemplate.from_template(template="".join(system_messages))
