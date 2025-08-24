# analysis.py

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

def analyze_data(customers, products, orders):
    import pandas as pd

    if not orders:
        print("Нет данных для анализа")
        return

    df_orders = pd.DataFrame([{
        'OrderID': o.oid,
        'CustomerID': o.customer.cid,
        'CustomerName': o.customer.name,
        'Date': o.date,
        'Products': [p.pid for p in o.products]
    } for o in orders])

    df_customers = pd.DataFrame([{
        'CustomerID': c.cid,
        'Name': c.name,
        'Address': c.address
    } for c in customers])

    df_orders['Date'] = pd.to_datetime(df_orders['Date'])
    df_products = pd.DataFrame([{
        'ProductID': p.pid,
        'Name': p.name,
        'Category': p.category,
        'Price': p.price
    } for p in products])

    # 1. ТОП 5 клиентов по заказам
    top_clients = df_orders['CustomerID'].value_counts().head(5)
    top_clients = top_clients.reset_index()
    top_clients.columns = ['CustomerID', 'Number of Orders']
    top_clients = top_clients.merge(df_customers, on='CustomerID', how='left')

    plt.figure(figsize=(8, 4))
    sns.barplot(data=top_clients, x='Number of Orders', y='Name')
    plt.title('ТОП 5 клиентов по числу заказов')
    plt.tight_layout()
    plt.show()

    # 2. Динамика заказов по датам
    plt.figure(figsize=(10, 4))
    df_orders.groupby(df_orders['Date'].dt.date).size().plot()
    plt.title('Динамика заказов по датам')
    plt.xlabel('Дата')
    plt.ylabel('Количество заказов')
    plt.tight_layout()
    plt.show()

    # 3. Граф связей клиентов по общим товарам
    G = nx.Graph()

    for c in customers:
        G.add_node(c.cid, label=c.name)

    for i, c1 in enumerate(customers):
        for c2 in customers[i+1:]:
            p1 = set()
            p2 = set()
            for o in orders:
                if o.customer.cid == c1.cid:
                    p1.update(p.pid for p in o.products)
                elif o.customer.cid == c2.cid:
                    p2.update(p.pid for p in o.products)
            shared = p1.intersection(p2)
            if shared:
                G.add_edge(c1.cid, c2.cid, weight=len(shared))
    plt.figure(figsize=(8,6))
    pos = nx.spring_layout(G, k=0.5)
    labels = {node: G.nodes[node]['label'] for node in G.nodes}
    nx.draw(G, pos, labels=labels, with_labels=True, node_color='skyblue', edge_color='gray')
    plt.title('Граф связей по товарам')
    plt.show()