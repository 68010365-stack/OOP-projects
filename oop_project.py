# Comments
# ปัง: ถ้าตรงไหนมันเข้าใจยากว่ามันคืออะไรฝาก comment ไว้ด้วย และก็แนะนำให้มีชื่อติดไว้ด้วย ถ้าไม่เข้าใจจะได้ถามถูกคน
# ปัง: ใครเปลี่ยนไรเยอะๆ สร้าง branch ใหม่ด้วย ถ้าเป็นไปได้บอกในไลน์ด้วย คนอื่นจะได้รู้
# ปัง: อย่าลืมดู branch github ด้วย | อย่า commit ผิด
# ปัง: ถ้าติดไรถามกันในไลน์

# Imports
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Actor Class
class User():
    def __init__(self, id, name, phone, email):
        self.__id = id
        self.__name = name
        self.__phone = phone
        self.__email = email
        self.__status = None

    @property
    def username(self): 
        return self.__id

    @property
    def get_email(self):
        return self.__email

    @property
    def get_status(self):
        return self.__status


class Member(User):
    def __init__(self, id, name, phone=None, email=None):
        super().__init__(id, name, phone, email)
        self.__tickets = []
        self.__order = []

    @property
    def tickets(self): return self.__tickets
    
    @property
    def orders(self):
        return self.__order
    
    def add_ticket(self, ticket):
        self.__tickets.append(ticket)

    def add_order(self, order):
        self.__order.append(order)    


class Player(User):
    pass



# Main Class

class Server():
    def __init__(self):
        self.__users: List[User] = []
        self.__tournaments: List[Tournament] = []
        self.__current_user: Optional[Member] = None

    def add_user(self, user: User):
        self.__users.append(user)

    def add_tournament(self, tournament: Tournament):
        self.__tournaments.append(tournament)

    def get_tournament(self) -> Tournament:
        return self.__tournaments[0]

    def find_user(self, username: str) -> Optional[Member]:
        return next((u for u in self.__users if u.username == username), None)

    def login(self, username: str) -> Optional[Member]:
        user = self.find_user(username)

        if isinstance(user, Member):
            self.__current_user = user
            return user

        return None

    def enter_match(self, user: Member, match_id: int, seat_id: str):
        tournament = self.__tournaments[0]
        return tournament.use_ticket(user, match_id, seat_id)

    @property
    def current_user(self) -> Optional[Member]:
        return self.__current_user

class Tournament():
    def __init__(self):
        self.__match_list = []
        self.__physical_seats = []

    def add_seat(self, seat: Seat):

        if any(s.id == seat.id for s in self.__physical_seats):
            raise ValueError("Seat already exists")

        self.__physical_seats.append(seat)

    def add_match(self, match: Match):

        if any(m.match_id == match.match_id for m in self.__match_list):
            raise ValueError("Match already exists")

        self.__match_list.append(match)

    def get_match(self, match_id: int) -> Optional[Match]:
        return next((m for m in self.__match_list if m.match_id == match_id), None)

    # ปัง: ใช้ ticket ของ Member ทำให้ ticket เปลี่ยนสถานะเป็น 'Used'| เปลี่ยนที่นั่งให้ว่า ตอนนี้ ณ matchนี้ มีคนนั่ง seat นี้แล้ว(เก็บใน match แบบ list)
    def use_ticket(self, user: Member, match_id: int, seat_id: str): 
        target_match = next((m for m in self.__match_list if m.match_id == match_id), None)
        if not target_match: return "Error: Match not found"
        
        physical_seat = next((s for s in self.__physical_seats if s.id == seat_id), None)
        if not physical_seat: return "Error: Physical seat does not exist"

        user_ticket = next((t for t in user.tickets if t.match_id == match_id and t.seat_id == seat_id), None)
        if not user_ticket: return "Error: You do not have a ticket for this seat"
        if user_ticket.status == "Used": return "Error: Ticket already used"
        if target_match.is_occupied(seat_id): return "Error: Seat already occupied"
        
        target_match.assign_seat(physical_seat, user)
        user_ticket.status = "Used"
        return "Enter Success"


class Match():
    def __init__(self, match_id: int):
        self.__match_id = match_id
        self.__occupancy_records = [] 

    @property
    def match_id(self): return self.__match_id

    def is_occupied(self, seat_id: str) -> bool:
        return any(rec.seat.id == seat_id for rec in self.__occupancy_records)

    def assign_seat(self, seat: Seat, member: Member):
        self.__occupancy_records.append(Occupation(seat, member))


class Seat():
    def __init__(self, id: str):
        self.__tier = None
        self.__id = id 

    @property
    def id(self):
        return self.__id
    
class OrderSeat():
    pass

class OrderProduct():

    def __init__(self, order_id: int, member: Member, match: Match):
        self.__order_id = order_id
        self.__member = member
        self.__match = match
        self.__items: List[Product] = []

    def add_product(self, product: Product):
        self.__items.append(product)

    @property
    def items(self):
        return self.__items

    @property
    def total_price(self):
        return sum(p.price for p in self.__items)

    @property
    def order_id(self):
        return self.__order_id



