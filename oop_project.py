from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Tournament + Payment API", version="1.2.0")


# ======================================================
# ENUMS
# ======================================================
class SeatTier(str, Enum):
    REGULAR = "Regular"
    VIP = "VIP"


class MemberTier(str, Enum):
    REGULAR = "Regular"
    VIP = "VIP"


class OrderStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"


class TicketStatus(str, Enum):
    VALID = "Valid"
    USED = "Used"
    EXPIRED = "Expired"


class MatchStatus(str, Enum):
    NOT_START = "not start"
    ONGOING = "ongoing"
    FINISHED = "finished"


# ======================================================
# USER CLASSES
# ======================================================
class User:
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str, status: str = "active"):
        self.__id = user_id
        self.__name = name
        self.__phone_no = phone_no
        self.__email = email
        self.__password = password
        self.__is_login = False
        self.__status = status

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def get_email(self):
        return self.__email

    @property
    def get_status(self):
        return self.__status

    @property
    def is_login(self):
        return self.__is_login

    def login(self, passw: str) -> bool:
        if self.__password == passw:
            self.__is_login = True
            return True
        self.__is_login = False
        return False

    def logout(self):
        self.__is_login = False


class Member(User):
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str, tier: MemberTier):
        super().__init__(user_id, name, phone_no, email, password)
        self.__tier = tier
        self.__orders = []
        self.__ticket: List[Ticket] = []
        self.__receipt_list: List[Receipt] = []
        self.__coupon_list: List[Coupon] = []

    @property
    def tier(self):
        return self.__tier

    @property
    def orders(self):
        return self.__orders

    @property
    def tickets(self):
        return self.__ticket

    @property
    def receipts(self):
        return self.__receipt_list

    @property
    def coupons(self):
        return self.__coupon_list

    def add_order(self, order):
        self.__orders.append(order)

    def add_ticket(self, ticket: "Ticket"):
        self.__ticket.append(ticket)

    def add_receipt(self, receipt: "Receipt"):
        self.__receipt_list.append(receipt)

    def add_coupon(self, coupon: "Coupon"):
        self.__coupon_list.append(coupon)


class Player(User):
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str):
        super().__init__(user_id, name, phone_no, email, password)
        self.__match_to_play = []

    @property
    def match_to_play(self):
        return self.__match_to_play

    def add_match(self, match: "Match"):
        self.__match_to_play.append(match)

    def play(self):
        return f"Player {self.name} is ready to play"


# ======================================================
# SUPPORT CLASSES
# ======================================================
class Seat:
    def __init__(self, seat_id: str, seat_type: SeatTier, seat_price: float):
        self.__seat_id = seat_id
        self.__seat_type = seat_type
        self.__seat_price = seat_price
        self.__occupant: Optional[str] = None

    @property
    def seat_id(self):
        return self.__seat_id

    @property
    def seat_type(self):
        return self.__seat_type

    @property
    def seat_price(self):
        return self.__seat_price

    @property
    def occupant(self):
        return self.__occupant

    def assign_occupant(self, member_id: str):
        self.__occupant = member_id

    def clear_occupant(self):
        self.__occupant = None


class Match:
    def __init__(self, match_id: str, day: str, time: str, status: MatchStatus = MatchStatus.NOT_START):
        self.__match_id = match_id
        self.__status = status
        self.__day = day
        self.__time = time
        self.__player: List[Player] = []
        self.__booked_seat: List[Seat] = []

    @property
    def match_id(self):
        return self.__match_id

    @property
    def get_status(self):
        return self.__status.value

    @property
    def get_day(self):
        return self.__day

    @property
    def get_time(self):
        return self.__time

    @property
    def get_player(self):
        return self.__player

    @property
    def get_booked_seat(self):
        return self.__booked_seat

    def add_player(self, player: Player):
        self.__player.append(player)
        player.add_match(self)

    def add_booked(self, seat: Seat) -> bool:
        if seat not in self.__booked_seat:
            self.__booked_seat.append(seat)
            return True
        return False

    def remove_booked(self, seat: Seat):
        if seat in self.__booked_seat:
            self.__booked_seat.remove(seat)

    def check_login_status(self):
        return self.__status.value

    def set_status(self, status: MatchStatus):
        self.__status = status

    def start_datetime(self) -> datetime:
        return datetime.strptime(f"{self.__day} {self.__time}", "%Y-%m-%d %H:%M")


