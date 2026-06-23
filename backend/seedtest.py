"""Seed script — Beauty Salon Database (نسخه جدید و درست)"""
import hashlib
from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models import Admin, Customer, Line, WorkSchedule, Reservation

# ایجاد جداول
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# اگر ادمین وجود داشت، seeding رو رد کن
if db.query(Admin).count() > 0:
    print("✅ Database already seeded. Skipping.")
    db.close()
    exit(0)

print("🚀 Starting fresh seeding...")

# ==================== 1. ادمین ====================
admin = Admin(
    username="admin",
    password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
    created_at=datetime.utcnow().isoformat()
)
db.add(admin)
db.flush()
print("👤 Admin created")

# ==================== 2. لاین‌ها (خدمات) ====================
lines_data = [
    {"name_line": "ناخن", "duration_minutes": 90, "price": 350000, "name_service": "کاشت و طراحی ناخن"},
    {"name_line": "ناخن", "duration_minutes": 60, "price": 250000, "name_service": "پدیکور"},
    {"name_line": "مو", "duration_minutes": 90, "price": 2000000, "name_service": "کراتین مو"},
    {"name_line": "مو", "duration_minutes": 75, "price": 1500000, "name_service": "رنگ و لایت مو"},
    {"name_line": "میکاپ", "duration_minutes": 60, "price": 5000000, "name_service": "میکاپ عروس"},
    {"name_line": "پوست", "duration_minutes": 45, "price": 320000, "name_service": "فیشیال پوست"},
    {"name_line": "پوست", "duration_minutes": 30, "price": 180000, "name_service": "درماپیلینگ"},
    {"name_line": "پوست", "duration_minutes": 30, "price": 180000, "name_service": "اصلاح ابرو"},
]

lines = []
for data in lines_data:
    line = Line(**data)
    db.add(line)
    lines.append(line)

db.flush()
print(f"📋 {len(lines)} services created")

# ==================== 3. مشتریان ====================
customers_data = [
    {"name": "فاطمه رضایی", "phone_number": "09123456789", "register_date": datetime.utcnow().isoformat(), "notes": "مشتری وفادار", "address": "مشهد، خیابان انقلاب"},
    {"name": "زهرا محمدی", "phone_number": "09351234567", "register_date": datetime.utcnow().isoformat(), "notes": "آلرژی به عطر", "address": "اصفهان، خیابان وکیل آباد"},
    {"name": "مریم احمدی", "phone_number": "09119876543", "register_date": datetime.utcnow().isoformat(), "notes": None, "address": "شیراز، خیابان سعیدی"},
    {"name": "سارا کریمی", "phone_number": "09211234567", "register_date": datetime.utcnow().isoformat(), "notes": "درخواست خدمات ویژه", "address": "مشهد، خیابان امام رضا"},
    {"name": "نرگس حسینی", "phone_number": "09362223333", "register_date": datetime.utcnow().isoformat(), "notes": None, "address": "مشهد، خیابان امام"},
]

customers = []
for data in customers_data:
    cust = Customer(**data)
    db.add(cust)
    customers.append(cust)

db.flush()
print(f"👥 {len(customers)} customers created")

# ==================== 4. ساعات کاری (Work Schedules) ====================
weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه شنبه", "چهارشنبه"]
time_slots = [
    ("09:00", "11:00"),
    ("11:00", "13:00"),
    ("13:00", "15:00"),
    ("15:00", "17:00"),
    ("17:00", "19:00"),
]

schedules = []
for line in lines:
    for wd in weekdays:
        for start, end in time_slots:
            ws = WorkSchedule(
                line_id=line.id,
                weekday=wd,
                start_time=start,
                end_time=end,
                status="free"
            )
            db.add(ws)
            schedules.append(ws)

db.flush()
print(f"🕒 {len(schedules)} work schedule slots created (2-hour slots, Sat-Wed)")

# ==================== 5. رزروهای نمونه ====================
# چند رزرو نمونه برای تست
reservation_examples = [
    (lines[0], customers[0], "شنبه", "09:00"),   # ناخن - فاطمه
    (lines[2], customers[1], "یکشنبه", "11:00"), # کراتین - زهرا
    (lines[3], customers[2], "دوشنبه", "13:00"), # رنگ مو - مریم
    (lines[6], customers[3], "سه شنبه", "15:00"), # درماپیلینگ - سارا
    (lines[7], customers[0], "چهارشنبه", "09:00"), # اصلاح ابرو - فاطمه
]

for line, customer, weekday, start_time in reservation_examples:
    # پیدا کردن schedule_id
    schedule = db.query(WorkSchedule).filter(
        WorkSchedule.line_id == line.id,
        WorkSchedule.weekday == weekday,
        WorkSchedule.start_time == start_time
    ).first()

    if schedule:
        res = Reservation(
            line_id=line.id,
            customer_id=customer.id,
            schedule_id=schedule.id,
            total_price=line.price,
            status="confirmed"
        )
        db.add(res)
        
        # بروزرسانی وضعیت اسلات
        schedule.status = "busy"

db.commit()
db.close()

print("✅ Database seeded successfully!")
print(f"   • Admin: admin / admin123")
print(f"   • Services: {len(lines)}")
print(f"   • Customers: {len(customers)}")
print(f"   • Work slots: {len(schedules)} (۲ ساعته)")
print(f"   • Reservations: {len(reservation_examples)}")