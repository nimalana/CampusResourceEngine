from pydantic import BaseModel
from typing import Optional, List


class Course(BaseModel):
    id: str
    code: str
    title: str
    department: str
    credits: int
    instructor: str
    description: str
    seats_available: int
    total_seats: int
    schedule: str
    location: str
    tags: List[str] = []


class Club(BaseModel):
    id: str
    name: str
    category: str
    description: str
    meeting_schedule: str
    location: str
    president: str
    email: str
    member_count: int
    founded: int
    tags: List[str] = []


class ResearchProject(BaseModel):
    id: str
    title: str
    department: str
    pi: str          # principal investigator
    description: str
    funding_source: str
    funding_amount: str
    status: str      # active | completed | recruiting
    lab: str
    tags: List[str] = []


class Event(BaseModel):
    id: str
    title: str
    organizer: str
    date: str
    time: str
    location: str
    description: str
    category: str
    capacity: Optional[int] = None
    rsvp_required: bool = False
    tags: List[str] = []


class DiningLocation(BaseModel):
    id: str
    name: str
    type: str        # dining_hall | cafe | restaurant | food_truck
    location: str
    hours: str
    menu_highlights: List[str]
    meal_plan_accepted: bool
    cuisine_types: List[str]
    rating: float
    tags: List[str] = []


class CachedResponse(BaseModel):
    data: object
    cache_hit: bool
    shard: str
    replicas: List[str]