class BookedSeat:
    def __init__(self, seat: Seat, match: Match):
        self.__seat = seat
        self.__match = match

    @property
    def get_seat(self):
        return self.__seat

    @property
    def get_match(self):
        return self.__match


class Ticket:
    def __init__(self, ticket_id: str, booked_seat: BookedSeat):
        self.__ticket_id = ticket_id
        self.__bookedseat = booked_seat
        self.__day = booked_seat.get_match.get_day
        self.__time = booked_seat.get_match.get_time
        self.__status = TicketStatus.VALID

    @property
    def ticket_id(self):
        return self.__ticket_id

    @property
    def bookedseat(self):
        return self.__bookedseat

    @property
    def day(self):
        return self.__day

    @property
    def time(self):
        return self.__time

    @property
    def status(self):
        return self.__status.value

    def match_start_datetime(self) -> datetime:
        return self.__bookedseat.get_match.start_datetime()

    def is_enterable(self) -> bool:
        now = datetime.now()
        start = self.match_start_datetime()
        return (start - timedelta(hours=1)) <= now <= start and self.__status == TicketStatus.VALID

    def use_ticket(self):
        self.__status = TicketStatus.USED

    def expire_ticket(self):
        self.__status = TicketStatus.EXPIRED


class Coupon:
    def __init__(self, coupon_name: str, coupon_type: str, discount_rate: float):
        self.__coupon_name = coupon_name
        self.__coupon_type = coupon_type
        self.__discount_rate = discount_rate

    @property
    def coupon_name(self):
        return self.__coupon_name

    @property
    def get_coupon_type(self):
        return self.__coupon_type

    @property
    def get_discount_rate(self):
        return self.__discount_rate


class Receipt:
    def __init__(self, receipt_id: str, price: float, product: str):
        self.__receipt_id = receipt_id
        self.__price = price
        self.__product = product

    @property
    def receipt_id(self):
        return self.__receipt_id

    @property
    def price(self):
        return self.__price

    @property
    def product(self):
        return self.__product


# ======================================================
# PAYMENT CLASSES
# ======================================================
class PaymentMethod(ABC):
    def __init__(self, payment_channel: str, price: float, no_show_fee: float = 0):
        self._payment_channel = payment_channel
        self._price = price
        self._no_show_fee = no_show_fee

    @property
    def get_payment_channel(self):
        return self._payment_channel

    def calculate_price(self, discount_rate: float = 0):
        return round(self._price * (1 - discount_rate), 2)

    def calculate_no_show_fee(self):
        return self._no_show_fee

    def get_total(self, discount_rate: float = 0):
        return round(self.calculate_price(discount_rate) + self.calculate_no_show_fee(), 2)

    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass


class DebitCard(PaymentMethod):
    def __init__(self, price: float, no_show_fee: float, account: "CurrentAccount"):
        super().__init__("DebitCard", price, no_show_fee)
        self.__account = account

    def checkLimit(self, amount: float) -> bool:
        return self.__account.can_spend_today(amount)

    def pay(self, amount: float) -> bool:
        if not self.checkLimit(amount):
            return False
        return self.__account.withdraw(amount)


class Cash(PaymentMethod):
    def __init__(self, price: float, no_show_fee: float, order_reference: str):
        super().__init__("Cash", price, no_show_fee)
        self.__order_reference = order_reference

    def verify_order_reference(self) -> bool:
        return CounterService.validateOrderReference(self.__order_reference)

    def pay(self, amount: float) -> bool:
        return self.verify_order_reference()