# Payment Process

class Payment():
    pass


class Debitcard(Payment):
    pass


class Cash(Payment):
    pass


class CurrentAccount():
    pass


class CounterService():
    pass


class Coupon():
    pass



#Support class
class BookedSeat():
    def __init__(self, match: Match, seat: Seat):
        self.__match = match
        self.__seat = seat

    @property
    def match_id(self): 
        return self.__match.match_id
    
    @property
    def seat_id(self): 
        return self.__seat.id


#ปัง: เพิ่มเพื่อการเก็บให้รู้ว่าใครนั่งไหนใน match นั้นแล้ว
class Occupation:
    def __init__(self, seat: Seat, member: Member):
        self.seat = seat
        self.member = member


class Store():
    def __init__(self):
        self.__products: List[Product] = []

    def add_product(self, product: Product):

        if any(p.id == product.id for p in self.__products):
            raise ValueError("Product already exists")

        self.__products.append(product)

    def get_products(self):
        return self.__products

    def get_product(self, product_id: int) -> Optional[Product]:
        return next((p for p in self.__products if p.id == product_id), None)


class Product():
    def __init__(self, id: int, name: str, price: float):
        self.__id = id
        self.__name = name
        self.__price = price

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def price(self):
        return self.__price


class Receipt():
    pass


class Ticket():
    def __init__(self, ticket_id: int, booked_seat: BookedSeat):
        self.__ticket_id = ticket_id
        self.__booked_seat = booked_seat
        self.status = "Valid"

    @property
    def ticket_id(self):
        return self.__ticket_id
    
    @property
    def match_id(self): 
        return self.__booked_seat.match_id
    
    @property
    def seat_id(self): 
        return self.__booked_seat.seat_id



# System Setup| ปัง: อันนี้ผมใส่ไปก่อนถ้ามีใครจะแก้ก็ได้เลย

server = Server()
Championship = Tournament()
server.add_tournament(Championship)


user1 = Member("pange_123", "Pange")
user2 = Member("ark_456", "Ark")
server.add_user(user1)
server.add_user(user2)


s1 = Seat("a01")
Championship.add_seat(s1)
m1 = Match(1)
Championship.add_match(m1)

Pange_ticket = Ticket(1001, BookedSeat(m1, s1))
user1.add_ticket(Pange_ticket)

store = Store()

store.add_product(Product(1, "Water", 20))
store.add_product(Product(2, "Popcorn", 50))
store.add_product(Product(3, "Team Jersey", 1200))


# schematics
class LoginRequest(BaseModel): # ปัง: ใครที่ทำเกี่ยวกับ user login แก้ได้เลย
    username: str

class TicketSchema(BaseModel):
    ticket_id: int
    seat_id: str
    match_id: int
    status: str
    class Config: from_attributes = True

class ProductSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    order_id: int
    total_price: float

    class Config:
        from_attributes = True

class BuyRequest(BaseModel):
    product_ids: List[int]
    match_id: int



# api/mcp

# ปัง: อันนี้สำหรับ log in ใครที่ทำเกี่ยวกับ user login แก้ได้เลย
@app.post("/login", tags=["Auth"])
async def login(req: LoginRequest):

    user = server.login(req.username)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"message": f"Logged in as {user.username}"}

# ปัง: ใช้ดูว่ามี ticket ไรบ้าง
@app.get("/me/tickets", response_model=List[TicketSchema], tags=["Member"])
async def get_my_tickets():
    user = server.current_user
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    if not isinstance(user, Member):
        raise HTTPException(status_code=403, detail="Not a member")

    return user.tickets

# ปัง: เข้าชม match
@app.put("/enter/{match_id}/{seat_id}", tags=["Tournament"])
async def enter_seat(match_id: int, seat_id: str):

    user = server.current_user
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")
    if not isinstance(user, Member):
        raise HTTPException(status_code=403, detail="Not a member")

    result = server.enter_match(user, match_id, seat_id)

    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)

    return {"message": result}

#ปัง: เกี่ยวกับ store/product
@app.get("/store/products", response_model=List[ProductSchema], tags=["Store"])
async def get_products():
    return store.get_products()

@app.post("/store/buy", tags=["Store"])
async def buy_products(req: BuyRequest):

    user = server.current_user
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")

    tournament = server.get_tournament()
    match = tournament.get_match(req.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    order = OrderProduct(len(user.orders) + 1, user, match)

    for pid in req.product_ids:

        product = store.get_product(pid)

        if not product:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")

        order.add_product(product)

    user.add_order(order)

    return {
        "message": "Order successful",
        "total_price": order.total_price
    }

@app.get("/me/orders", response_model=List[OrderSchema], tags=["Member"])
async def get_my_orders():

    user = server.current_user
    if not user:
        raise HTTPException(status_code=401, detail="Please login first")

    return user.orders

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
