from tasks import generate_certificate

cert_data = {
    "user_name": "Abhijit",
    "college": "XYZ University", 
    "certificate_id": "CERT-607bb29f5139e727",
    "issued_at": "2025-02-11T05:16:07.163954+05:30",
    # Optional fields
    "user_id": 4,
    "test_id": 13
}

if __name__ == "__main__":
    try:
        result = generate_certificate.delay(cert_data)
        print(f"Task ID: {result.id}")
    except Exception as e:
        print(f"Error: {str(e)}")