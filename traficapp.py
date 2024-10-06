import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import yagmail
# import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
# import components.authentication as authenticate

# Styling
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


# with open('custom_css-cal.css') as css:
#      st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


# Function to calculate ad cost for a traffic source
def calculate_ad_cost(visitors, acquisition_type, cpm, cpc):
    if acquisition_type == "impression":
        return cpm * visitors
    elif acquisition_type == "clicks":
        return cpc * visitors
    else:
        return 0


# Function to calculate total ad cost for all traffic sources
def calculate_total_ad_cost(traffic_sources):
    total_ad_cost = 0
    for source in traffic_sources:
        total_ad_cost += source["ad_cost"]
    return total_ad_cost

# Function to calculate total ad cost for all product types
def calculate_total_ad_cost_for_products(products):
    total_ad_cost = 0
    for product in products:
        total_ad_cost += calculate_total_ad_cost(product["traffic_sources"])
    return total_ad_cost


# Function to calculate potential lead for a traffic source
def calculate_potential_leads(visitors, ctr):
    return ctr * visitors


# Function to calculate total potential_leads for all traffic sources
def calculate_total_potential_leads(traffic_sources):
    total_potential_lead = 0
    for source in traffic_sources:
        total_potential_lead += source["potential_lead"]
    return total_potential_lead

# Function to calculate total ad cost for all product types
def calculate_total_potential_leads_for_products(products):
    total_potential_lead = 0
    for product in products:
        total_potential_lead += calculate_total_potential_leads(product["traffic_sources"])
    return total_potential_lead


# Function to calculate total closed customers for a traffic source
def calculate_total_closed_customers(traffic_sources):
    total_closed_customers = 0
    for source in traffic_sources:
        total_closed_customers += source["closed_customers"]
    return total_closed_customers

def calculate_total_closed_customers_for_products(products):
    total_closed_customers = 0
    for product in products:
        total_closed_customers += calculate_total_ad_cost(product["traffic_sources"])
    return total_closed_customers


# Function to calculate total closed customers for a traffic source
def calculate_total_visitors(traffic_sources):
    total_visitors = 0
    for source in traffic_sources:
        total_visitors += source["visitors"]
    return total_visitors

def calculate_total_monthly_revenue(products):
    total_visitors = 0
    for source in products:
        total_visitors += source["monthly_revenue"]
    return total_visitors

def calculate_total_product_cost(products):
    total_product_cost = 0
    for source in products:
        total_product_cost += source["actual_product_cost"]
    return total_product_cost

# Function to calculate total Operating expenses in different categories
def calculate_total_expenses(expenses):
    total_expenses = sum(expenses.values())
    return total_expenses

# Function to calculate total Overhead expenses in different categories
def calculate_total_overhead_expenses(overhead_expenses):
    total_overhead_expenses = sum(overhead_expenses.values())
    return total_overhead_expenses

# cpl = total_market_spent / visitors
# ltv = revenue_monthly / closed_customers
# cpa = total_market_spent / closed_customers

# Streamlit app title
st.title("Traffic Conversion  Calculator")


# Allow users to input product information
product_count = st.number_input("Enter the number of products:", min_value=1, value=1, step=1)

products = []
count = 100
p_count = 1000
pn_count = 2000
p_cost = 4000
exp_cat = 5000
cpm_count = 3000
vis_count = 6000
acq_count = 7000
freq_count = 8000
p_struct = 9000
overhead_cat = 400
over_freq_count = 600
overhead_count = 300
cat_count = 10000
ctr_count = 11000
sales_count =12000

