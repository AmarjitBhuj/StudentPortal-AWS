import json
import os
import boto3
import psycopg2

# AWS Secrets Manager
secrets_client = boto3.client("secretsmanager")
SECRET_NAME = "student-portal/rds-credentials"


def get_db_password():
    print("DIAGNOSTIC: Calling Secrets Manager")

    response = secrets_client.get_secret_value(
        SecretId=SECRET_NAME
    )

    print("DIAGNOSTIC: Secrets Manager responded")

    secret = json.loads(response["SecretString"])
    return secret["password"]


def get_db_connection():
    password = get_db_password()

    print("DIAGNOSTIC: Connecting to RDS")

    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=password,
        connect_timeout=5
    )

    print("DIAGNOSTIC: RDS connection successful")
    return connection


def lambda_handler(event, context):
    method = event.get(
        "requestContext", {}
    ).get("http", {}).get("method", "POST")

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if method == "POST":
            body = event.get("body") or {}

            if isinstance(body, str):
                body = json.loads(body)

            name = body.get("name")
            email = body.get("email")
            course = body.get("course")
            year = body.get("year")

            if not name or not email:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "message": "Name and email are required"
                    })
                }

            cursor.execute(
                """
                INSERT INTO students
                    (name, email, course, year)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, email, course, year, created_at;
                """,
                (name, email, course, year)
            )

            student = cursor.fetchone()
            connection.commit()

            return {
                "statusCode": 201,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Student added successfully!",
                    "student": {
                        "id": student[0],
                        "name": student[1],
                        "email": student[2],
                        "course": student[3],
                        "year": student[4],
                        "created_at": str(student[5])
                    }
                })
            }

        elif method == "GET":
            cursor.execute(
                """
                SELECT id, name, email, course, year, created_at
                FROM students
                ORDER BY id;
                """
            )

            rows = cursor.fetchall()

            students = [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "course": row[3],
                    "year": row[4],
                    "created_at": str(row[5])
                }
                for row in rows
            ]

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "students": students
                })
            }

        else:
            return {
                "statusCode": 405,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Method not allowed"
                })
            }

    except Exception as error:
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))

        if connection:
            connection.rollback()

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()