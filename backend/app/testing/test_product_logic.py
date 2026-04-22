import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Vendor, Project, ProjectProduct, DraftProjectPage
from app.routers import products, projects
from app.routers.checkout import create_checkout
from app.schemas import CheckoutCreateRequest, CheckoutCustomer, CheckoutItem
from app.models import MediaObjectMetadata


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_user(db_session, username: str) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        phone="1234567890",
        hash_password="pw",
        first_name=username,
        last_name="User",
        stripe_customer_id=f"cus_{username}",
    )
    db_session.add(user)
    db_session.commit()
    return user


def make_vendor(db_session, user: User, name: str) -> Vendor:
    vendor = Vendor(
        business_name=name,
        email=f"{name.lower()}@example.com",
        owner=user.id,
        phone="1234567890",
        stripe_connect_id=f"acct_{name.lower()}",
        payouts_enabled=True,
        requirements_due_for_payment="",
    )
    db_session.add(vendor)
    db_session.commit()
    return vendor


def make_project(db_session, vendor: Vendor, name: str, is_live: bool = False) -> Project:
    project = Project(name=name, vendor=vendor.id, is_live=is_live)
    db_session.add(project)
    db_session.commit()
    return project


def make_product(
    db_session,
    project: Project,
    name: str,
    *,
    is_active: bool = True,
    is_published: bool = False,
    stock: int = 5,
) -> ProjectProduct:
    product = ProjectProduct(
        project_id=project.id,
        name=name,
        description=f"{name} description",
        sale_price=1000,
        shipping_price=250,
        stock=stock,
        is_active=is_active,
        is_published=is_published,
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.mark.asyncio
async def test_product_routes_enforce_vendor_ownership(db_session):
    owner = make_user(db_session, "owner")
    owner_vendor = make_vendor(db_session, owner, "OwnerShop")
    project = make_project(db_session, owner_vendor, "Owner Project")
    product = make_product(db_session, project, "Owner Product")

    intruder = make_user(db_session, "intruder")
    make_vendor(db_session, intruder, "IntruderShop")

    with pytest.raises(HTTPException) as create_exc:
        await products.create_product(
            products.ProductIn(
                project_id=project.id,
                name="Hijack",
                description="Nope",
                sale_price=100,
                shipping_price=10,
                stock=1,
            ),
            db=db_session,
            user=intruder,
        )
    assert create_exc.value.status_code == 403

    with pytest.raises(HTTPException) as list_exc:
        await products.get_all_products(project.id, db=db_session, user=intruder)
    assert list_exc.value.status_code == 403

    with pytest.raises(HTTPException) as update_exc:
        await products.update_product(
            product.id,
            products.ProductUpdate(name="Stolen"),
            db=db_session,
            user=intruder,
        )
    assert update_exc.value.status_code == 403


@pytest.mark.asyncio
async def test_inactive_products_stay_manageable_in_admin_list(db_session):
    owner = make_user(db_session, "manager")
    vendor = make_vendor(db_session, owner, "ManagerShop")
    project = make_project(db_session, vendor, "Catalog")

    active_product = make_product(db_session, project, "Active Product", is_active=True)
    inactive_product = make_product(db_session, project, "Inactive Product", is_active=False)

    result = await products.get_all_products(project.id, db=db_session, user=owner)

    returned_ids = {item["id"] for item in result}
    assert active_product.id in returned_ids
    assert inactive_product.id in returned_ids


@pytest.mark.asyncio
async def test_publish_only_exposes_active_products_publicly(db_session):
    owner = make_user(db_session, "publisher")
    vendor = make_vendor(db_session, owner, "PublisherShop")
    project = make_project(db_session, vendor, "Storefront")
    db_session.add(DraftProjectPage(project=project.id, name="Home", layout=[]))
    db_session.commit()

    active_product = make_product(db_session, project, "Published Product", is_active=True)
    inactive_product = make_product(db_session, project, "Hidden Product", is_active=False)

    await projects.publish_project(project.id, db=db_session, user=owner)

    db_session.refresh(active_product)
    db_session.refresh(inactive_product)

    assert active_product.is_published is True
    assert inactive_product.is_published is False

    public_products = await projects.get_project_products(str(project.id), db=db_session)
    public_ids = {item["id"] for item in public_products["products"]}

    assert active_product.id in public_ids
    assert inactive_product.id not in public_ids


@pytest.mark.asyncio
async def test_checkout_rejects_products_not_available_for_purchase(db_session):
    owner = make_user(db_session, "checkout")
    vendor = make_vendor(db_session, owner, "CheckoutShop")
    project = make_project(db_session, vendor, "Checkout Project")
    unavailable_product = make_product(
        db_session,
        project,
        "Unavailable Product",
        is_active=False,
        is_published=False,
    )

    with pytest.raises(HTTPException) as checkout_exc:
        await create_checkout(
            CheckoutCreateRequest(
                project_id=project.id,
                items=[CheckoutItem(product_id=unavailable_product.id, quantity=1)],
                customer=CheckoutCustomer(email="buyer@example.com", name="Buyer Name"),
                payment_method="manual",
            ),
            db=db_session,
        )

    assert checkout_exc.value.status_code == 400
    assert "not available for purchase" in checkout_exc.value.detail


def test_ecommerce_layout_uses_grid_positions_and_proxy_images(db_session):
    owner = make_user(db_session, "layout")
    vendor = make_vendor(db_session, owner, "LayoutShop")
    project = make_project(db_session, vendor, "Layout Project")
    db_session.add(
        DraftProjectPage(
            project=project.id,
            name="Home",
            layout=[
                {
                    "id": "navbar-1",
                    "type": "navbar",
                    "col": 1,
                    "row": 1,
                    "colSpan": 12,
                    "rowSpan": 1,
                    "props": {
                        "links": ["Home", "About"],
                        "style": {
                            "fontSize": 20,
                            "backgroundColor": "#111111",
                            "backgroundOpacity": 1,
                            "color": "#ffffff",
                            "textAlign": "center",
                        },
                    },
                }
            ],
        )
    )
    db_session.commit()

    first = make_product(db_session, project, "First Product")
    second = make_product(db_session, project, "Second Product")

    metadata = MediaObjectMetadata(
        project_id=project.id,
        file_key="products/first/image.jpg",
        file_type="image/jpeg",
        file_size_bytes=123,
    )
    db_session.add(metadata)
    db_session.flush()
    first.product_image = metadata.id
    db_session.commit()

    layout = products.create_ecommerce_layout([first, second], db_session, project.id)

    assert layout[0]["type"] == "navbar"
    assert layout[0]["col"] == 1
    assert layout[0]["row"] == 1
    assert layout[0]["colSpan"] == 12
    assert layout[0]["props"]["links"] == ["Home", "About"]

    assert layout[1]["col"] == 1
    assert layout[1]["row"] == 2
    assert layout[1]["colSpan"] == 4
    assert layout[1]["rowSpan"] == 5
    assert layout[1]["props"]["imageUrl"] == "/api/site/_media?file_key=products%2Ffirst%2Fimage.jpg"

    assert layout[2]["col"] == 5
    assert layout[2]["row"] == 2