# product_name = ""
for i in range(product_count):



    pn_count += 1
    product_label = st.write("Enter your Product Name to update the label")
    product_name = st.text_input(f"{product_label}", key = pn_count)
    st.subheader(f"Product Name: {product_name}")

    expenses = {}
    overhead_expenses = {}
        
    # st.markdown('## Product Cost Structure')
    with st.expander(f"{product_name} Product Cost Structure"):
        p_cost += 1
        p_struct += 1
        exp_cat += 1
        count += 3
        p_count += 2
        # freq_count+= 1
        product_price = st.number_input(f"{product_name} Price", min_value=0.0, key = p_count)
        price_type = st.radio(f"{product_name} Price Type", ("Yearly", "Monthly", "OneTime"), key = count)
        if price_type == "Yearly":
            product_price = product_price / 12
        else:
            product_price = product_price
        prd_cost_structure=st.text_area(f"{product_name} Product", key = p_struct)
        product_cost=st.number_input(f"{product_name} Product Cost", min_value=0.0, key = p_cost)
        options= ["Marketing", "Equipment", "Training", "Software", "Utility", "Payroll", "Phone & Internet", "Accounting", "Content Creation", "Office Rent", "Other Expenses"]
        expense_categories = st.multiselect(f"Business Expenses (Operating Cost directly related to {product_name} Product)", options=options, key=exp_cat)

                
        for category in expense_categories:
            freq_count += 2
            cat_count += 1
            expenses[category] = st.number_input(f"{category} Direct Expense", min_value=0.0, key = cat_count)
            bill_freq = st.selectbox(f"{category} Direct Expense billing frequency", ("Yearly", "Monthly", "OneTime"), key=freq_count)
            if bill_freq == "Yearly":
                expenses[category] = (expenses[category])/12
            else:
                expenses[category] = (expenses[category])

                
    with st.expander("Business Overhead Cost Structure"):
        p_cost += 1
        p_struct += 1
        overhead_cat += 1
        prd_cost_structure=st.text_area(f"{product_name} Product Cost Structure", key = p_struct)
        # product_cost=st.number_input(f"{product_name} Product Cost", min_value=0.0, key = p_cost)
        overhead_options= ["Marketing", "Equipment", "Training", "Software", "Utility", "Payroll", "Phone & Internet", "Accounting", "Content Creation", "Office Rent", "Other Expenses"]
        expense_overhead_categories = st.multiselect(f"Other Business Expenses (Overhead Cost associated with the overall business operations)", options=overhead_options, key=overhead_cat)

        for overhead in expense_overhead_categories:
            over_freq_count += 2
            overhead_count += 1
            overhead_expenses[overhead] = st.number_input(f"{overhead} Overhead Expense", min_value=0.0, key = overhead_count)
            over_bill_freq = st.selectbox(f"{overhead} Overhead Expense billing frequency", ("Yearly", "Monthly", "OneTime"), key=over_freq_count)
            if over_bill_freq == "Yearly":
                overhead_expenses[overhead] = (overhead_expenses[overhead])/12
            else:
                overhead_expenses[overhead] = overhead_expenses[overhead]


    traffic_sources = []
    # st.subheader("Traffic Sources")
    # Input parameters inside a st.expander
    with st.sidebar.expander(f"Traffic Source Data for {product_name} product"): 
        count += 1  
        source_count = st.number_input(f"Enter the number of traffic sources for {product_name} :", min_value=1, value=1, step=1, key = count)
    
        for j in range(source_count):
            acq_count +=3 
            pn_count += 3   
            cpm_count += 3 
            vis_count += 3 
            sales_count += 1

            st.subheader(f"{product_name} Traffic Source {j+1}")
            acquisition_type = st.radio(f"Acquisition Type {j+1}",("Impression", "Clicks"), key=acq_count)
            # for acq in acquisition_type:
            ctr_count += 3
            cpm_count += 3 
            pn_count += 3

            if acquisition_type == "Impression":
                cpm = st.number_input(f"CPM (Cost Per Mille) {j+1} ", min_value=0.0, value=0.0, step=0.01, key=cpm_count)                
                ctr = st.slider(f"CTR (Click Through Rate) {j+1}", min_value=0.0, max_value=1.0, step=0.01, key=ctr_count)
                cpc = None 
            else:
                cpm = None           
                ctr = st.slider(f"CTR (Click Through Rate) {j+1}", min_value=0.0, max_value=1.0, step=0.01, key=ctr_count)
                cpc = st.number_input(f"CPC {j+1}", min_value=0.0, value=0.0, step=0.01, key=pn_count) 

            visitors = st.number_input(f"Visitors {j+1}", min_value=0, key=vis_count)
            ad_cost = calculate_ad_cost(visitors, acquisition_type.lower(), cpm, cpc)
            potential_lead = calculate_potential_leads(visitors, ctr)
            sales_conversion_rate = st.slider("Sales Conversion Rate:", min_value=0.0, max_value=1.0, step=0.01, key=sales_count)
            closed_customers = potential_lead * sales_conversion_rate
            monthly_revenue = closed_customers * product_price
            actual_product_cost = product_cost * closed_customers
            traffic_sources.append({"acquisition_type": acquisition_type.lower(), "visitors": visitors, "cpm": cpm, "cpc": cpc, "ctr": ctr, "ad_cost": ad_cost, 
                                    "sales_conversion_rate": sales_conversion_rate, "potential_lead": potential_lead, "closed_customers": closed_customers})
        products.append({"name": product_name, "price": product_price, "actual_product_cost": actual_product_cost, "expenses": expenses, "overhead_expenses": overhead_expenses, "monthly_revenue": monthly_revenue, "traffic_sources": traffic_sources})
    
    if st.sidebar.button("Conversion Performance"):
 
