#!/usr/bin/env python3

import requests
import json
import sys

def test_review_endpoints():
    """Test the review system endpoints"""
    base_url = "http://localhost:8000/api"
    
    print("Testing Review System Endpoints...")
    
    # Test 1: Get review queue (should work even if empty)
    try:
        response = requests.get(f"{base_url}/review-queue")
        print(f"✓ GET /review-queue: {response.status_code}")
        if response.status_code == 200:
            queue_data = response.json()
            print(f"  Queue items: {len(queue_data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ GET /review-queue failed: {e}")
    
    # Test 2: Get review statistics
    try:
        response = requests.get(f"{base_url}/statistics")
        print(f"✓ GET /statistics: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"  Total reviews: {stats.get('total_reviews', 0)}")
            print(f"  Pending reviews: {stats.get('pending_reviews', 0)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ GET /statistics failed: {e}")
    
    # Test 3: Queue low confidence cases
    try:
        response = requests.post(f"{base_url}/queue-low-confidence", params={
            "confidence_threshold": 70,
            "authenticity_threshold": 30
        })
        print(f"✓ POST /queue-low-confidence: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Queued: {result.get('total_queued', 0)} cases")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ POST /queue-low-confidence failed: {e}")
    
    # Test 4: Get updated queue after queueing
    try:
        response = requests.get(f"{base_url}/review-queue")
        print(f"✓ GET /review-queue (after queueing): {response.status_code}")
        if response.status_code == 200:
            queue_data = response.json()
            print(f"  Queue items after queueing: {len(queue_data)}")
            
            # If we have items, test reviewing one
            if queue_data:
                item = queue_data[0]
                review_id = item['review_id']
                
                # Test 5: Submit a review decision
                review_decision = {
                    "decision": "approve",
                    "notes": "Test approval from automated test"
                }
                
                try:
                    response = requests.put(f"{base_url}/review/{review_id}", json=review_decision)
                    print(f"✓ PUT /review/{review_id}: {response.status_code}")
                    if response.status_code == 200:
                        print("  Review decision submitted successfully")
                    else:
                        print(f"  Error: {response.text}")
                except Exception as e:
                    print(f"✗ PUT /review/{review_id} failed: {e}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ GET /review-queue (after queueing) failed: {e}")
    
    print("\nReview system test completed!")

if __name__ == "__main__":
    test_review_endpoints()