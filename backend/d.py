# delete_data.py
from app.database import SessionLocal, engine
from app.models import WorkSchedule, Line, Reservation, Customer,Admin
from sqlalchemy import text

def delete_all_data():
    db = SessionLocal()
    try:
        # ⚠️ ترتیب پاک کردن مهمه! (به خاطر کلیدهای خارجی)
        
# 1. اول رکوردهای وابسته رو پاک کنید
        print("🗑️ پاک کردن ادمی...")
        db.query(Admin).delete()

        # 1. اول رکوردهای وابسته رو پاک کنید
        print("🗑️ پاک کردن برنامه‌های کاری...")
        db.query(WorkSchedule).delete()
        
        print("🗑️ پاک کردن رزروها...")
        db.query(Reservation).delete()
        
        # 2. بعد خطوط (lines) رو پاک کنید
        print("🗑️ پاک کردن خطوط...")
        db.query(Line).delete()
        
        # 3. آخر مشتری‌ها رو پاک کنید
        print("🗑️ پاک کردن مشتری‌ها...")
        db.query(Customer).delete()
        
        db.commit()
        print("✅ تمام دیتاها با موفقیت پاک شدند!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطا در پاک کردن دیتاها: {e}")
    finally:
        db.close()

def delete_specific_tables():
    """پاک کردن فقط بعضی جدول‌ها"""
    db = SessionLocal()
    try:
        # فقط برنامه‌های کاری و خطوط رو پاک کن
        print("🗑️ پاک کردن برنامه‌های کاری...")
        db.query(WorkSchedule).delete()
        
        print("🗑️ پاک کردن خطوط...")
        db.query(Line).delete()
        
        # رزروها و مشتری‌ها رو نگه دار
        # db.query(Reservation).delete()
        # db.query(Customer).delete()
        
        db.commit()
        print("✅ دیتاهای مورد نظر پاک شدند!")
    except Exception as e:
        db.rollback()
        print(f"❌ خطا: {e}")
    finally:
        db.close()

def reset_work_schedules():
    """فقط برنامه‌های کاری رو پاک کن"""
    db = SessionLocal()
    try:
        print("🗑️ پاک کردن تمام برنامه‌های کاری...")
        deleted = db.query(WorkSchedule).delete()
        db.commit()
        print(f"✅ {deleted} برنامه کاری پاک شد!")
    except Exception as e:
        db.rollback()
        print(f"❌ خطا: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("1. پاک کردن تمام دیتاها")
    print("2. پاک کردن فقط برنامه‌های کاری و خطوط")
    print("3. پاک کردن فقط برنامه‌های کاری")
    
    choice = input("انتخاب کنید (1-3): ")
    
    if choice == "1":
        delete_all_data()
    elif choice == "2":
        delete_specific_tables()
    elif choice == "3":
        reset_work_schedules()
    else:
        print("❌ انتخاب نامعتبر!")