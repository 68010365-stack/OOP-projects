# Comments
# ปัง: ถ้าตรงไหนมันเข้าใจยากว่ามันคืออะไรฝาก comment ไว้ด้วย และก็แนะนำให้มีชื่อติดไว้ด้วย ถ้าไม่เข้าใจจะได้ถามถูกคน
# ปัง: ถ้าติดไรถามกันในไลน์
# ปัง: อย่าลืมดู branch github ด้วย | อย่า commit ผิด


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
        return self.__name

    @property
    def get_email():
        pass

    @property
    def get_status():
        pass


class Member(User):
    def __init__(self):
        self.__tickets = []
        self.__order = []

    @property
    def tickets(self): return self.__tickets

    def add_ticket(self, ticket):
        self.__tickets.append(ticket)


class Player(User):
    pass



# Main Class

class Server():
    pass


class Tournament():
    def __init__(self):
        self.__match_list = []
        self.__physical_seats = []
        self.__members = []

    def add_member(self, member: Member):
        self.__members.append(member)

    def get_member(self, username: str) -> Optional[Member]:
        return next((m for m in self.__members if m.username == username), None)

    def add_seat(self, seat: Seat): 
        self.__physical_seats.append(seat)

    def add_match(self, match: Match): 
        self.__match_list.append(match)

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
        self.id = id 

class OrderSeat():
    pass

class OrderProduct():
    pass



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
    pass


class Product():
    pass


class reciept():
    pass


class Ticket():
    def __init__(self, ticket_id: int, booked_seat: BookedSeat):
        self.ticket_id = ticket_id
        self.__booked_seat = booked_seat
        self.status = "Valid"

    @property
    def match_id(self): 
        return self.__booked_seat.match_id
    
    @property
    def seat_id(self): 
        return self.__booked_seat.seat_id



# System Setup| ปัง: อันนี้ผมใส่ไปก่อนถ้ามีใครจะแก้ก็ได้เลย

Championship = Tournament()

user1 = Member("pange_123", "Pange")
user2 = Member("ark_456", "Ark")
Championship.add_member(user1)
Championship.add_member(user2)

s1 = Seat("a01")
Championship.add_seat(s1)
m1 = Match(1)
Championship.add_match(m1)

Pange_ticket = Ticket(1001, BookedSeat(m1, s1))
user1.add_ticket(Pange_ticket)

current_logged_in_user: Optional[Member] = None # ปัง: ใครที่ทำเกี่ยวกับ user login แก้ได้เลย



# schematics
class LoginRequest(BaseModel): # ปัง: ใครที่ทำเกี่ยวกับ user login แก้ได้เลย
    username: str

class TicketSchema(BaseModel):
    ticket_id: int
    seat_id: str
    match_id: int
    status: str
    class Config: from_attributes = True



# api/mcp

# ปัง: อันนี้สำหรับ log in ใครที่ทำเกี่ยวกับ user login แก้ได้เลย
@app.post("/login", tags=["Auth"])
async def login(req: LoginRequest):
    global current_logged_in_user
    user = Championship.get_member(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    current_logged_in_user = user
    return {"message": f"Logged in as {user.username}"}

# ปัง: ใช้ดูว่ามี ticket ไรบ้าง
@app.get("/me/tickets", response_model=List[TicketSchema], tags=["Member"])
async def get_my_tickets():
    if not current_logged_in_user:
        raise HTTPException(status_code=401, detail="Please login first")
    return current_logged_in_user.tickets

# ปัง: เข้าชม match
@app.put("/enter/{match_id}/{seat_id}", tags=["Tournament"])
async def enter_seat(match_id: int, seat_id: str):
    if not current_logged_in_user:
        raise HTTPException(status_code=401, detail="Please login first")
    
    result = Championship.use_ticket(current_logged_in_user, match_id, seat_id)
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"message": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)