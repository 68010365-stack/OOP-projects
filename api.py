from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


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
    NOT_START = "Not Start"
    ONGOING = "Ongoing"
    FINISHED = "Finished"


class PlayerClass(str, Enum):
    TANK = "Tank"
    FIGHTER = "Fighter"
    ASSASSIN = "Assassin"
    MAGE = "Mage"
    SUPPORT = "Support"


class DemoTimeManager:
    def __init__(self):
        self.__demo_time: Optional[datetime] = None

    def now(self) -> datetime:
        if self.__demo_time is None:
            return datetime.now()
        return self.__demo_time

    def set_time(self, new_time: datetime) -> None:
        self.__demo_time = new_time

    def advance_minutes(self, minutes: int) -> None:
        self.set_time(self.now() + timedelta(minutes=minutes))

    def advance_hours(self, hours: int) -> None:
        self.set_time(self.now() + timedelta(hours=hours))

    def reset(self) -> None:
        self.__demo_time = None


class User:
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str):
        self.__user_id = user_id
        self.__name = name
        self.__phone_no = phone_no
        self.__email = email
        self.__password = password
        self.__is_login = False
    def get_password(self) -> str:
        return self.__password

    def get_user_id(self) -> str:
        return self.__user_id

    def get_name(self) -> str:
        return self.__name

    def get_phone_no(self) -> str:
        return self.__phone_no

    def get_email(self) -> str:
        return self.__email

    def is_login(self) -> bool:
        return self.__is_login

    def login(self, password: str) -> bool:
        if self.__password == password:
            self.__is_login = True
            return True
        return False

    def logout(self) -> None:
        self.__is_login = False


class Coupon:
    def __init__(self, coupon_id: str, coupon_name: str, discount_rate: float, owner_id: str):
        self.__coupon_id = coupon_id
        self.__coupon_name = coupon_name
        self.__discount_rate = discount_rate
        self.__owner_id = owner_id
        self.__is_used = False

    def get_coupon_id(self) -> str:
        return self.__coupon_id

    def get_coupon_name(self) -> str:
        return self.__coupon_name

    def get_discount_rate(self) -> float:
        return self.__discount_rate

    def get_owner_id(self) -> str:
        return self.__owner_id

    def is_used(self) -> bool:
        return self.__is_used

    def mark_used(self) -> None:
        self.__is_used = True

    def can_use_by(self, member_id: str) -> bool:
        return self.__owner_id == member_id and not self.__is_used


class Receipt:
    def __init__(self, receipt_id: str, order_id: str, amount: float, description: str, paid_at: datetime):
        self.__receipt_id = receipt_id
        self.__order_id = order_id
        self.__amount = amount
        self.__description = description
        self.__paid_at = paid_at

    def get_receipt_id(self) -> str:
        return self.__receipt_id

    def get_order_id(self) -> str:
        return self.__order_id

    def get_amount(self) -> float:
        return self.__amount

    def get_description(self) -> str:
        return self.__description

    def get_paid_at(self) -> datetime:
        return self.__paid_at

class StoreManager(User):
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str):
        super().__init__(user_id, name, phone_no, email, password)

class Member(User):
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str, tier: MemberTier):
        super().__init__(user_id, name, phone_no, email, password)
        self.__tier = tier
        self.__orders: List[BaseOrder] = []
        self.__tickets: List[Ticket] = []
        self.__receipts: List[Receipt] = []
        self.__coupons: List[Coupon] = []
        self.__card_list = []

    def get_tier(self) -> MemberTier:
        return self.__tier

    def get_cards(self):
        for e in self.__card_list:
            return e

    def get_orders(self) -> List[BaseOrder]:
        return self.__orders

    def get_tickets(self) -> List[Ticket]:
        return self.__tickets

    def get_receipts(self) -> List[Receipt]:
        return self.__receipts

    def get_coupons(self) -> List[Coupon]:
        return self.__coupons

    def add_card(self, card):
        self.__card_list.append(card)

    def add_order(self, order: BaseOrder) -> None:
        self.__orders.append(order)

    def add_ticket(self, ticket: Ticket) -> None:
        self.__tickets.append(ticket)

    def add_receipt(self, receipt: Receipt) -> None:
        self.__receipts.append(receipt)

    def add_coupon(self, coupon: Coupon) -> None:
        self.__coupons.append(coupon)

    def find_coupon(self, coupon_id: str) -> Optional[Coupon]:
        for coupon in self.__coupons:
            if coupon.get_coupon_id() == coupon_id:
                return coupon
        return None

    def owns_coupon(self, coupon_id: str) -> bool:
        coupon = self.find_coupon(coupon_id)
        if coupon is None:
            return False
        return coupon.can_use_by(self.get_user_id())