class CurrentAccount:
    def __init__(self, account_id: str, balance: float, daily_limit: float):
        self.__accountId = account_id
        self.__balance = balance
        self.__daily_limit = daily_limit
        self.__used_today = 0.0
        self.__last_reset_date = datetime.now().date()

    @property
    def balance(self):
        return self.__balance

    @property
    def daily_limit(self):
        return self.__daily_limit

    @property
    def used_today(self):
        self._reset_if_new_day()
        return self.__used_today
    
    @property
    def account_id(self):
        return self.__accountId

    def _reset_if_new_day(self):
        today = datetime.now().date()
        if today != self.__last_reset_date:
            self.__used_today = 0.0
            self.__last_reset_date = today

    def can_spend_today(self, amount: float) -> bool:
        self._reset_if_new_day()
        return self.__used_today + amount <= self.__daily_limit

    def deposit(self, amount: float):
        self.__balance += amount

    def withdraw(self, amount: float) -> bool:
        self._reset_if_new_day()
        if amount > self.__balance:
            return False
        if self.__used_today + amount > self.__daily_limit:
            return False
        self.__balance -= amount
        self.__used_today += amount
        return True

class AccountManager:
    def __init__(self):
        self.__accounts: List[CurrentAccount] = []

    def add_account(self, account: CurrentAccount):
        self.__accounts.append(account)

    def get_account_by_id(self, account_id: str) -> Optional[CurrentAccount]:
        for acc in self.__accounts:
            if acc.account_id == account_id:
                return acc
        return None

class CounterService:
    @staticmethod
    def validateOrderReference(order_reference: str) -> bool:
        return isinstance(order_reference, str) and len(order_reference.strip()) > 0


# ======================================================
# STORE / PRODUCT / ORDERS
# ======================================================
class Product:
    def __init__(self, product_id: int, name: str, price: float, is_available: bool = True):
        self.__id = product_id
        self.__name = name
        self.__price = price
        self.__is_available = is_available

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def price(self):
        return self.__price

    @property
    def is_available(self):
        return self.__is_available


class Store:
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


class BaseOrder(ABC):
    def __init__(self, order_id: str):
        self._order_id = order_id
        self._status = OrderStatus.PENDING
        self._receipt: Optional[Receipt] = None
        self._created_at = datetime.now()
        self._paid_at: Optional[datetime] = None

    @property
    def order_id(self):
        return self._order_id

    @property
    def status(self):
        return self._status.value

    @property
    def created_at(self):
        return self._created_at

    @property
    def receipt(self):
        return self._receipt

    def cancel_order(self):
        self._status = OrderStatus.CANCELLED

    @abstractmethod
    def total_price(self):
        pass

    @abstractmethod
    def pay_order(self, payment_method: PaymentMethod, receipt_id: str, coupon: Optional[Coupon] = None):
        pass


class OrderProduct(BaseOrder):
    def __init__(self, order_id: str, member: Member, match: Match):
        super().__init__(order_id)
        self.__member = member
        self.__match = match
        self.__items: List[Product] = []

    def add_product(self, product: Product):
        if not product.is_available:
            raise ValueError("Product is not available")
        self.__items.append(product)

    @property
    def items(self):
        return self.__items

    @property
    def total_price(self):
        return sum(p.price for p in self.__items)

    @property
    def match(self):
        return self.__match

    def pay_order(self, payment_method: PaymentMethod, receipt_id: str, coupon: Optional[Coupon] = None):
        if self._status != OrderStatus.PENDING:
            raise ValueError("Order is not pending")
        if self.total_price <= 0:
            raise ValueError("Order has no product")

        discount_rate = coupon.get_discount_rate if coupon else 0
        payment_method._price = self.total_price
        total_amount = payment_method.get_total(discount_rate)

        if not payment_method.pay(total_amount):
            raise ValueError("Payment failed")

        item_names = ", ".join([p.name for p in self.__items])
        self._status = OrderStatus.PAID
        self._paid_at = datetime.now()
        self._receipt = Receipt(receipt_id, total_amount, f"Store Order / Match {self.__match.match_id} / {item_names}")
        return self._receipt