#Calculate and display results for each product
        for product in products:
            total_ad_cost = calculate_total_ad_cost(product["traffic_sources"])
            total_expenses = calculate_total_expenses(product["expenses"])
            total_overhead_expenses = calculate_total_overhead_expenses(product["overhead_expenses"])
            total_product_cost = calculate_total_product_cost([product])
            total_ad_cost_all_products = calculate_total_ad_cost_for_products([product])
            total_visitors = calculate_total_visitors(product["traffic_sources"])
            total_potential_leads = calculate_total_potential_leads_for_products([product])
            total_closed_customers = calculate_total_closed_customers_for_products([product])
            total_monthly_revenue = calculate_total_monthly_revenue([product])
            total_monthly_profit = total_monthly_revenue - total_expenses - total_overhead_expenses - total_product_cost
            total_cpl = total_ad_cost_all_products / total_visitors
            total_ltv = total_monthly_revenue / total_closed_customers
            total_cpa = total_ad_cost_all_products / total_closed_customers
            total_aov = total_monthly_revenue / total_closed_customers
            total_roas = (total_monthly_revenue/total_ad_cost_all_products) * 100

        st.markdown('## Conversion Performance Metrics')
                    # col1, col2, col3 = st.columns(3)
                
        def make_grid(cols,rows):
            grid = [0]*cols
            for i in range(cols):
                with st.container():
                    grid[i] = st.columns(rows)
            return grid    
            
        mygrid = make_grid(3,3)

        mygrid[0][0].metric(label = "Monthly Revenue (estimated)",
                    value = (total_monthly_revenue)
                    )

        mygrid[0][1].metric(label = "Monthly Profit (estimated)",
                    value = (total_monthly_profit)
                    )

        mygrid[0][2].metric(label = "Leads",
                    value = (total_potential_leads)
                    )

        mygrid[1][0].metric(label = "Cost Per Acqusition",
                    value = (total_cpa)
                    )

        mygrid[1][1].metric(label = "Cost Per Lead",
                    value = (total_cpl)
                    )

        mygrid[1][2].metric(label = "ROAS",
                    value = (total_roas)
                    )

#     # Display results for the current product
#     st.subheader(f"Product: {product['name']}")
#     st.write(f"Total Ad Cost: ${total_ad_cost:.2f}")
#     st.write(f"Total Expenses: ${total_expenses:.2f}")
#     st.write(f"Total Ad Cost for All Traffic Sources: ${total_ad_cost_all_products:.2f}")
#     st.write("---")

# Streamlit app is automatically rendered
