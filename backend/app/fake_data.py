import random

from datetime import datetime, timedelta
from faker import Faker


from sqlalchemy.orm import Session
from sqlmodel import create_engine

from app.models import (
    ProjectOrder, ProjectOrderItem, ProjectCustomer, 
    ProjectCustomerAddress, ProjectProduct, Project, User, Vendor
)

# Initialize Faker
fake = Faker()

def seed_orders(db: Session, num_orders=20):
    print(f"Starting to seed {num_orders} orders...")

    # 1. Get existing projects and products to link to
    project = db.query(Project).join(Vendor, Project.vendor == Vendor.id).join(User, Vendor.owner == User.id).where(User.email == "jared@sandfoss.net").first()
    
    products = db.query(ProjectProduct).where(ProjectProduct.project_id == project.id).all()


    for i in range(num_orders):
        # Pick a random project
        target_project = project
        
        # Calculate random dates over the last 30 days for your "Revenue Over Time" chart
        random_days_ago = random.randint(0, 30)
        order_date = datetime.utcnow() - timedelta(days=random_days_ago)

        # Generate a random total amount (between $20.00 and $500.00 in cents)
        total_cents = random.randint(2000, 50000)
        platform_fee = round(total_cents * 0.07)
        vendor_amount = total_cents - platform_fee

        # 2. Create the Order
        order = ProjectOrder(
            project=target_project.id,
            stripe_id=f"cs_test_{fake.uuid4()}",
            amount_total=total_cents,
            currency="USD",
            payment_status=True,
            platform_fee_cents=platform_fee,
            vendor_amount_cents=vendor_amount,
            shipping_price_cents=random.choice([0, 500, 1000, 1500]),
            created_at=order_date # Ensure your model supports this field
        )
        db.add(order)
        db.flush() # Get the order.id

        # 3. Create a Customer for this order
        customer = ProjectCustomer(
            order=order.id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number()
        )
        db.add(customer)
        db.flush()

        # 4. Create Customer Address
        address = ProjectCustomerAddress(
            customer=customer.id,
            house_number=fake.building_number(),
            street_name=fake.street_name(),
            city=fake.city(),
            state=fake.state_abbr(),
            postal_code=fake.postcode()
        )
        db.add(address)

        # 5. Create 1-3 random Items for this order
        num_items = random.randint(1, 3)
        selected_products = products[:num_items]

        for prod in selected_products:
            item = ProjectOrderItem(
                order=order.id,
                item=prod.id,
                quantity=random.randint(1, 4),
                price_at_purchase=prod.sale_price,
                shipping_status=random.choice(["PENDING", "SHIPPED", "DELIVERED"])
            )
            db.add(item)

    try:
        db.commit()
        print(f"Successfully seeded {num_orders} orders with customers and items!")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed data: {e}")

if __name__ == "__main__":
    # Create a new session instance
    from app.database import SessionLocal 
    
    db = SessionLocal()

    try:
        # Check if data already exists to prevent accidental double-seeding
        order_count = db.query(ProjectOrder).count()
        if order_count > 1000:
            print(f"Database already has {order_count} orders. Skipping seed to prevent duplicates.")
        else:
            seed_orders(db, num_orders=50)
    finally:
        db.close()