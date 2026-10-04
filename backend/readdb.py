import json

from database import get_connection


def read_all_reports():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    report_type,
                    title,
                    description,
                    image_url,
                    category,
                    primary_color,
                    brand,
                    model,
                    distinctive_features,
                    keywords,
                    location_name,
                    event_timestamp,
                    created_at
                FROM reports
                ORDER BY created_at DESC
            """)

            rows = cursor.fetchall()

            print(f"\nFound {len(rows)} reports:\n")

            for row in rows:
                print("=" * 60)
                print(f"ID:          {row['id']}")
                print(f"Type:        {row['report_type']}")
                print(f"Title:       {row['title']}")
                print(f"Description: {row['description']}")
                print(f"Image:       {row['image_url']}")
                print(f"Category:    {row['category']}")
                print(f"Color:       {row['primary_color']}")
                print(f"Brand:       {row['brand']}")
                print(f"Model:       {row['model']}")
                print(f"Features:    {row['distinctive_features']}")
                print(f"Keywords:    {row['keywords']}")
                print(f"Location:    {row['location_name']}")
                print(f"Event Time:  {row['event_timestamp']}")
                print(f"Created At:  {row['created_at']}")

            print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    read_all_reports()