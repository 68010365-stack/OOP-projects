from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("demo")
BASE_URL = "http://host.docker.internal:8000"


# -------------------------
# LOGIN
# -------------------------

@mcp.tool()
async def login_member(user_id: str, password: str):
    """Login member"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/login/member",
            json={
                "user_id": user_id,
                "password": password
            }
        )
        return r.json()


@mcp.tool()
async def enter_match(match_id: str, player_id: str):
    """Enter match"""

    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{BASE_URL}/enter/{match_id}",
            json={
                "player_id": player_id
            }
        )
        return r.json()


@mcp.tool()
async def logout_member():
    """Logout current member"""

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/logout/member")
        return r.json()

@mcp.tool()
async def login_store_manager(user_id: str, password: str):
    """Login as store manager"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/login/store-manager",
            json={
                "user_id": user_id,
                "password": password
            }
        )
        return r.json()

@mcp.tool()
async def logout_store_manager():
    """Logout current store manager"""

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/logout/store-manager")
        return r.json()

@mcp.tool()
async def use_ticket(ticket_id: str):
    """Use a ticket to enter a match"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/tickets/use",
            json={
                "ticket_id": ticket_id
            }
        )
        return r.json()


# -------------------------
# MATCH
# -------------------------

@mcp.tool()
async def get_matches():
    """Get all matches"""

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/matches")
        return r.json()



@mcp.tool()
async def get_match_players(match_id: str):
    """Get players and classes in match"""

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}/matches/{match_id}/players"
        )
        return r.json()

@mcp.tool()
async def login_player(user_id: str, password: str):
    """Login player"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/login/player",
            json={
                "user_id": user_id,
                "password": password
            }
        )
        return r.json()

@mcp.tool()
async def logout_player():
    """Logout player"""
    return {"message": "Player logged out successfully"}

# -------------------------
# PLAYER
# -------------------------

@mcp.tool()
async def select_player_class(match_id: str, player_id: str, player_class: str):
    """Select player class for a match"""

    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{BASE_URL}/players/select-class",
            json={
                "match_id": match_id,
                "player_id": player_id,
                "player_class": player_class
            }
        )
        return r.json()


@mcp.tool()
async def ready_player(match_id: str, player_id: str):
    """Player ready for match"""

    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{BASE_URL}/ready/{match_id}",
            json={
                "player_id": player_id
            }
        )
        return r.json()


# -------------------------
# SEATS / TICKETS
# -------------------------
#get seat in match
@mcp.tool()
async def get_match_seats(match_id: str):
    """Get seats of a match"""

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}/matches/{match_id}/seats"
        )
        return r.json()

#create seat order
@mcp.tool()
async def create_seat_order(match_id: str, seat_id: str):
    """Create seat booking order"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/orders/seat",
            json={
                "match_id": match_id,
                "seat_id": seat_id
            }
        )
        return r.json()

#pay seat
@mcp.tool()
async def pay_order(order_id: str, payment_type: str, coupon_id: str = ""):
    """Pay an order"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/orders/pay",
            json={
                "order_id": order_id,
                "payment_type": payment_type,
                "coupon_id": coupon_id
            }
        )
        return r.json()


#get ticket
@mcp.tool()
async def get_my_tickets():
    """Get my tickets"""

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/me/tickets")
        return r.json()


# -------------------------
# STORE ORDER
# -------------------------

#create product order
@mcp.tool()
async def create_store_order(match_id: str, product_ids: list[int], store_id: str):
    """Create store order"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/orders/store",
            json={
                "match_id": match_id,
                "product_ids": product_ids,
                "store_id": store_id
            }
        )
        return r.json()

#get store product
@mcp.tool()
async def get_store_products(store_id: str = "S001"):
    """Get store products"""

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}/store/products",
            params={"store_id": store_id}
        )
        return r.json()

#create product
@mcp.tool()
async def create_product(product_id: int, name: str, price: float, stock: int, store_id: str = "S001"):
    """Create store product"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/store/products",
            params={"store_id": store_id},
            json={
                "product_id": product_id,
                "name": name,
                "price": price,
                "stock": stock
            }
        )
        return r.json()

#add product stock
@mcp.tool()
async def add_stock(product_id: int, amount: int, store_id: str = "S001"):
    """Add product stock"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/store/products/{product_id}/stock",
            params={"store_id": store_id},
            json={
                "amount": amount
            }
        )
        return r.json()


# -------------------------
# DEMO TIME
# -------------------------

#get time
@mcp.tool()
async def get_demo_time():
    """Get demo time"""

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/demo-time")
        return r.json()

#set time
@mcp.tool()
async def set_demo_time(iso_datetime: str):
    """Set demo time"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/demo-time/set",
            json={
                "iso_datetime": iso_datetime
            }
        )
        return r.json()

#advance time
@mcp.tool()
async def advance_demo_time(minutes: int = 0, hours: int = 0):
    """Advance demo time"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/demo-time/advance",
            json={
                "minutes": minutes,
                "hours": hours
            }
        )
        return r.json()


@mcp.tool()
async def reset_demo_time():
    """Reset demo time"""

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/demo-time/reset")
        return r.json()


# -------------------------
# RUN MCP SERVER
# -------------------------

if __name__ == "__main__":
    mcp.run()