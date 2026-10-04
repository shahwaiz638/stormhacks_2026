import json
import uuid

from database import get_connection


def write_test_report():
    conn = get_connection()

    # Fake 768-dimensional embedding for testing the database.
    # Later this comes from generate_embedding().
    test_vector = [0.01] * 768

    report = {
        "id": str(uuid.uuid4()),
        "report_type": "FOUND",
        "title": "Navy Herschel Backpack",
        "description": "Found a navy blue Herschel backpack near the library.",
        "image_url": None,

        "category": "Backpack",
        "primary_color": "Navy Blue",
        "brand": "Herschel",
        "model": None,

        "distinctive_features": [
            "Red keychain",
            "Canvas material"
        ],

        "keywords": [
            "backpack",
            "navy",
            "herschel",
            "red keychain"
        ],

        "location_name": "SFU Library"
    }

    sql = """
        INSERT INTO reports (
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
            description_vector
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    report["id"],
                    report["report_type"],
                    report["title"],
                    report["description"],
                    report["image_url"],
                    report["category"],
                    report["primary_color"],
                    report["brand"],
                    report["model"],
                    json.dumps(report["distinctive_features"]),
                    json.dumps(report["keywords"]),
                    report["location_name"],
                    json.dumps(test_vector),
                )
            )

        conn.commit()

        print("Successfully inserted report!")
        print("Report ID:", report["id"])

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    write_test_report()