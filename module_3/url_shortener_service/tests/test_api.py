import pytest
import json
from models import db, URL, Click
from datetime import datetime, timedelta

class TestAPI:
    """Test API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data
        assert 'version' in data
    
    def test_docs_endpoint(self, client):
        """Test API documentation endpoint"""
        response = client.get('/docs')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'title' in data
        assert 'endpoints' in data
        assert 'POST /shorten' in data['endpoints']
    
    def test_shorten_url_valid(self, client, sample_url_data):
        """Test URL shortening with valid URL"""
        response = client.post('/shorten',
                             data=json.dumps(sample_url_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['message'] == 'URL shortened successfully'
        assert 'data' in data
        
        url_data = data['data']
        assert 'short_code' in url_data
        assert 'short_url' in url_data
        assert url_data['original_url'] == sample_url_data['url']
        assert url_data['is_active'] == True
        assert url_data['click_count'] == 0
    
    def test_shorten_url_invalid(self, client):
        """Test URL shortening with invalid URL"""
        invalid_data = {'url': 'not-a-valid-url'}
        
        response = client.post('/shorten',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_shorten_url_missing_data(self, client):
        """Test URL shortening with missing data"""
        response = client.post('/shorten',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'URL is required'
    
    def test_shorten_url_unsafe(self, client):
        """Test URL shortening with unsafe URL"""
        unsafe_data = {'url': 'http://localhost:8080/admin'}
        
        response = client.post('/shorten',
                             data=json.dumps(unsafe_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'restricted address' in data['error']
    
    def test_shorten_url_with_expiration(self, client, sample_url_data):
        """Test URL shortening with expiration"""
        data_with_expiration = sample_url_data.copy()
        data_with_expiration['expires_in_hours'] = 24
        
        response = client.post('/shorten',
                             data=json.dumps(data_with_expiration),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['expires_at'] is not None
    
    def test_shorten_url_duplicate(self, client, sample_url_data):
        """Test URL shortening with duplicate URL"""
        # Create first URL
        response1 = client.post('/shorten',
                              data=json.dumps(sample_url_data),
                              content_type='application/json')
        assert response1.status_code == 201
        data1 = json.loads(response1.data)
        
        # Try to create same URL again
        response2 = client.post('/shorten',
                              data=json.dumps(sample_url_data),
                              content_type='application/json')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        
        # Should return existing URL
        assert data2['message'] == 'URL already exists'
        assert data1['data']['short_code'] == data2['data']['short_code']
    
    def test_redirect_valid_url(self, client, app, sample_url_data):
        """Test redirecting to valid URL"""
        with app.app_context():
            # Create URL first
            response = client.post('/shorten',
                                 data=json.dumps(sample_url_data),
                                 content_type='application/json')
            data = json.loads(response.data)
            short_code = data['data']['short_code']
            
            # Test redirect
            redirect_response = client.get(f'/{short_code}')
            assert redirect_response.status_code == 302
            assert redirect_response.location == sample_url_data['url']
            
            # Check click was tracked
            url_record = URL.query.filter_by(short_code=short_code).first()
            assert url_record.clicks.count() == 1
    
    def test_redirect_nonexistent_url(self, client):
        """Test redirecting to non-existent URL"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Short URL not found'
    
    def test_redirect_expired_url(self, client, app, sample_url_data):
        """Test redirecting to expired URL"""
        with app.app_context():
            # Create expired URL
            url = URL(
                original_url=sample_url_data['url'],
                short_code='expired123',
                expires_at=datetime.utcnow() - timedelta(hours=1)
            )
            db.session.add(url)
            db.session.commit()
            
            # Try to redirect
            response = client.get('/expired123')
            assert response.status_code == 410
            
            data = json.loads(response.data)
            assert data['error'] == 'Short URL has expired'
    
    def test_get_url_stats(self, client, app, sample_url_data):
        """Test getting URL statistics"""
        with app.app_context():
            # Create URL and clicks
            response = client.post('/shorten',
                                 data=json.dumps(sample_url_data),
                                 content_type='application/json')
            data = json.loads(response.data)
            short_code = data['data']['short_code']
            
            # Create some clicks
            url_record = URL.query.filter_by(short_code=short_code).first()
            for i in range(3):
                click = Click(
                    url_id=url_record.id,
                    ip_address=f'192.168.1.{i}',
                    user_agent=f'Browser {i}',
                    referrer='https://google.com' if i % 2 == 0 else None
                )
                db.session.add(click)
            db.session.commit()
            
            # Get stats
            stats_response = client.get(f'/stats/{short_code}')
            assert stats_response.status_code == 200
            
            stats_data = json.loads(stats_response.data)
            assert 'url' in stats_data
            assert 'statistics' in stats_data
            
            stats = stats_data['statistics']
            assert stats['total_clicks'] == 3
            assert 'daily_stats' in stats
            assert 'top_referrers' in stats
    
    def test_get_url_stats_nonexistent(self, client):
        """Test getting stats for non-existent URL"""
        response = client.get('/stats/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Short URL not found'
    
    def test_list_urls(self, client, app):
        """Test listing URLs with pagination"""
        with app.app_context():
            # Create multiple URLs
            for i in range(5):
                url = URL(
                    original_url=f'https://example{i}.com',
                    short_code=f'test{i:03d}'
                )
                db.session.add(url)
            db.session.commit()
            
            # Test default pagination
            response = client.get('/urls')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'urls' in data
            assert 'pagination' in data
            assert len(data['urls']) == 5
            
            # Test custom pagination
            response = client.get('/urls?page=1&per_page=2')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data['urls']) == 2
            assert data['pagination']['per_page'] == 2
            assert data['pagination']['total'] == 5
    
    def test_delete_url(self, client, app, sample_url_data):
        """Test soft deleting a URL"""
        with app.app_context():
            # Create URL
            response = client.post('/shorten',
                                 data=json.dumps(sample_url_data),
                                 content_type='application/json')
            data = json.loads(response.data)
            short_code = data['data']['short_code']
            
            # Delete URL
            delete_response = client.delete(f'/urls/{short_code}')
            assert delete_response.status_code == 200
            
            delete_data = json.loads(delete_response.data)
            assert delete_data['message'] == 'URL deactivated successfully'
            
            # Verify URL is deactivated
            url_record = URL.query.filter_by(short_code=short_code).first()
            assert url_record.is_active == False
            
            # Should not be able to redirect
            redirect_response = client.get(f'/{short_code}')
            assert redirect_response.status_code == 404
    
    def test_delete_nonexistent_url(self, client):
        """Test deleting non-existent URL"""
        response = client.delete('/urls/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Short URL not found'