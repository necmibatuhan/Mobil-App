#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Debt Tracking App
Tests all high-priority backend functionality including:
- User Authentication System
- Debt CRUD Operations  
- Multi-Currency Support
- Dashboard Analytics
- Database Models and MongoDB Integration
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "https://3465f712-36f2-4485-a14c-2279310f7ece.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DebtTrackerTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.test_user_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
        self.test_user_password = "SecurePass123!"
        self.test_user_name = "John Doe"
        self.created_debt_ids = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status else "❌"
        print(f"{status_symbol} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not status:
            print(f"   Failed test: {test_name}")
        print()
        
    def test_user_registration(self):
        """Test user registration with valid and invalid data"""
        print("=== Testing User Authentication System ===")
        
        # Test valid registration
        registration_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": self.test_user_name
        }
        
        try:
            response = requests.post(f"{self.base_url}/register", 
                                   json=registration_data, 
                                   headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.auth_token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    self.log_test("User Registration (Valid)", True, 
                                f"User registered successfully with token")
                else:
                    self.log_test("User Registration (Valid)", False, 
                                f"Missing token in response: {data}")
            else:
                self.log_test("User Registration (Valid)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration (Valid)", False, f"Exception: {str(e)}")
            
        # Test duplicate email registration
        try:
            response = requests.post(f"{self.base_url}/register", 
                                   json=registration_data, 
                                   headers=self.headers)
            
            if response.status_code == 400:
                self.log_test("User Registration (Duplicate Email)", True, 
                            "Correctly rejected duplicate email")
            else:
                self.log_test("User Registration (Duplicate Email)", False, 
                            f"Should have returned 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("User Registration (Duplicate Email)", False, f"Exception: {str(e)}")
            
        # Test invalid email format
        invalid_email_data = {
            "email": "invalid-email",
            "password": self.test_user_password,
            "full_name": self.test_user_name
        }
        
        try:
            response = requests.post(f"{self.base_url}/register", 
                                   json=invalid_email_data, 
                                   headers=self.headers)
            
            if response.status_code == 422:
                self.log_test("User Registration (Invalid Email)", True, 
                            "Correctly rejected invalid email format")
            else:
                self.log_test("User Registration (Invalid Email)", False, 
                            f"Should have returned 422, got {response.status_code}")
                
        except Exception as e:
            self.log_test("User Registration (Invalid Email)", False, f"Exception: {str(e)}")
    
    def test_user_login(self):
        """Test user login with correct and incorrect credentials"""
        
        # Test valid login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = requests.post(f"{self.base_url}/login", 
                                   json=login_data, 
                                   headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    # Update token for subsequent tests
                    self.auth_token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    self.log_test("User Login (Valid Credentials)", True, 
                                "Login successful with valid credentials")
                else:
                    self.log_test("User Login (Valid Credentials)", False, 
                                f"Missing token in response: {data}")
            else:
                self.log_test("User Login (Valid Credentials)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("User Login (Valid Credentials)", False, f"Exception: {str(e)}")
            
        # Test invalid password
        invalid_login_data = {
            "email": self.test_user_email,
            "password": "WrongPassword123!"
        }
        
        try:
            response = requests.post(f"{self.base_url}/login", 
                                   json=invalid_login_data, 
                                   headers=self.headers)
            
            if response.status_code == 401:
                self.log_test("User Login (Invalid Password)", True, 
                            "Correctly rejected invalid password")
            else:
                self.log_test("User Login (Invalid Password)", False, 
                            f"Should have returned 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("User Login (Invalid Password)", False, f"Exception: {str(e)}")
            
        # Test non-existent user
        nonexistent_login_data = {
            "email": "nonexistent@example.com",
            "password": self.test_user_password
        }
        
        try:
            response = requests.post(f"{self.base_url}/login", 
                                   json=nonexistent_login_data, 
                                   headers=self.headers)
            
            if response.status_code == 401:
                self.log_test("User Login (Non-existent User)", True, 
                            "Correctly rejected non-existent user")
            else:
                self.log_test("User Login (Non-existent User)", False, 
                            f"Should have returned 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("User Login (Non-existent User)", False, f"Exception: {str(e)}")
    
    def test_jwt_authentication(self):
        """Test JWT token authentication for protected endpoints"""
        
        # Test with valid token
        try:
            response = requests.get(f"{self.base_url}/debts", headers=self.headers)
            
            if response.status_code == 200:
                self.log_test("JWT Authentication (Valid Token)", True, 
                            "Protected endpoint accessible with valid token")
            else:
                self.log_test("JWT Authentication (Valid Token)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("JWT Authentication (Valid Token)", False, f"Exception: {str(e)}")
            
        # Test with invalid token
        invalid_headers = self.headers.copy()
        invalid_headers["Authorization"] = "Bearer invalid_token_here"
        
        try:
            response = requests.get(f"{self.base_url}/debts", headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("JWT Authentication (Invalid Token)", True, 
                            "Correctly rejected invalid token")
            else:
                self.log_test("JWT Authentication (Invalid Token)", False, 
                            f"Should have returned 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("JWT Authentication (Invalid Token)", False, f"Exception: {str(e)}")
            
        # Test without token
        no_auth_headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.get(f"{self.base_url}/debts", headers=no_auth_headers)
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("JWT Authentication (No Token)", True, 
                            "Correctly rejected request without token")
            else:
                self.log_test("JWT Authentication (No Token)", False, 
                            f"Should have returned 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_test("JWT Authentication (No Token)", False, f"Exception: {str(e)}")
    
    def test_debt_crud_operations(self):
        """Test comprehensive debt CRUD operations"""
        print("=== Testing Debt CRUD Operations ===")
        
        # Test Create Debt - TRY currency
        debt_data_try = {
            "debt_type": "i_owe",
            "person_name": "Alice Johnson",
            "amount": 1500.0,
            "currency": "TRY",
            "description": "Borrowed money for rent",
            "category": "rent",
            "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        try:
            response = requests.post(f"{self.base_url}/debts", 
                                   json=debt_data_try, 
                                   headers=self.headers)
            
            if response.status_code == 200:
                debt = response.json()
                if all(key in debt for key in ["id", "person_name", "amount", "currency"]):
                    self.created_debt_ids.append(debt["id"])
                    self.log_test("Create Debt (TRY Currency)", True, 
                                f"Debt created with ID: {debt['id']}")
                else:
                    self.log_test("Create Debt (TRY Currency)", False, 
                                f"Missing required fields in response: {debt}")
            else:
                self.log_test("Create Debt (TRY Currency)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Create Debt (TRY Currency)", False, f"Exception: {str(e)}")
            
        # Test Create Debt - USD currency
        debt_data_usd = {
            "debt_type": "they_owe",
            "person_name": "Bob Smith",
            "amount": 100.0,
            "currency": "USD",
            "description": "Lent money for lunch",
            "category": "personal_loan",
            "due_date": (datetime.utcnow() + timedelta(days=15)).isoformat()
        }
        
        try:
            response = requests.post(f"{self.base_url}/debts", 
                                   json=debt_data_usd, 
                                   headers=self.headers)
            
            if response.status_code == 200:
                debt = response.json()
                if debt.get("currency") == "USD" and debt.get("amount_in_try", 0) > 0:
                    self.created_debt_ids.append(debt["id"])
                    self.log_test("Create Debt (USD Currency)", True, 
                                f"USD debt created with TRY conversion: {debt['amount_in_try']}")
                else:
                    self.log_test("Create Debt (USD Currency)", False, 
                                f"Currency conversion issue: {debt}")
            else:
                self.log_test("Create Debt (USD Currency)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Create Debt (USD Currency)", False, f"Exception: {str(e)}")
            
        # Test Create Debt - EUR currency
        debt_data_eur = {
            "debt_type": "i_owe",
            "person_name": "Charlie Brown",
            "amount": 50.0,
            "currency": "EUR",
            "description": "Shared dinner expense",
            "category": "shared_expense",
            "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        try:
            response = requests.post(f"{self.base_url}/debts", 
                                   json=debt_data_eur, 
                                   headers=self.headers)
            
            if response.status_code == 200:
                debt = response.json()
                if debt.get("currency") == "EUR" and debt.get("amount_in_try", 0) > 0:
                    self.created_debt_ids.append(debt["id"])
                    self.log_test("Create Debt (EUR Currency)", True, 
                                f"EUR debt created with TRY conversion: {debt['amount_in_try']}")
                else:
                    self.log_test("Create Debt (EUR Currency)", False, 
                                f"Currency conversion issue: {debt}")
            else:
                self.log_test("Create Debt (EUR Currency)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Create Debt (EUR Currency)", False, f"Exception: {str(e)}")
            
        # Test Read All Debts
        try:
            response = requests.get(f"{self.base_url}/debts", headers=self.headers)
            
            if response.status_code == 200:
                debts = response.json()
                if isinstance(debts, list) and len(debts) >= len(self.created_debt_ids):
                    self.log_test("Read All Debts", True, 
                                f"Retrieved {len(debts)} debts")
                else:
                    self.log_test("Read All Debts", False, 
                                f"Expected list with at least {len(self.created_debt_ids)} debts, got: {debts}")
            else:
                self.log_test("Read All Debts", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Read All Debts", False, f"Exception: {str(e)}")
            
        # Test Read Single Debt
        if self.created_debt_ids:
            debt_id = self.created_debt_ids[0]
            try:
                response = requests.get(f"{self.base_url}/debts/{debt_id}", headers=self.headers)
                
                if response.status_code == 200:
                    debt = response.json()
                    if debt.get("id") == debt_id:
                        self.log_test("Read Single Debt", True, 
                                    f"Retrieved debt with ID: {debt_id}")
                    else:
                        self.log_test("Read Single Debt", False, 
                                    f"ID mismatch: expected {debt_id}, got {debt.get('id')}")
                else:
                    self.log_test("Read Single Debt", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test("Read Single Debt", False, f"Exception: {str(e)}")
                
        # Test Update Debt
        if self.created_debt_ids:
            debt_id = self.created_debt_ids[0]
            update_data = {
                "person_name": "Alice Johnson Updated",
                "amount": 2000.0,
                "description": "Updated rent payment"
            }
            
            try:
                response = requests.put(f"{self.base_url}/debts/{debt_id}", 
                                      json=update_data, 
                                      headers=self.headers)
                
                if response.status_code == 200:
                    debt = response.json()
                    if (debt.get("person_name") == update_data["person_name"] and 
                        debt.get("amount") == update_data["amount"]):
                        self.log_test("Update Debt", True, 
                                    f"Debt updated successfully")
                    else:
                        self.log_test("Update Debt", False, 
                                    f"Update not reflected: {debt}")
                else:
                    self.log_test("Update Debt", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test("Update Debt", False, f"Exception: {str(e)}")
                
        # Test Mark Debt as Paid
        if len(self.created_debt_ids) > 1:
            debt_id = self.created_debt_ids[1]
            try:
                response = requests.post(f"{self.base_url}/debts/{debt_id}/mark-paid", 
                                       headers=self.headers)
                
                if response.status_code == 200:
                    # Verify debt is marked as paid
                    verify_response = requests.get(f"{self.base_url}/debts/{debt_id}", 
                                                 headers=self.headers)
                    if verify_response.status_code == 200:
                        debt = verify_response.json()
                        if debt.get("status") == "paid":
                            self.log_test("Mark Debt as Paid", True, 
                                        f"Debt marked as paid successfully")
                        else:
                            self.log_test("Mark Debt as Paid", False, 
                                        f"Status not updated: {debt.get('status')}")
                    else:
                        self.log_test("Mark Debt as Paid", False, 
                                    f"Could not verify paid status")
                else:
                    self.log_test("Mark Debt as Paid", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test("Mark Debt as Paid", False, f"Exception: {str(e)}")
    
    def test_multi_currency_support(self):
        """Test multi-currency support and conversion"""
        print("=== Testing Multi-Currency Support ===")
        
        # Test currency conversion by creating debts in different currencies
        currencies = ["TRY", "USD", "EUR"]
        conversion_results = {}
        
        for currency in currencies:
            debt_data = {
                "debt_type": "i_owe",
                "person_name": f"Test Person {currency}",
                "amount": 100.0,
                "currency": currency,
                "description": f"Test debt in {currency}",
                "category": "other"
            }
            
            try:
                response = requests.post(f"{self.base_url}/debts", 
                                       json=debt_data, 
                                       headers=self.headers)
                
                if response.status_code == 200:
                    debt = response.json()
                    amount_in_try = debt.get("amount_in_try", 0)
                    conversion_results[currency] = amount_in_try
                    self.created_debt_ids.append(debt["id"])
                    
                    if currency == "TRY":
                        # TRY should be 1:1
                        if amount_in_try == 100.0:
                            self.log_test(f"Currency Conversion ({currency})", True, 
                                        f"TRY conversion correct: {amount_in_try}")
                        else:
                            self.log_test(f"Currency Conversion ({currency})", False, 
                                        f"TRY should be 1:1, got: {amount_in_try}")
                    else:
                        # USD and EUR should be converted
                        if amount_in_try > 100.0:
                            self.log_test(f"Currency Conversion ({currency})", True, 
                                        f"{currency} converted to TRY: {amount_in_try}")
                        else:
                            self.log_test(f"Currency Conversion ({currency})", False, 
                                        f"{currency} conversion seems incorrect: {amount_in_try}")
                else:
                    self.log_test(f"Currency Conversion ({currency})", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Currency Conversion ({currency})", False, f"Exception: {str(e)}")
        
        # Verify conversion rates are reasonable
        if "USD" in conversion_results and "EUR" in conversion_results and "TRY" in conversion_results:
            usd_rate = conversion_results["USD"] / 100.0
            eur_rate = conversion_results["EUR"] / 100.0
            
            if usd_rate > 20 and usd_rate < 50:  # Reasonable USD to TRY rate
                self.log_test("USD Exchange Rate Validation", True, 
                            f"USD rate appears reasonable: {usd_rate}")
            else:
                self.log_test("USD Exchange Rate Validation", False, 
                            f"USD rate seems unreasonable: {usd_rate}")
                
            if eur_rate > 30 and eur_rate < 60:  # Reasonable EUR to TRY rate
                self.log_test("EUR Exchange Rate Validation", True, 
                            f"EUR rate appears reasonable: {eur_rate}")
            else:
                self.log_test("EUR Exchange Rate Validation", False, 
                            f"EUR rate seems unreasonable: {eur_rate}")
    
    def test_dashboard_analytics(self):
        """Test dashboard analytics calculations"""
        print("=== Testing Dashboard Analytics ===")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=self.headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = [
                    "total_owed", "total_to_collect", "net_balance",
                    "active_debts_count", "overdue_debts_count"
                ]
                
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_test("Dashboard Stats Structure", True, 
                                f"All required fields present")
                    
                    # Validate data types and logic
                    if (isinstance(stats["total_owed"], (int, float)) and 
                        isinstance(stats["total_to_collect"], (int, float)) and
                        isinstance(stats["net_balance"], (int, float))):
                        
                        # Check if net balance calculation is correct
                        expected_net = stats["total_to_collect"] - stats["total_owed"]
                        if abs(stats["net_balance"] - expected_net) < 0.01:
                            self.log_test("Dashboard Net Balance Calculation", True, 
                                        f"Net balance correctly calculated: {stats['net_balance']}")
                        else:
                            self.log_test("Dashboard Net Balance Calculation", False, 
                                        f"Net balance incorrect: got {stats['net_balance']}, expected {expected_net}")
                        
                        self.log_test("Dashboard Data Types", True, 
                                    f"All numeric fields have correct types")
                    else:
                        self.log_test("Dashboard Data Types", False, 
                                    f"Incorrect data types in stats: {stats}")
                        
                    # Test analytics insights
                    if stats["active_debts_count"] >= 0:
                        self.log_test("Dashboard Active Debts Count", True, 
                                    f"Active debts count: {stats['active_debts_count']}")
                    else:
                        self.log_test("Dashboard Active Debts Count", False, 
                                    f"Invalid active debts count: {stats['active_debts_count']}")
                        
                    if stats["overdue_debts_count"] >= 0:
                        self.log_test("Dashboard Overdue Debts Count", True, 
                                    f"Overdue debts count: {stats['overdue_debts_count']}")
                    else:
                        self.log_test("Dashboard Overdue Debts Count", False, 
                                    f"Invalid overdue debts count: {stats['overdue_debts_count']}")
                        
                    # Test optional fields
                    if stats.get("person_owe_most"):
                        self.log_test("Dashboard Person Owe Most", True, 
                                    f"Person owe most: {stats['person_owe_most']} ({stats.get('person_owe_most_amount', 0)})")
                    
                    if stats.get("most_overdue_debt"):
                        self.log_test("Dashboard Most Overdue Debt", True, 
                                    f"Most overdue: {stats['most_overdue_debt']} ({stats.get('most_overdue_days', 0)} days)")
                        
                else:
                    self.log_test("Dashboard Stats Structure", False, 
                                f"Missing fields: {missing_fields}")
            else:
                self.log_test("Dashboard Analytics", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Dashboard Analytics", False, f"Exception: {str(e)}")
    
    def test_database_integration(self):
        """Test database models and MongoDB integration"""
        print("=== Testing Database Models and MongoDB Integration ===")
        
        # Test data persistence by creating, reading, and verifying data
        test_debt = {
            "debt_type": "i_owe",
            "person_name": "Database Test Person",
            "amount": 999.99,
            "currency": "TRY",
            "description": "Database integration test",
            "category": "other"
        }
        
        try:
            # Create debt
            create_response = requests.post(f"{self.base_url}/debts", 
                                          json=test_debt, 
                                          headers=self.headers)
            
            if create_response.status_code == 200:
                created_debt = create_response.json()
                debt_id = created_debt["id"]
                self.created_debt_ids.append(debt_id)
                
                # Verify data persistence by reading back
                read_response = requests.get(f"{self.base_url}/debts/{debt_id}", 
                                           headers=self.headers)
                
                if read_response.status_code == 200:
                    read_debt = read_response.json()
                    
                    # Verify all fields match
                    fields_match = all([
                        read_debt.get("person_name") == test_debt["person_name"],
                        read_debt.get("amount") == test_debt["amount"],
                        read_debt.get("currency") == test_debt["currency"],
                        read_debt.get("description") == test_debt["description"],
                        read_debt.get("category") == test_debt["category"]
                    ])
                    
                    if fields_match:
                        self.log_test("Database Data Persistence", True, 
                                    "Data correctly stored and retrieved")
                    else:
                        self.log_test("Database Data Persistence", False, 
                                    f"Data mismatch: created {test_debt}, read {read_debt}")
                        
                    # Verify UUID format
                    if len(debt_id) == 36 and debt_id.count('-') == 4:
                        self.log_test("Database UUID Generation", True, 
                                    f"Valid UUID format: {debt_id}")
                    else:
                        self.log_test("Database UUID Generation", False, 
                                    f"Invalid UUID format: {debt_id}")
                        
                    # Verify timestamps
                    if "created_at" in read_debt and "updated_at" in read_debt:
                        self.log_test("Database Timestamps", True, 
                                    "Timestamps present in data")
                    else:
                        self.log_test("Database Timestamps", False, 
                                    "Missing timestamps in data")
                else:
                    self.log_test("Database Data Persistence", False, 
                                f"Could not read back created debt: {read_response.status_code}")
            else:
                self.log_test("Database Data Persistence", False, 
                            f"Could not create test debt: {create_response.status_code}")
                
        except Exception as e:
            self.log_test("Database Integration", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("=== Testing Error Handling ===")
        
        # Test invalid debt creation
        invalid_debt = {
            "debt_type": "invalid_type",
            "person_name": "",
            "amount": -100,
            "currency": "INVALID",
            "description": "",
            "category": "invalid_category"
        }
        
        try:
            response = requests.post(f"{self.base_url}/debts", 
                                   json=invalid_debt, 
                                   headers=self.headers)
            
            if response.status_code == 422:
                self.log_test("Error Handling (Invalid Debt Data)", True, 
                            "Correctly rejected invalid debt data")
            else:
                self.log_test("Error Handling (Invalid Debt Data)", False, 
                            f"Should have returned 422, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling (Invalid Debt Data)", False, f"Exception: {str(e)}")
            
        # Test accessing non-existent debt
        try:
            response = requests.get(f"{self.base_url}/debts/non-existent-id", 
                                  headers=self.headers)
            
            if response.status_code == 404:
                self.log_test("Error Handling (Non-existent Debt)", True, 
                            "Correctly returned 404 for non-existent debt")
            else:
                self.log_test("Error Handling (Non-existent Debt)", False, 
                            f"Should have returned 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling (Non-existent Debt)", False, f"Exception: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("=== Cleaning Up Test Data ===")
        
        deleted_count = 0
        for debt_id in self.created_debt_ids:
            try:
                response = requests.delete(f"{self.base_url}/debts/{debt_id}", 
                                         headers=self.headers)
                if response.status_code == 200:
                    deleted_count += 1
            except:
                pass
                
        self.log_test("Test Data Cleanup", True, 
                    f"Cleaned up {deleted_count}/{len(self.created_debt_ids)} test debts")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing for Debt Tracking App")
        print("=" * 70)
        
        # Test authentication system
        self.test_user_registration()
        self.test_user_login()
        self.test_jwt_authentication()
        
        # Test debt operations
        self.test_debt_crud_operations()
        
        # Test multi-currency support
        self.test_multi_currency_support()
        
        # Test dashboard analytics
        self.test_dashboard_analytics()
        
        # Test database integration
        self.test_database_integration()
        
        # Test error handling
        self.test_error_handling()
        
        # Cleanup
        self.cleanup_test_data()
        
        print("=" * 70)
        print("✅ Backend testing completed!")

if __name__ == "__main__":
    tester = DebtTrackerTester()
    tester.run_all_tests()