class OrderSeat(BaseOrder):
    BOOKING_HOLD_MINUTES = 30

    def __init__(self, order_id: str, booked_seat: BookedSeat):
        super().__init__(order_id)
        self.__booked_seat = booked_seat
        self.__ticket: Optional[Ticket] = None
        self.__no_show_paid = False

    @property
    def booked_seat(self):
        return self.__booked_seat

    @property
    def ticket(self):
        return self.__ticket

    @property
    def total_price(self):
        return self.__booked_seat.get_seat.seat_price

    def is_expired_hold(self) -> bool:
        if self._status != OrderStatus.PENDING:
            return False
        return datetime.now() > self._created_at + timedelta(minutes=self.BOOKING_HOLD_MINUTES)

    def auto_cancel_if_expired(self):
        if self.is_expired_hold():
            self.cancel_order()
            self.__booked_seat.get_match.remove_booked(self.__booked_seat.get_seat)
            return True
        return False

    def can_pay_no_show_fee(self) -> bool:
        return datetime.now() > self.__booked_seat.get_match.start_datetime()

    def pay_order(self, payment_method: PaymentMethod, receipt_id: str, coupon: Optional[Coupon] = None):
        if self.auto_cancel_if_expired():
            raise ValueError("Booking expired and has been cancelled")
        if self._status != OrderStatus.PENDING:
            raise ValueError("Order is not pending")

        discount_rate = coupon.get_discount_rate if coupon else 0
        total_amount = payment_method.get_total(discount_rate)
        is_paid = payment_method.pay(total_amount)

        if not is_paid:
            raise ValueError("Payment failed")

        self._status = OrderStatus.PAID
        self._paid_at = datetime.now()
        self.__ticket = Ticket(next_ticket_id(), self.__booked_seat)
        seat_name = self.__booked_seat.get_seat.seat_id
        match_name = self.__booked_seat.get_match.match_id
        self._receipt = Receipt(receipt_id, total_amount, f"Seat {seat_name} / Match {match_name}")
        return self.__ticket, self._receipt

    def pay_no_show_fee(self, payment_method: PaymentMethod, receipt_id: str):
        if self._status != OrderStatus.PAID:
            raise ValueError("Only paid seat order can pay no-show fee")
        if not self.can_pay_no_show_fee():
            raise ValueError("No-show fee can be paid only after match start/end")
        total_amount = payment_method.get_total(0)
        if not payment_method.pay(total_amount):
            raise ValueError("Payment failed")
        self.__no_show_paid = True
        return Receipt(receipt_id, total_amount, f"No-show fee / Order {self.order_id}")


