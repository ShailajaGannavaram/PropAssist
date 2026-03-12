import os
import django
import csv
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import Property

CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata']

def extract_city(location):
    for city in CITIES:
        if city.lower() in location.lower():
            return city
    return None

def guess_property_type(title):
    title = title.lower()
    if 'villa' in title:
        return 'villa'
    elif 'plot' in title or 'land' in title:
        return 'plot'
    elif 'commercial' in title or 'office' in title or 'shop' in title:
        return 'commercial'
    elif 'independent house' in title or 'bungalow' in title:
        return 'house'
    else:
        return 'apartment'

def guess_bedrooms(title):
    title = title.lower()
    for n in ['10','9','8','7','6','5','4','3','2','1']:
        if f'{n} bhk' in title or f'{n}bhk' in title:
            return int(n)
    return 2

def clean_price(price_str):
    price_str = str(price_str).replace(',', '').replace('₹', '').replace(' ', '').strip().lower()
    try:
        if 'cr' in price_str:
            number = float(''.join(c for c in price_str if c.isdigit() or c == '.'))
            return round(number * 10000000, 2)
        elif 'lac' in price_str or 'lakh' in price_str or price_str.endswith('l'):
            number = float(''.join(c for c in price_str if c.isdigit() or c == '.'))
            return round(number * 100000, 2)
        else:
            cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
            return round(float(cleaned), 2) if cleaned else 0
    except:
        return 0

def clean_area(area_str):
    try:
        cleaned = ''.join(c for c in str(area_str) if c.isdigit() or c == '.')
        return int(float(cleaned)) if cleaned else 0
    except:
        return 0

def import_csv(filepath, limit=None):
    imported = 0
    skipped = 0

    # Clear existing imported data
    confirm = input("This will delete all existing properties and reimport. Type YES to continue: ")
    if confirm != "YES":
        print("Cancelled.")
        return

    Property.objects.all().delete()
    print("Existing properties cleared.")

    with open(filepath, encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if limit and imported >= limit:
                break

            try:
                title = str(row.get('Property Title', '')).strip()
                location = str(row.get('Location', '')).strip()
                price_raw = str(row.get('Price', '0')).strip()
                area_raw = str(row.get('Total_Area', '0')).strip()
                description = str(row.get('Description', '')).strip()
                baths_raw = str(row.get('Baths', '1')).strip()

                if not title or not location:
                    skipped += 1
                    continue

                city = extract_city(location)
                if not city:
                    skipped += 1
                    continue

                price = clean_price(price_raw)
                area = clean_area(area_raw)

                if price == 0 or area == 0:
                    skipped += 1
                    continue

                try:
                    bathrooms = int(float(baths_raw))
                except:
                    bathrooms = 1

                Property.objects.create(
                    title=title[:200],
                    property_type=guess_property_type(title),
                    location=location[:200],
                    city=city,
                    price=price,
                    bedrooms=guess_bedrooms(title),
                    bathrooms=bathrooms,
                    area_sqft=area,
                    description=description[:1000] if description else f"{title} in {location}.",
                    is_available=True
                )
                imported += 1

                if imported % 100 == 0:
                    print(f"Imported {imported} properties...")

            except Exception as e:
                skipped += 1
                continue

    print(f"\nDone!")
    print(f"Imported : {imported}")
    print(f"Skipped  : {skipped}")

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "Real_Estate_Data_V21.csv"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print(f"Importing from {filepath}...")
    import_csv(filepath, limit)
