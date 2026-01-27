#!/usr/bin/env python3

import requests
import json
import time

def test_complete_age_verification_flow():
    print("🧪 Testing Complete Age Verification Flow")
    print("=" * 60)
    
    url = "http://localhost:8000/graphql/"
    
    try:
        # Step 1: Start basket
        print("1️⃣ Starting basket...")
        start_basket = """
        mutation {
          startBasket(employeeId: 1, terminalId: "test-terminal") {
            basketId
            status
          }
        }
        """
        
        response = requests.post(url, json={'query': start_basket})
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ Error starting basket: {data['errors']}")
            return
            
        basket_id = data['data']['startBasket']['basketId']
        print(f"✅ Basket started: {basket_id}")
        
        # Step 2: Add age-restricted item
        print("\\n2️⃣ Adding age-restricted item (WINE-001)...")
        add_item = f'''
        mutation {{
          addItem(
            basketId: "{basket_id}"
            productId: "WINE-001"
            productName: "Red Wine Bottle"
            quantity: 1
            price: 25.99
          ) {{
            id
            productName
            quantity
          }}
        }}
        '''
        
        response = requests.post(url, json={'query': add_item})
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ Error adding item: {data['errors']}")
            return
            
        item = data['data']['addItem']
        print(f"✅ Item response: {item}")
        
        if item['id'].startswith('temp_'):
            print("✅ Temporary item returned - age verification triggered!")
        else:
            print("❌ Regular item returned - age verification NOT triggered!")
            return
        
        print("\\n⏳ Waiting 2 seconds for Kafka processing...")
        time.sleep(2)
        
        # Step 3: Verify age
        print("\\n3️⃣ Verifying customer age...")
        verify_age = f'''
        mutation {{
          verifyAge(
            basketId: "{basket_id}"
            verifierEmployeeId: 1
            customerAge: 25
            verificationMethod: "ID_CHECK"
          )
        }}
        '''
        
        response = requests.post(url, json={'query': verify_age})
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ Error verifying age: {data['errors']}")
            return
            
        verified = data['data']['verifyAge']
        print(f"✅ Age verification result: {verified}")
        
        print("\\n⏳ Waiting 2 seconds for Kafka processing...")
        time.sleep(2)
        
        # Step 4: Add verified item
        print("\\n4️⃣ Adding verified item to basket...")
        add_verified = f'''
        mutation {{
          addVerifiedItem(
            basketId: "{basket_id}"
            productId: "WINE-001"
            productName: "Red Wine Bottle"
            quantity: 1
            price: 25.99
          ) {{
            id
            productName
            quantity
          }}
        }}
        '''
        
        response = requests.post(url, json={'query': add_verified})
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ Error adding verified item: {data['errors']}")
            return
            
        verified_item = data['data']['addVerifiedItem']
        print(f"✅ Verified item added: {verified_item}")
        
        # Step 5: Check basket contents
        print("\\n5️⃣ Checking final basket contents...")
        get_basket = f'''
        query {{
          basket(basketId: "{basket_id}") {{
            basketId
            status
            items {{
              id
              productName
              quantity
              price
            }}
          }}
        }}
        '''
        
        response = requests.post(url, json={'query': get_basket})
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ Error getting basket: {data['errors']}")
        else:
            basket = data['data']['basket']
            print(f"✅ Final basket: {basket}")
            
        print("\\n🎉 Age verification flow completed!")
        print("\\n📋 Summary:")
        print("  ✅ Basket created")
        print("  ✅ Age-restricted item triggered verification")
        print("  ✅ Age verification completed")
        print("  ✅ Verified item added to basket")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server. Make sure it's running!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_complete_age_verification_flow()