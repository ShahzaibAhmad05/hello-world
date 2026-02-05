import pytest
import json
import time
from models import db, URL, Click

class TestIntegration:
    """Integration tests for the complete URL shortener workflow"""
    
    def test_complete_url_shortener_workflow(self, client, app):
        """Test the complete workflow from creation to deletion"""
        with app.app_context():
            test_url = 'https://www.github.com/python/cpython'
            
            # Step 1: Shorten URL
            shorten_data = {'url': test_url}
            response = client.post('/shorten',
                                 data=json.dumps(shorten_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            short_code = data['data']['short_code']
            
            # Step 2: Use shortened URL (redirect)
            redirect_response = client.get(f'/{short_code}')
            assert redirect_response.status_code == 302
            assert redirect_response.location == test_url
            
            # Step 3: Check statistics
            stats_response = client.get(f'/stats/{short_code}')
            assert stats_response.status_code == 200
            
            stats_data = json.loads(stats_response.data)
            assert stats_data['statistics']['total_clicks'] == 1
            
            # Step 4: Multiple clicks
            for _ in range(3):
                client.get(f'/{short_code}')
            
            # Step 5: Check updated statistics
            stats_response = client.get(f'/stats/{short_code}')
            stats_data = json.loads(stats_response.data)
            assert stats_data['statistics']['total_clicks'] == 4
            
            # Step 6: List URLs
            list_response = client.get('/urls')
            assert list_response.status_code == 200
            
            list_data = json.loads(list_response.data)
            assert len(list_data['urls']) == 1
            assert list_data['urls'][0]['short_code'] == short_code
            
            # Step 7: Deactivate URL
            delete_response = client.delete(f'/urls/{short_code}')
            assert delete_response.status_code == 200
            
            # Step 8: Verify URL is no longer accessible
            final_redirect = client.get(f'/{short_code}')
            assert final_redirect.status_code == 404
    
    def test_concurrent_url_creation(self, client):
        """Test creating multiple URLs concurrently"""
        urls = [
            'https://www.google.com',
            'https://www.github.com',
            'https://www.stackoverflow.com',
            'https://www.reddit.com',
            'https://www.youtube.com'
        ]
        
        created_codes = []
        
        for url in urls:
            response = client.post('/shorten',
                                 data=json.dumps({'url': url}),
                                 content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            created_codes.append(data['data']['short_code'])
        
        # Ensure all codes are unique
        assert len(created_codes) == len(set(created_codes))
        
        # Test all redirects work
        for i, code in enumerate(created_codes):
            redirect_response = client.get(f'/{code}')
            assert redirect_response.status_code == 302
            assert redirect_response.location == urls[i]
    
    def test_url_with_expiration_workflow(self, client, app):
        """Test workflow with URL expiration"""
        with app.app_context():
            # Create URL with very short expiration for testing
            test_data = {
                'url': 'https://www.example.com/test',
                'expires_in_hours': -1  # Expired immediately for testing
            }
            
            response = client.post('/shorten',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            assert response.status_code == 201
            
            data = json.loads(response.data)
            short_code = data['data']['short_code']
            
            # Update URL to be expired (manipulate database for testing)
            from datetime import datetime, timedelta
            url_record = URL.query.filter_by(short_code=short_code).first()
            url_record.expires_at = datetime.utcnow() - timedelta(minutes=1)
            db.session.commit()
            
            # Try to redirect - should fail
            redirect_response = client.get(f'/{short_code}')
            assert redirect_response.status_code == 410
            
            data = json.loads(redirect_response.data)
            assert 'expired' in data['error'].lower()
    
    def test_analytics_accuracy(self, client, app):
        """Test the accuracy of analytics data"""
        with app.app_context():
            test_url = 'https://www.example.com/analytics-test'
            
            # Create URL
            response = client.post('/shorten',
                                 data=json.dumps({'url': test_url}),
                                 content_type='application/json')
            data = json.loads(response.data)
            short_code = data['data']['short_code']
            
            # Simulate clicks from different sources
            click_data = [
                {'User-Agent': 'Mozilla/5.0 Chrome', 'Referer': 'https://google.com'},
                {'User-Agent': 'Mozilla/5.0 Firefox', 'Referer': 'https://google.com'},
                {'User-Agent': 'Mozilla/5.0 Safari', 'Referer': 'https://twitter.com'},
                {'User-Agent': 'Mobile Browser', 'Referer': None}
            ]
            
            for click_info in click_data:
                headers = {k: v for k, v in click_info.items() if v is not None}
                client.get(f'/{short_code}', headers=headers)
            
            # Check analytics
            stats_response = client.get(f'/stats/{short_code}')
            stats_data = json.loads(stats_response.data)
            
            assert stats_data['statistics']['total_clicks'] == 4
            
            # Should have referrer data
            referrers = stats_data['statistics']['top_referrers']
            google_referrers = [r for r in referrers if 'google.com' in r['referrer']]
            assert len(google_referrers) > 0
            assert google_referrers[0]['count'] == 2  # Two clicks from Google
    
    def test_error_handling_workflow(self, client):
        """Test various error scenarios"""
        # Test invalid JSON
        response = client.post('/shorten',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test missing content type
        response = client.post('/shorten',
                             data=json.dumps({'url': 'https://example.com'}))
        assert response.status_code in [400, 415]  # Bad request or unsupported media type
        
        # Test non-existent endpoints
        response = client.get('/non-existent-endpoint')
        assert response.status_code == 404
        
        # Test wrong HTTP methods
        response = client.post('/health')
        assert response.status_code == 405
    
    def test_large_scale_operation(self, client, app):
        """Test handling of larger scale operations"""
        with app.app_context():
            # Create 50 URLs
            base_url = 'https://example.com/page-'
            created_urls = []
            
            for i in range(50):
                url = f'{base_url}{i}'
                response = client.post('/shorten',
                                     data=json.dumps({'url': url}),
                                     content_type='application/json')
                assert response.status_code == 201
                data = json.loads(response.data)
                created_urls.append(data['data']['short_code'])
            
            # Test pagination
            response = client.get('/urls?per_page=10')
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert len(data['urls']) == 10
            assert data['pagination']['total'] == 50
            assert data['pagination']['pages'] == 5
            
            # Test page 2
            response = client.get('/urls?page=2&per_page=10')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['urls']) == 10
            assert data['pagination']['page'] == 2
            
            # Random sampling: Test 10 random URLs work correctly
            import random
            sample_codes = random.sample(created_urls, 10)
            
            for code in sample_codes:
                response = client.get(f'/{code}')
                assert response.status_code == 302