class Player(User):
    def __init__(self, user_id: str, name: str, phone_no: str, email: str, password: str):
        super().__init__(user_id, name, phone_no, email, password)
        self.__current_match = None
        self.__class_name = None
        self.__ready = False
        self.__match_to_play: List[Match] = []

    def add_match(self, match: Match) -> None:
        if not self.has_match(match.get_match_id()):
            self.__match_to_play.append(match)

    def has_match(self, match_id: str) -> bool:
        for match in self.__match_to_play:
            if match.get_match_id() == match_id:
                return True
        return False

    def get_match_to_play(self) -> List[Match]:
        return self.__match_to_play


class Account:
    def __init__(self, account_id: str, owner_name: str, balance: float, daily_limit: float):
        self.__account_id = account_id
        self.__owner_name = owner_name
        self.__balance = balance
        self.__daily_limit = daily_limit
        self.__used_today = 0.0
        self.__last_used_date = datetime.now().date()

    def __reset_if_new_day(self) -> None:
        today = datetime.now().date()
        if self.__last_used_date != today:
            self.__used_today = 0.0
            self.__last_used_date = today

    def get_account_id(self) -> str:
        return self.__account_id

    def get_owner_name(self) -> str:
        return self.__owner_name

    def get_balance(self) -> float:
        return self.__balance

    def get_daily_limit(self) -> float:
        return self.__daily_limit

    def get_used_today(self) -> float:
        self.__reset_if_new_day()
        return self.__used_today

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.__balance += amount

    def can_withdraw(self, amount: float) -> bool:
        self.__reset_if_new_day()
        if amount <= 0:
            return False
        if self.__balance < amount:
            return False
        if self.__used_today + amount > self.__daily_limit:
            return False
        return True

    def withdraw(self, amount: float) -> bool:
        if not self.can_withdraw(amount):
            return False
        self.__balance -= amount
        self.__used_today += amount
        return True


class PaymentMethod(ABC):
    def __init__(self, payment_channel: str):
        self.__payment_channel = payment_channel

    def get_payment_channel(self) -> str:
        return self.__payment_channel

    @abstractmethod
    def pay(self, amount: float) -> bool:
        raise NotImplementedError


class Card(PaymentMethod, ABC):
    def __init__(self, payment_channel: str, card_number: str, holder_name: str, expired_month: int, expired_year: int):
        super().__init__(payment_channel)
        self.__card_number = card_number
        self.__holder_name = holder_name
        self.__expired_month = expired_month
        self.__expired_year = expired_year

    def get_card_number(self) -> str:
        return self.__card_number

    def get_holder_name(self) -> str:
        return self.__holder_name

    def validate_card(self) -> bool:
        now = datetime.now()
        year_ok = self.__expired_year > now.year
        same_year_ok = self.__expired_year == now.year and self.__expired_month >= now.month
        return year_ok or same_year_ok


class DebitCard(Card):
    def __init__(self, card_number: str, holder_name: str, expired_month: int, expired_year: int, account: Account):
        super().__init__("Debit Card", card_number, holder_name, expired_month, expired_year)
        self.__account = account

    def get_account(self) -> Account:
        return self.__account

    def pay(self, amount: float) -> bool:
        if not self.validate_card():
            return False
        return self.__account.withdraw(amount)


class CreditCard(Card):
    def __init__(self, card_number: str, holder_name: str, expired_month: int, expired_year: int, credit_limit: float):
        super().__init__("Credit Card", card_number, holder_name, expired_month, expired_year)
        self.__credit_limit = credit_limit
        self.__used_credit = 0.0

    def get_credit_limit(self) -> float:
        return self.__credit_limit

    def get_used_credit(self) -> float:
        return self.__used_credit

    def get_available_credit(self) -> float:
        return self.__credit_limit - self.__used_credit

    def pay(self, amount: float) -> bool:
        if not self.validate_card():
            return False
        if amount <= 0:
            return False
        if self.get_available_credit() < amount:
            return False
        self.__used_credit += amount
        return True