# ======================================================
# TOURNAMENT / SERVER
# ======================================================
class Tournament:
    def __init__(self):
        self.__match_list: List[Match] = []
        self.__match_history = []
        self.__transaction_log = []
        self.__store: List[Store] = []
        self.__seat: List[Seat] = []

    def add_seat(self, seat: Seat):
        self.__seat.append(seat)

    def add_match(self, match: Match):
        self.__match_list.append(match)

    def add_store(self, store: Store):
        self.__store.append(store)

    @property
    def match_list(self):
        return self.__match_list

    @property
    def seat_list(self):
        return self.__seat

    @property
    def store_list(self):
        return self.__store

    def refresh_expired_bookings(self, member: Optional[Member] = None):
        if not member:
            return
        for order in member.orders:
            if isinstance(order, OrderSeat):
                order.auto_cancel_if_expired()

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        for match in self.__match_list:
            if match.match_id == match_id:
                return match
        return None

    def get_match(self, match_id: str) -> Optional[Match]:
        return self.get_match_by_id(match_id)

    def get_seat_by_id(self, seat_id: str) -> Optional[Seat]:
        for seat in self.__seat:
            if seat.seat_id == seat_id:
                return seat
        return None

    @property
    def search_available_match(self):
        available_match_list = []
        for search_match in self.__match_list:
            if search_match.get_status == "not start":
                for check_seat in self.__seat:
                    if check_seat not in search_match.get_booked_seat:
                        available_match_list.append(search_match)
                        break
        return available_match_list

    def search_match_available_by_day(self, day: str):
        match_day_list = []
        all_match_available = self.search_available_match
        for match in all_match_available:
            if match.get_day == day:
                match_day_list.append(match)
        return match_day_list

    def search_match_available_by_player_name(self, player_name: str):
        match_player_list = []
        all_match_available = self.search_available_match
        for search in all_match_available:
            player_names = [p.name.lower() for p in search.get_player]
            if player_name.lower() in player_names:
                match_player_list.append(search)
        return match_player_list

    def search_match_available_by_match(self, match_name: str):
        match_id_list = []
        all_match_available = self.search_available_match
        for match in all_match_available:
            if match_name.lower() in match.match_id.lower():
                match_id_list.append(match)
        return match_id_list

    def search_available_seat(self, match: Match):
        available_seat_list = []
        booked = match.get_booked_seat
        for seat in self.__seat:
            if seat not in booked:
                available_seat_list.append(seat)
        return available_seat_list

    def use_ticket(self, ticket: Ticket, member: Member):
        seat = ticket.bookedseat.get_seat
        if ticket.status == TicketStatus.USED.value:
            return False, "Ticket already used"
        if not ticket.is_enterable():
            if datetime.now() > ticket.match_start_datetime():
                ticket.expire_ticket()
            return False, "Ticket can be used only within 1 hour before match start"
        seat.assign_occupant(member.id)
        ticket.use_ticket()
        return True, "Enter success"


class Server:
    def __init__(self):
        self.__user: List[User] = []
        self.__tournament: List[Tournament] = []
        self.__current_user: Optional[Member] = None

    def add_user(self, user: User):
        self.__user.append(user)

    def add_tournament(self, tournament: Tournament):
        self.__tournament.append(tournament)

    def get_user_by_id(self, user_id: str):
        for user in self.__user:
            if user.id == user_id:
                return user
        return None

    def login(self, user_id: str, password: str):
        user = self.get_user_by_id(user_id)
        if user and user.login(password):
            self.__current_user = user
            return user
        return None

    def logout(self):
        if self.__current_user:
            self.__current_user.logout()
        self.__current_user = None

    def get_tournament(self):
        return self.__tournament[0] if self.__tournament else None

    @property
    def current_user(self):
        return self.__current_user

    @property
    def tournament(self):
        return self.get_tournament()


# ======================================================
# SYSTEM SETUP
# ======================================================
server = Server()
championship = Tournament()
server.add_tournament(championship)

# seats
championship.add_seat(Seat("R1", SeatTier.REGULAR, 100))
championship.add_seat(Seat("R2", SeatTier.REGULAR, 100))
championship.add_seat(Seat("V1", SeatTier.VIP, 500))
championship.add_seat(Seat("V2", SeatTier.VIP, 500))

# matches (set future dates for easy testing)
m1 = Match("M1", "2026-12-08", "18:00")
m2 = Match("M2", "2026-12-09", "20:00")

# players
player1 = Player("P1", "Alpha", "0811111111", "alpha@mail.com", "1111")
player2 = Player("P2", "Bravo", "0822222222", "bravo@mail.com", "2222")

m1.add_player(player1)
m1.add_player(player2)
m2.add_player(player2)

championship.add_match(m1)
championship.add_match(m2)

# members
member1 = Member("U1", "Pange", "0999999999", "pange@mail.com", "1234", MemberTier.VIP)
member2 = Member("U2", "Ark", "0888888888", "ark@mail.com", "5678", MemberTier.REGULAR)
server.add_user(member1)
server.add_user(member2)

member1.add_coupon(Coupon("VIP10", "percent", 0.10))

# accounts with daily limit stored in account/database style
account_manager = AccountManager()

account_manager.add_account(CurrentAccount("U1", 5000, 3000))
account_manager.add_account(CurrentAccount("U2", 1800, 1000))

