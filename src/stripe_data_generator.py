import stripe
import random
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Definir chave da API do Stripe
stripe.api_key = os.getenv('STRIPE_TEST_KEY')

# Sample data for generating random names
first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack", "Quinton", "Akriti", "Justin", "Marcos"]
last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Wall", "Chau", "Keswani", "Marx"]

# Sample clothing product names
clothing_names = [
    "T-Shirt", "Jeans", "Jacket", "Sweater", "Hoodie",
    "Shorts", "Dress", "Blouse", "Skirt", "Pants",
    "Shoes", "Sandals", "Sneakers", "Socks", "Hat",
    "Scarf", "Gloves", "Coat", "Belt", "Tie",
    "Tank Top", "Cardigan", "Overalls", "Tracksuit", "Polo Shirt",
    "Cargo Pants", "Capris", "Dungarees", "Boots", "Cufflinks",
    "Raincoat", "Peacoat", "Blazer", "Slippers", "Underwear",
    "Leggings", "Windbreaker", "Tracksuit Bottoms", "Beanie", "Bikini"
]

# List of random colors
colors = [
    "Red", "Blue", "Green", "Yellow", "Black", "White", "Gray",
    "Pink", "Purple", "Orange", "Brown", "Teal", "Navy", "Maroon",
    "Gold", "Silver", "Beige", "Lavender", "Turquoise", "Coral"
]

# Function to create sample customers with random names
def create_customers(count=5):
    customers = []
    for _ in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"

        customer = stripe.Customer.create(
            name=name,
            email=email,
            description="Sample customer for testing"
        )
        customers.append(customer)
        print(f"Created Customer: {customer['name']} (ID: {customer['id']})")
    return customers

# Function to create sample products with random clothing names and colors
def create_products(count=3):
    products = []
    for _ in range(count):
        color = random.choice(colors)
        product_name = random.choice(clothing_names)
        full_name = f"{color} {product_name}"
        product = stripe.Product.create(
            name=full_name,
            description=f"This is a {color.lower()} {product_name.lower()}"
        )
        products.append(product)
        print(f"Created Product: {product['name']} (ID: {product['id']})")
    return products

# Function to create prices for the products with random unit_amount
def create_prices(products, min_price=500, max_price=5000):
    prices = []
    for product in products:
        unit_amount = random.randint(min_price, max_price)  # Random amount in cents
        price = stripe.Price.create(
            unit_amount=unit_amount,
            currency="usd",
            product=product['id']
        )
        prices.append(price)
        print(f"Created Price: ${unit_amount / 100:.2f} for Product {product['name']} (ID: {price['id']})")
    return prices

# Function to create random invoices for each customer
def create_invoices(customers, prices, max_invoices_per_customer=5):
    invoices = []
    for customer in customers:
        num_invoices = random.randint(1, max_invoices_per_customer)
        for _ in range(num_invoices):
            price = random.choice(prices)
            # Create an invoice item first
            invoice_item = stripe.InvoiceItem.create(
                customer=customer['id'],
                price=price['id'],
                description=f"Purchase of {price['product']}"
            )

            # Create the invoice
            invoice = stripe.Invoice.create(
                customer=customer['id'],
                auto_advance=False,  # Don't auto-finalize
                collection_method='charge_automatically',
                description=f"Invoice for {customer['name']}"
            )

            # Finalize and pay the invoice manually
            invoice = stripe.Invoice.finalize_invoice(invoice['id'])
            if invoice.status != 'paid':  # Only pay if not already paid
                invoice = stripe.Invoice.pay(invoice['id'])

            invoices.append(invoice)
            print(f"Created Invoice for Customer {customer['name']} (Amount: ${price['unit_amount'] / 100:.2f})")
    return invoices

# Main function to create sample data
def main():
    print("Creating sample customers with random names...")
    customers = create_customers(count=5)

    print("\nCreating sample products with random clothing names and colors...")
    products = create_products(count=5)

    print("\nCreating prices for products with random amounts...")
    prices = create_prices(products, min_price=500, max_price=5000)

    print("\nCreating random invoices for each customer...")
    invoices = create_invoices(customers, prices, max_invoices_per_customer=2)

    print("\nSample data creation complete!")
    print(f"Created {len(customers)} customers, {len(products)} products, and {len(invoices)} invoices.")

if __name__ == "__main__":
    main()