class Cash(PaymentMethod):
    def __init__(self):
        super().__init__("Cash")

    def pay(self, amount: float) -> bool:
        return amount > 0


class Product:
    def __init__(self, product_id: int, name: str, price: float, stock: int):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_product_id(self) -> int:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def set_name(self, name: str) -> None:
        self.__name = name

    def set_price(self, price: float) -> None:
        self.__price = price

    def add_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.__stock += amount

    def reduce_stock(self, amount: int) -> bool:
        if amount <= 0:
            return False
        if self.__stock < amount:
            return False
        self.__stock -= amount
        return True

    def has_stock(self, amount: int = 1) -> bool:
        return self.__stock >= amount


class Store:
    def __init__(self, store_id: str, store_name: str):
        self.__store_id = store_id
        self.__store_name = store_name
        self.__products: List[Product] = []


    def get_store_id(self) -> str:
        return self.__store_id

    def get_store_name(self) -> str:
        return self.__store_name

    def get_products(self) -> List[Product]:
        return self.__products

    def add_product(self, product: Product) -> None:
        if self.find_product(product.get_product_id()) is not None:
            raise ValueError("product id already exists")
        self.__products.append(product)

    def find_product(self, product_id: int) -> Optional[Product]:
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product
        return None

    def increase_stock(self, product_id: int, amount: int) -> bool:
        product = self.find_product(product_id)
        if product is None:
            return False
        product.add_stock(amount)
        return True


class Seat:
    def __init__(self, seat_id: str, seat_type: SeatTier, seat_price: float):
        self.__seat_id = seat_id
        self.__seat_type = seat_type
        self.__seat_price = seat_price
        self.__occupant_member_id = ""

    def get_seat_id(self) -> str:
        return self.__seat_id

    def get_seat_type(self) -> SeatTier:
        return self.__seat_type

    def get_seat_price(self) -> float:
        return self.__seat_price

    def get_occupant_member_id(self) -> str:
        return self.__occupant_member_id

    def is_available(self) -> bool:
        return self.__occupant_member_id == ""

    def assign_occupant(self, member_id: str) -> None:
        self.__occupant_member_id = member_id

    def clear_occupant(self) -> None:
        self.__occupant_member_id = ""


class Match:
    def __init__(self, match_id: str, day: str, time_text: str, status: MatchStatus = MatchStatus.NOT_START):
        self.__match_id = match_id
        self.__day = day
        self.__time_text = time_text
        self.__status = status
        self.__seats: List[Seat] = []
        self.__players: List[Player] = []
        self.__allowed_players = []

        
    def allow_player(self, player: Player):

        player_id = player.get_user_id()

        if player_id not in self.__allowed_players:
            self.__allowed_players.append(player_id)

    def is_player_in_match(self, player):
        return player in self.__players

    def get_match_id(self) -> str:
        return self.__match_id

    def get_day(self) -> str:
        return self.__day

    def get_time_text(self) -> str:
        return self.__time_text

    def get_status(self) -> MatchStatus:
        return self.__status

    def add_seat(self, seat: Seat) -> None:
        if self.find_seat(seat.get_seat_id()) is not None:
            raise ValueError("seat id already exists in match")
        self.__seats.append(seat)

    def get_seats(self) -> List[Seat]:
        return self.__seats

    def find_seat(self, seat_id: str) -> Optional[Seat]:
        for seat in self.__seats:
            if seat.get_seat_id() == seat_id:
                return seat
        return None

    def get_available_seats(self) -> List[Seat]:
        result: List[Seat] = []
        for seat in self.__seats:
            if seat.is_available():
                result.append(seat)
        return result

    def add_player(self, player: Player) -> None:
        if self.find_player_index(player.get_user_id()) == -1:
            self.__players.append(player)
            player.add_match(self)

    def find_player_index(self, player_id: str) -> int:
        index = 0
        while index < len(self.__players):
            if self.__players[index].get_user_id() == player_id:
                return index
            index += 1
        return -1

    def has_player(self, player_id):
        for p in self.__players:
            if p.get_user_id() == player_id:
                return True

        return False


    def start_datetime(self, base_time: DemoTimeManager) -> datetime:
        current = base_time.now()
        pieces = self.__time_text.split(":")
        hour = int(pieces[0])
        minute = int(pieces[1])
        return datetime(current.year, current.month, current.day, hour, minute)

    def get_players(self) -> List[Player]:
        return self.__players