# store
store = Store()
store.add_product(Product(1, "Water", 20))
store.add_product(Product(2, "Popcorn", 50))
store.add_product(Product(3, "Team Jersey", 1200))
championship.add_store(store)

ORDER_COUNTER = 1
RECEIPT_COUNTER = 1
PRODUCT_ORDER_COUNTER = 1


def next_order_id():
    global ORDER_COUNTER
    oid = f"O{ORDER_COUNTER}"
    ORDER_COUNTER += 1
    return oid


def next_ticket_id():
    global ORDER_COUNTER
    tid = f"T{ORDER_COUNTER}"
    return tid


def next_receipt_id():
    global RECEIPT_COUNTER
    rid = f"R{RECEIPT_COUNTER}"
    RECEIPT_COUNTER += 1
    return rid


def next_product_order_id():
    global PRODUCT_ORDER_COUNTER
    oid = f"PO{PRODUCT_ORDER_COUNTER}"
    PRODUCT_ORDER_COUNTER += 1
    return oid


# ======================================================
# API SCHEMAS
# ======================================================
class LoginRequest(BaseModel):
    user_id: str
    password: str


class BookSeatRequest(BaseModel):
    match_id: str
    seat_id: str


class CreateProductOrderRequest(BaseModel):
    match_id: str
    product_ids: List[int]


class PayOrderRequest(BaseModel):
    order_id: str
    payment_type: str  # debit_card | cash
    coupon_name: Optional[str] = None
    no_show_fee: float = 0


class ProductSchema(BaseModel):
    id: int
    name: str
    price: float


# ======================================================
# HELPERS
# ======================================================
def get_logged_in_member() -> Member:
    user = server.current_user
    if not user or not isinstance(user, Member):
        raise HTTPException(status_code=401, detail="Please login as member first")
    championship.refresh_expired_bookings(user)
    return user


def build_payment(payment_type: str, price: float, member_id: str, no_show_fee: float, order_id: str) -> PaymentMethod:
    if payment_type == "debit_card":
        account = account_manager.get_account_by_id(member_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return DebitCard(price, no_show_fee, account)
    
    if payment_type == "cash":
        return Cash(price, no_show_fee, order_id)
    raise HTTPException(status_code=400, detail="payment_type must be debit_card or cash")


def find_coupon(user: Member, coupon_name: Optional[str]) -> Optional[Coupon]:
    if not coupon_name:
        return None
    for c in user.coupons:
        if c.coupon_name == coupon_name:
            return c
    return None


def find_user_order_by_id(user: Member, order_id: str):
    for order in user.orders:
        if hasattr(order, "order_id") and order.order_id == order_id:
            return order
    return None


# ======================================================
# API ROUTES
# ======================================================
@app.get("/")
def root():
    return {"message": "Tournament + Payment API running"}


@app.post("/login")
def login(req: LoginRequest):
    user = server.login(req.user_id, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user_id or password")
    return {"message": f"Logged in as {user.name}", "user_id": user.id}


@app.post("/logout")
def logout():
    server.logout()
    return {"message": "Logged out successfully"}


@app.get("/matches/available")
def get_available_matches():
    matches = championship.search_available_match
    return [
        {
            "match_id": m.match_id,
            "day": m.get_day,
            "time": m.get_time,
            "status": m.get_status,
            "players": [p.name for p in m.get_player],
        }
        for m in matches
    ]


@app.get("/matches/search/day/{day}")
def search_matches_by_day(day: str):
    matches = championship.search_match_available_by_day(day)
    return [
        {
            "match_id": m.match_id,
            "day": m.get_day,
            "time": m.get_time,
            "status": m.get_status,
            "players": [p.name for p in m.get_player],
        }
        for m in matches
    ]


@app.get("/matches/search/player/{player_name}")
def search_matches_by_player_name(player_name: str):
    matches = championship.search_match_available_by_player_name(player_name)
    return [
        {
            "match_id": m.match_id,
            "day": m.get_day,
            "time": m.get_time,
            "status": m.get_status,
            "players": [p.name for p in m.get_player],
        }
        for m in matches
    ]


@app.get("/matches/search/match/{match_id}")
def search_matches_by_match_name(match_name: str):
    matches = championship.search_match_available_by_match(match_name)
    return [
        {
            "match_id": m.match_id,
            "day": m.get_day,
            "time": m.get_time,
            "status": m.get_status,
            "players": [p.name for p in m.get_player],
        }
        for m in matches
    ]


@app.get("/matches/{match_id}/available-seats")
def get_available_seats(match_id: str):
    user = server.current_user
    if user and isinstance(user, Member):
        championship.refresh_expired_bookings(user)

    match = championship.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    seats = championship.search_available_seat(match)
    return [
        {
            "seat_id": s.seat_id,
            "seat_type": s.seat_type.value,
            "seat_price": s.seat_price,
            "occupant": s.occupant,
        }
        for s in seats
    ]


@app.post("/orders/seat")
def create_order_seat(req: BookSeatRequest):
    user = get_logged_in_member()

    match = championship.get_match_by_id(req.match_id)
    seat = championship.get_seat_by_id(req.seat_id)

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    if seat in match.get_booked_seat:
        raise HTTPException(status_code=400, detail="Seat already booked")

    match.add_booked(seat)
    booked_seat = BookedSeat(seat, match)
    order = OrderSeat(next_order_id(), booked_seat)
    user.add_order(order)

    return {
        "message": "Seat booked successfully",
        "order_id": order.order_id,
        "seat_id": seat.seat_id,
        "match_id": match.match_id,
        "price": seat.seat_price,
        "status": order.status,
        "booking_expire_at": (order.created_at + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/store/products", response_model=List[ProductSchema], tags=["Store"])
def get_products():
    return [ProductSchema(id=p.id, name=p.name, price=p.price) for p in store.get_products()]


@app.post("/orders/store", tags=["Store"])
def create_store_order(req: CreateProductOrderRequest):
    user = get_logged_in_member()
    match = server.get_tournament().get_match(req.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    order = OrderProduct(next_product_order_id(), user, match)
    for pid in req.product_ids:
        product = store.get_product(pid)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        order.add_product(product)

    user.add_order(order)
    return {
        "message": "Product order created",
        "order_id": order.order_id,
        "match_id": match.match_id,
        "items": [{"id": p.id, "name": p.name, "price": p.price} for p in order.items],
        "total_price": order.total_price,
        "status": order.status,
    }


@app.post("/orders/pay")
def pay_any_order(req: PayOrderRequest):
    user = get_logged_in_member()
    order = find_user_order_by_id(user, req.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    coupon = find_coupon(user, req.coupon_name)

    if isinstance(order, OrderSeat):
        payment = build_payment(req.payment_type, order.total_price, user.id, 0, req.order_id)
        try:
            ticket, receipt = order.pay_order(payment, next_receipt_id(), coupon)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        user.add_ticket(ticket)
        user.add_receipt(receipt)
        return {
            "message": "Seat payment success",
            "order_type": "seat",
            "order_id": order.order_id,
            "ticket_id": ticket.ticket_id,
            "receipt_id": receipt.receipt_id,
            "seat_id": ticket.bookedseat.get_seat.seat_id,
            "match_id": ticket.bookedseat.get_match.match_id,
            "total_price": receipt.price,
            "product": receipt.product,
            "ticket_status": ticket.status,
            "account_balance": account_manager.get_account_by_id(user.id).balance if req.payment_type == "debit_card" else None,
            "daily_limit": account_manager.get_account_by_id(user.id).daily_limit if req.payment_type == "debit_card" else None,
            "used_today": account_manager.get_account_by_id(user.id).used_today if req.payment_type == "debit_card" else None,
        }

    if isinstance(order, OrderProduct):
        payment = build_payment(req.payment_type, order.total_price, user.id, 0, req.order_id)
        try:
            receipt = order.pay_order(payment, next_receipt_id(), coupon)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        user.add_receipt(receipt)
        return {
            "message": "Product payment success",
            "order_type": "product",
            "order_id": order.order_id,
            "receipt_id": receipt.receipt_id,
            "match_id": order.match.match_id,
            "items": [{"id": p.id, "name": p.name, "price": p.price} for p in order.items],
            "total_price": receipt.price,
            "product": receipt.product,
            "account_balance": account_manager.get_account_by_id(user.id).balance if req.payment_type == "debit_card" else None,
            "daily_limit": account_manager.get_account_by_id(user.id).daily_limit if req.payment_type == "debit_card" else None,
            "used_today": account_manager.get_account_by_id(user.id).used_today if req.payment_type == "debit_card" else None,
        }

    raise HTTPException(status_code=400, detail="Unsupported order type")


@app.post("/orders/{order_id}/no-show-fee")
def pay_no_show_fee(order_id: str, req: PayOrderRequest):
    user = get_logged_in_member()
    order = find_user_order_by_id(user, order_id)
    if not order or not isinstance(order, OrderSeat):
        raise HTTPException(status_code=404, detail="Seat order not found")
    if req.no_show_fee <= 0:
        raise HTTPException(status_code=400, detail="no_show_fee must be greater than 0")

    payment = build_payment(req.payment_type, 0, user.id, req.no_show_fee, order_id)
    try:
        receipt = order.pay_no_show_fee(payment, next_receipt_id())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user.add_receipt(receipt)
    return {
        "message": "No-show fee paid successfully",
        "order_id": order.order_id,
        "receipt_id": receipt.receipt_id,
        "total_price": receipt.price,
        "product": receipt.product,
        "account_balance": account_manager.get_account_by_id(user.id).balance if req.payment_type == "debit_card" else None,
    }


@app.get("/me/orders")
def get_my_orders():
    user = get_logged_in_member()
    result = []
    for o in user.orders:
        if isinstance(o, OrderSeat):
            result.append({
                "order_type": "seat",
                "order_id": o.order_id,
                "seat_id": o.booked_seat.get_seat.seat_id,
                "match_id": o.booked_seat.get_match.match_id,
                "price": o.total_price,
                "status": o.status,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "expires_at": (o.created_at + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            })
        elif isinstance(o, OrderProduct):
            result.append({
                "order_type": "product",
                "order_id": o.order_id,
                "match_id": o.match.match_id,
                "items": [{"id": p.id, "name": p.name, "price": p.price} for p in o.items],
                "price": o.total_price,
                "status": o.status,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
    return result


@app.get("/me/tickets")
def get_my_tickets():
    user = get_logged_in_member()
    return [
        {
            "ticket_id": t.ticket_id,
            "seat_id": t.bookedseat.get_seat.seat_id,
            "match_id": t.bookedseat.get_match.match_id,
            "day": t.day,
            "time": t.time,
            "status": t.status,
            "usable_from": (t.match_start_datetime() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "usable_until": t.match_start_datetime().strftime("%Y-%m-%d %H:%M:%S"),
        }
        for t in user.tickets
    ]


@app.get("/me/receipts")
def get_my_receipts():
    user = get_logged_in_member()
    return [{"receipt_id": r.receipt_id, "price": r.price, "product": r.product} for r in user.receipts]


@app.put("/enter/{ticket_id}")
def enter_match(ticket_id: str):
    user = get_logged_in_member()

    target_ticket = None
    for ticket in user.tickets:
        if ticket.ticket_id == ticket_id:
            target_ticket = ticket
            break

    if not target_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ok, message = championship.use_ticket(target_ticket, user)
    if not ok:
        raise HTTPException(status_code=400, detail=message)

    return {
        "message": message,
        "ticket_id": target_ticket.ticket_id,
        "seat_id": target_ticket.bookedseat.get_seat.seat_id,
        "seat_occupant": target_ticket.bookedseat.get_seat.occupant,
        "ticket_status": target_ticket.status,
    }


if __name__ == "__main__":
    uvicorn.run("combined_tournament_payment_api:app", host="127.0.0.1", port=8000, reload=True)