class Ticket:
    def __init__(self, ticket_id: str, match: Match, seat: Seat, member_id: str):
        self.__ticket_id = ticket_id
        self.__match = match
        self.__seat = seat
        self.__member_id = member_id
        self.__status = TicketStatus.VALID

    def get_ticket_id(self) -> str:
        return self.__ticket_id

    def get_match(self) -> Match:
        return self.__match

    def get_seat(self) -> Seat:
        return self.__seat

    def get_member_id(self) -> str:
        return self.__member_id

    def get_status(self) -> TicketStatus:
        return self.__status

    def mark_used(self) -> None:
        self.__status = TicketStatus.USED

    def mark_expired(self) -> None:
        self.__status = TicketStatus.EXPIRED

    def is_enterable(self, time_manager: DemoTimeManager) -> bool:
        if self.__status != TicketStatus.VALID:
            return False
        current = time_manager.now()
        start = self.__match.start_datetime(time_manager)
        open_time = start - timedelta(hours=1)
        close_time = start + timedelta(hours=4)
        return open_time <= current <= close_time


class BaseOrder(ABC):
    def __init__(self, order_id: str, member: Member):
        self.__order_id = order_id
        self.__member = member
        self.__status = OrderStatus.PENDING
        self.__created_at = datetime.now()
        self.__paid_at: Optional[datetime] = None
        self.__receipt: Optional[Receipt] = None

    def get_order_id(self) -> str:
        return self.__order_id

    def get_member(self) -> Member:
        return self.__member

    def get_status(self) -> OrderStatus:
        return self.__status

    def get_created_at(self) -> datetime:
        return self.__created_at

    def get_paid_at(self) -> Optional[datetime]:
        return self.__paid_at

    def get_receipt(self) -> Optional[Receipt]:
        return self.__receipt

    def mark_paid(self, paid_at: datetime, receipt: Receipt) -> None:
        self.__status = OrderStatus.PAID
        self.__paid_at = paid_at
        self.__receipt = receipt
        self.__member.add_receipt(receipt)

    def cancel(self) -> None:
        self.__status = OrderStatus.CANCELLED

    def is_pending(self) -> bool:
        return self.__status == OrderStatus.PENDING

    @abstractmethod
    def total_price(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError


class SeatBookingOrder(BaseOrder):
    def __init__(self, order_id: str, member: Member, match: Match, seat: Seat):
        super().__init__(order_id, member)
        self.__match = match
        self.__seat = seat
        self.__ticket: Optional[Ticket] = None

    def get_match(self) -> Match:
        return self.__match

    def get_seat(self) -> Seat:
        return self.__seat

    def get_ticket(self) -> Optional[Ticket]:
        return self.__ticket

    def set_ticket(self, ticket: Ticket) -> None:
        self.__ticket = ticket

    def total_price(self) -> float:
        return self.__seat.get_seat_price()

    def get_description(self) -> str:
        return "Seat Booking"


class StoreOrder(BaseOrder):
    def __init__(self, order_id: str, member: Member, match: Match):
        super().__init__(order_id, member)
        self.__match = match
        self.__products: List[Product] = []

    def add_product(self, product: Product) -> None:
        self.__products.append(product)

    def get_products(self) -> List[Product]:
        return self.__products

    def get_match(self) -> Match:
        return self.__match

    def can_reduce_stock(self) -> bool:
        checked_ids: List[int] = []
        checked_counts: List[int] = []
        for product in self.__products:
            product_id = product.get_product_id()
            index = 0
            found = -1
            while index < len(checked_ids):
                if checked_ids[index] == product_id:
                    found = index
                    break
                index += 1
            if found == -1:
                checked_ids.append(product_id)
                checked_counts.append(1)
            else:
                checked_counts[found] += 1
        index = 0
        while index < len(checked_ids):
            product = self.find_product_in_order(checked_ids[index])
            if product is None:
                return False
            if not product.has_stock(checked_counts[index]):
                return False
            index += 1
        return True

    def reduce_stock_after_payment(self) -> bool:
        if not self.can_reduce_stock():
            return False
        reduced_ids: List[int] = []
        for product in self.__products:
            product_id = product.get_product_id()
            if self.__count_in_list(reduced_ids, product_id) == 0:
                needed = self.__count_product(product_id)
                product.reduce_stock(needed)
                reduced_ids.append(product_id)
        return True

    def __count_product(self, product_id: int) -> int:
        count = 0
        for product in self.__products:
            if product.get_product_id() == product_id:
                count += 1
        return count

    def __count_in_list(self, values: List[int], target: int) -> int:
        count = 0
        for value in values:
            if value == target:
                count += 1
        return count

    def find_product_in_order(self, product_id: int) -> Optional[Product]:
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product
        return None

    def total_price(self) -> float:
        total = 0.0
        for product in self.__products:
            total += product.get_price()
        return total

    def get_description(self) -> str:
        return "Store Order"


class NoShowFeeOrder(BaseOrder):
    def __init__(self, order_id: str, member: Member, ticket: Ticket, fee_amount: float):
        super().__init__(order_id, member)
        self.__ticket = ticket
        self.__fee_amount = fee_amount

    def get_ticket(self) -> Ticket:
        return self.__ticket

    def total_price(self) -> float:
        return self.__fee_amount

    def get_description(self) -> str:
        return "No Show Fee"


class Tournament:
    def __init__(self, tournament_id: str, tournament_name: str):
        self.__tournament_id = tournament_id
        self.__tournament_name = tournament_name
        self.__matches: List[Match] = []
        self.__stores: List[Store] = []
        self.__current_store: Optional[Store] = None

    def get_player_matches(self, player_id: str):
        result = []

        for match in self.__matches:
            for player in match.get_players():
                if player.get_user_id() == player_id:
                    result.append(match)

        return result

    def add_store(self, store: Store) -> None:
        self.__stores.append(store)

    def find_store(self, store_id: str) -> Optional[Store]:
        for store in self.__stores:
            if store.get_store_id() == store_id:
                return store
        return None

    def login_store(self, store_id: str) -> bool:
        store = self.find_store(store_id)
        if store is None:
            return False
        self.__current_store = store
        return True

    def logout_store(self) -> None:
        self.__current_store = None

    def get_current_store(self) -> Optional[Store]:
        return self.__stores[0]

    def get_tournament_id(self) -> str:
        return self.__tournament_id

    def get_tournament_name(self) -> str:
        return self.__tournament_name

    def add_match(self, match: Match) -> None:
        self.__matches.append(match)

    def get_matches(self) -> List[Match]:
        return self.__matches

    def get_stores(self) -> List[Store]:
        return self.__stores

    def find_match(self, match_id: str) -> Optional[Match]:
        for match in self.__matches:
            if match.get_match_id() == match_id:
                return match
        return None


class IdGenerator:
    def __init__(self):
        self.__order_running = 1
        self.__ticket_running = 1
        self.__receipt_running = 1

    def next_order_id(self) -> str:
        value = f"ORD{self.__order_running:03d}"
        self.__order_running += 1
        return value

    def next_ticket_id(self) -> str:
        value = f"TIC{self.__ticket_running:03d}"
        self.__ticket_running += 1
        return value

    def next_receipt_id(self) -> str:
        value = f"REC{self.__receipt_running:03d}"
        self.__receipt_running += 1
        return value


class Server:
    def __init__(self, time_manager: DemoTimeManager, tournament: Tournament, id_generator: IdGenerator):
        self.__time_manager = time_manager
        self.__tournament = tournament
        self.__id_generator = id_generator
        self.__members: List[Member] = []
        self.__players: List[Player] = []
        self.__orders: List[BaseOrder] = []
        self.__current_member: Optional[Member] = None
        self.__current_player: Optional[Player] = None
        self.__store_managers: List[StoreManager] = []
        self.__current_store_manager: Optional[StoreManager] = None

    def add_store_manager(self, manager: StoreManager) -> None:
        self.__store_managers.append(manager)

    def get_current_store_manager(self) -> Optional[StoreManager]:
        return self.__current_store_manager

    def find_store_manager(self, user_id: str) -> Optional[StoreManager]:
        for manager in self.__store_managers:
            if manager.get_user_id() == user_id:
                return manager
        return None 

    def login_store_manager(self, user_id: str, password: str) -> bool:
        manager = self.find_store_manager(user_id)
        if manager is None:
            return False
        if not manager.login(password):
            return False
        self.__current_store_manager = manager
        return True

    def logout_store_manager(self) -> None:
        if self.__current_store_manager is not None:
            self.__current_store_manager.logout()
        self.__current_store_manager = None

    def add_member(self, member: Member) -> None:
        self.__members.append(member)

    def add_player(self, player: Player) -> None:
        self.__players.append(player)

    def get_tournament(self) -> Tournament:
        return self.__tournament

    def get_current_member(self) -> Optional[Member]:
        return self.__current_member

    def get_current_player(self) -> Optional[Player]:
        return self.__current_player

    def login_member(self, user_id: str, password: str) -> bool:
        member = self.find_member(user_id)
        if member is None:
            return False
        if not member.login(password):
            return False
        self.__current_member = member
        return True

    def login_player(self, user_id: str, password: str) -> bool:
        player = self.find_player(user_id)
        if player is None:
            return False
        if not player.login(password):
            return False
        self.__current_player = player
        return True

    def logout_member(self) -> None:
        if self.__current_member is not None:
            self.__current_member.logout()
        self.__current_member = None

    def logout_player(self) -> None:
        if self.__current_player is not None:
            self.__current_player.logout()
        self.__current_player = None

    def find_member(self, user_id: str) -> Optional[Member]:
        for member in self.__members:
            if member.get_user_id() == user_id:
                return member
        return None

    def find_player(self, user_id: str) -> Optional[Player]:
        for player in self.__players:
            if player.get_user_id() == user_id:
                return player
        return None

    def find_order(self, order_id: str) -> Optional[BaseOrder]:
        for order in self.__orders:
            if order.get_order_id() == order_id:
                return order
        return None

    def find_ticket(self, ticket_id: str) -> Optional[Ticket]:
        for member in self.__members:
            for ticket in member.get_tickets():
                if ticket.get_ticket_id() == ticket_id:
                    return ticket
        return None

    def has_no_show_fee_order(self, ticket_id: str) -> bool:
        for order in self.__orders:
            if isinstance(order, NoShowFeeOrder):
                if order.get_ticket().get_ticket_id() == ticket_id:
                    if order.get_status() == OrderStatus.PENDING or order.get_status() == OrderStatus.PAID:
                        return True
        return False

    def auto_create_no_show_fee_order(self, ticket: Ticket) -> Optional[NoShowFeeOrder]:
        if ticket.get_status() != TicketStatus.VALID:
            return None
        start = ticket.get_match().start_datetime(self.__time_manager)
        close_time = start + timedelta(hours=4)
        if self.__time_manager.now() <= close_time:
            return None
        if self.has_no_show_fee_order(ticket.get_ticket_id()):
            return None
        member = self.find_member(ticket.get_member_id())
        if member is None:
            return None
        fee_amount = ticket.get_seat().get_seat_price() * 0.5
        order = NoShowFeeOrder(self.__id_generator.next_order_id(), member, ticket, fee_amount)
        self.__orders.append(order)
        member.add_order(order)
        ticket.mark_expired()
        return order

    def cleanup_expired_orders(self):
        now = self.__time_manager.now()
        for order in self.__orders:
            if isinstance(order, SeatBookingOrder) and order.get_status() == OrderStatus.PENDING:
                if now > order.get_created_at() + timedelta(minutes=30):
                    order.get_seat().clear_occupant()
                    order.cancel()

    def get_all_matches(self) -> List[Match]:
        return self.__tournament.get_matches()

    def create_seat_order(self, match_id: str, seat_id: str) -> SeatBookingOrder:
        if self.__current_member is None:
            raise ValueError("member is not logged in")
        match = self.__tournament.find_match(match_id)
        if match is None:
            raise ValueError("match not found")
        seat = match.find_seat(seat_id)
        if seat is None:
            raise ValueError("seat not found")
        if not seat.is_available():
            raise ValueError("seat is already booked")
        seat.assign_occupant(self.__current_member.get_user_id())
        order = SeatBookingOrder(self.__id_generator.next_order_id(), self.__current_member, match, seat)
        self.__orders.append(order)
        self.__current_member.add_order(order)
        return order

    def create_store_order(self, match_id: str, product_ids: List[int], store_id: str = "S001") -> StoreOrder:
        if self.__current_member is None:
            raise ValueError("member is not logged in")
        match = self.__tournament.find_match(match_id)
        if match is None:
            raise ValueError("match not found")
        store = self.__tournament.find_store(store_id)
        if store is None:
            raise ValueError("store not found")
        order = StoreOrder(self.__id_generator.next_order_id(), self.__current_member, match)
        for product_id in product_ids:
            product = store.find_product(product_id)
            if product is None:
                raise ValueError(f"product {product_id} not found")
            order.add_product(product)
        self.__orders.append(order)
        self.__current_member.add_order(order)
        return order

    def create_no_show_fee_order(self, ticket_id: str, fee_amount: float) -> NoShowFeeOrder:
        if self.__current_member is None:
            raise ValueError("member is not logged in")
        ticket = self.find_ticket(ticket_id)
        if ticket is None:
            raise ValueError("ticket not found")
        if ticket.get_member_id() != self.__current_member.get_user_id():
            raise ValueError("ticket does not belong to current member")
        order = NoShowFeeOrder(self.__id_generator.next_order_id(), self.__current_member, ticket, fee_amount)
        self.__orders.append(order)
        self.__current_member.add_order(order)
        return order

    def pay_order(self, order_id: str, payment_method: PaymentMethod, coupon_id: str = "") -> Receipt:
        order = self.find_order(order_id)
        if order is None:
            raise ValueError("order not found")
        if self.__current_member is None:
            raise ValueError("member is not logged in")
        if order.get_member().get_user_id() != self.__current_member.get_user_id():
            raise ValueError("order does not belong to current member")
        if not order.is_pending():
            raise ValueError("order is not pending")
        amount = order.total_price()
        if coupon_id != "":
            if not self.__current_member.owns_coupon(coupon_id):
                raise ValueError("coupon is not owned by current member or already used")
            coupon = self.__current_member.find_coupon(coupon_id)
            if coupon is None:
                raise ValueError("coupon not found")
            amount = amount * (1.0 - coupon.get_discount_rate())
            coupon.mark_used()
        if isinstance(order, StoreOrder):
            if not order.can_reduce_stock():
                raise ValueError("stock is not enough")
        if not payment_method.pay(amount):
            raise ValueError("payment failed")
        if isinstance(order, StoreOrder):
            reduced = order.reduce_stock_after_payment()
            if not reduced:
                raise ValueError("stock reduction failed")
        receipt = Receipt(
            self.__id_generator.next_receipt_id(),
            order.get_order_id(),
            amount,
            order.get_description(),
            self.__time_manager.now(),
        )
        order.mark_paid(self.__time_manager.now(), receipt)
        if isinstance(order, SeatBookingOrder):
            ticket = Ticket(self.__id_generator.next_ticket_id(), order.get_match(), order.get_seat(), self.__current_member.get_user_id())
            order.set_ticket(ticket)
            self.__current_member.add_ticket(ticket)
        return receipt

#schemas
class LoginBody(BaseModel):
    user_id: str
    password: str


class SelectClassBody(BaseModel):
    match_id: str
    player_class: PlayerClass


class CreateSeatOrderBody(BaseModel):
    match_id: str
    seat_id: str


class CreateStoreOrderBody(BaseModel):
    match_id: str
    product_ids: List[int]
    store_id: str = "S001"


class PayOrderBody(BaseModel):
    order_id: str
    payment_type: str
    coupon_id: str = ""


class ProductCreateBody(BaseModel):
    product_id: int
    name: str
    price: float
    stock: int

class UseTicketBody(BaseModel):
    ticket_id: str

class StockBody(BaseModel):
    amount: int


class DemoTimeSetBody(BaseModel):
    iso_datetime: str


class DemoTimeAdvanceBody(BaseModel):
    minutes: int = 0
    hours: int = 0

#setup

app = FastAPI(title="Tournament API Full List Only")


time_manager = DemoTimeManager()
id_generator = IdGenerator()

tournament = Tournament("T001", "Campus Tournament")

store = Store("S001", "Main Store")
store.add_product(Product(1, "Water", 10.0, 20))
store.add_product(Product(2, "Popcorn", 30.0, 10))
store.add_product(Product(3, "Burger", 79.0, 5))

tournament.add_store(store)

server = Server(time_manager, tournament, id_generator)

# members

# -------------------------
# CREATE MEMBERS (3)
# -------------------------

member1 = Member(
    "member1",
    "Member One",
    "0811111111",
    "member1@email.com",
    "pass123",
    MemberTier.REGULAR
)

member2 = Member(
    "member2",
    "Member Two",
    "0822222222",
    "member2@email.com",
    "pass123",
    MemberTier.REGULAR
)

member3 = Member(
    "member3",
    "Member Three",
    "0833333333",
    "member3@email.com",
    "pass123",
    MemberTier.VIP
)

members = [member1, member2, member3]

server.add_member(member1)
server.add_member(member2)
server.add_member(member3)

# -------------------------
# CREATE PLAYERS (8)
# -------------------------

player1 = Player("player1","Player One","0900000001","p1@email.com","pass123")
player2 = Player("player2","Player Two","0900000002","p2@email.com","pass123")
player3 = Player("player3","Player Three","0900000003","p3@email.com","pass123")
player4 = Player("player4","Player Four","0900000004","p4@email.com","pass123")
player5 = Player("player5","Player Five","0900000005","p5@email.com","pass123")
player6 = Player("player6","Player Six","0900000006","p6@email.com","pass123")
player7 = Player("player7","Player Seven","0900000007","p7@email.com","pass123")
player8 = Player("player8","Player Eight","0900000008","p8@email.com","pass123")

players = [
    player1,
    player2,
    player3,
    player4,
    player5,
    player6,
    player7,
    player8
]

server.add_player(player1)
server.add_player(player2)
server.add_player(player3)
server.add_player(player4)
server.add_player(player5)
server.add_player(player6)
server.add_player(player7)
server.add_player(player8)

# -------------------------
# CREATE MATCHES (3)
# -------------------------

match1 = Match("M001","Day1","10:00")
match2 = Match("M002","Day1","11:00")
match3 = Match("M003","Day1","12:00")

# -------------------------
# ADD SEATS
# -------------------------

match1.add_seat(Seat("A1", SeatTier.VIP, 500))
match1.add_seat(Seat("A2", SeatTier.REGULAR, 200))
match1.add_seat(Seat("A3", SeatTier.REGULAR, 200))

match2.add_seat(Seat("B1", SeatTier.VIP, 500))
match2.add_seat(Seat("B2", SeatTier.REGULAR, 200))
match2.add_seat(Seat("B3", SeatTier.REGULAR, 200))

match3.add_seat(Seat("C1", SeatTier.VIP, 500))
match3.add_seat(Seat("C2", SeatTier.REGULAR, 200))
match3.add_seat(Seat("C3", SeatTier.REGULAR, 200))

tournament.add_match(match1)
tournament.add_match(match2)
tournament.add_match(match3)


match1.add_player(player1)
match1.add_player(player2)
match1.add_player(player3)
#
player1.add_match(match1)
player2.add_match(match1)
player3.add_match(match1)

player4.add_match(match2)
player5.add_match(match2)
player6.add_match(match2)

player7.add_match(match3)
player8.add_match(match3) #

match2.add_player(player4)
match2.add_player(player5)
match2.add_player(player6)

match3.add_player(player7)
match3.add_player(player8)

VIP10 = Coupon("COU001", "VIP10", .1, "member1")
member1.add_coupon(VIP10)
sample_account = Account("ACC001","Demo Owner",10000,5000)

sample_debit_card = DebitCard(
    "1111222233334444",
    "Demo Owner",
    12,
    2030,
    sample_account
)

sample_credit_card = CreditCard(
    "5555666677778888",
    "Demo Owner",
    12,
    2030,
    20000
)

member1.add_card(sample_credit_card)
member1.add_card(sample_debit_card)
sample_cash = Cash()

manager1 = StoreManager("manager1", "Manager One", "0899999999", "m1@email.com", "pass123")
server.add_store_manager(manager1)


def get_payment_method(payment_type: str) -> PaymentMethod:
    if payment_type == "debit":
        return sample_debit_card
    if payment_type == "credit":
        return sample_credit_card
    if payment_type == "cash":
        return sample_cash
    raise ValueError("unsupported payment type")



