import pytest
from models import db, URL, Click
from utils import generate_short_code, encode_id, decode_short_code, validate_url, normalize_url, is_safe_url
import string

class TestUtilsFunctions:
    """Test utility functions"""
    
    def test_generate_short_code_default_length(self):
        """Test default short code generation"""
        code = generate_short_code()
        assert len(code) == 6
        assert all(c in string.ascii_letters + string.digits for c in code)
    
    def test_generate_short_code_custom_length(self):
        """Test custom length short code generation"""
        code = generate_short_code(10)
        assert len(code) == 10
    
    def test_encode_decode_id(self):
        """Test ID encoding and decoding"""
        test_ids = [0, 1, 100, 1000, 999999]
        
        for test_id in test_ids:
            encoded = encode_id(test_id)
            decoded = decode_short_code(encoded)
            assert decoded == test_id
    
    def test_validate_url_valid(self):
        """Test URL validation with valid URLs"""
        valid_urls = [
            'https://www.example.com',
            'http://example.com',
            'https://sub.domain.example.com/path?query=value',
            'www.example.com'  # Should be valid after normalization
        ]
        
        for url in valid_urls:
            assert validate_url(url) == True
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            '',
            '   ',
            'not-a-url',
            'ftp://example.com',  # FTP not supported by validators
            'javascript:alert("xss")'
        ]
        
        for url in invalid_urls:
            assert validate_url(url) == False
    
    def test_normalize_url(self):
        """Test URL normalization"""
        test_cases = [
            ('www.example.com', 'https://www.example.com'),
            ('example.com/path', 'https://example.com/path'),
            ('https://example.com', 'https://example.com'),
            ('http://example.com', 'http://example.com')
        ]
        
        for input_url, expected in test_cases:
            assert normalize_url(input_url) == expected
    
    def test_normalize_url_invalid(self):
        """Test URL normalization with invalid URLs"""
        with pytest.raises(ValueError):
            normalize_url('')
        
        with pytest.raises(ValueError):
            normalize_url('   ')
        
        with pytest.raises(ValueError):
            normalize_url('not-a-valid-url')
    
    def test_is_safe_url(self):
        """Test URL safety checks"""
        safe_urls = [
            'https://www.google.com',
            'https://example.com',
            'https://github.com/user/repo'
        ]
        
        unsafe_urls = [
            'https://localhost:8080',
            'http://127.0.0.1:3000',
            'https://192.168.1.1',
            'http://10.0.0.1'
        ]
        
        for url in safe_urls:
            assert is_safe_url(url) == True
        
        for url in unsafe_urls:
            assert is_safe_url(url) == False


class TestModels:
    """Test database models"""
    
    def test_url_model_creation(self, app):
        """Test URL model creation"""
        with app.app_context():
            url = URL(
                original_url='https://www.example.com',
                short_code='abc123'
            )
            
            db.session.add(url)
            db.session.commit()
            
            # Test retrieval
            retrieved = URL.query.filter_by(short_code='abc123').first()
            assert retrieved is not None
            assert retrieved.original_url == 'https://www.example.com'
            assert retrieved.short_code == 'abc123'
            assert retrieved.is_active == True
            assert retrieved.expires_at is None
    
    def test_url_model_to_dict(self, app):
        """Test URL model to_dict method"""
        with app.app_context():
            url = URL(
                original_url='https://www.example.com',
                short_code='abc123'
            )
            
            db.session.add(url)
            db.session.commit()
            
            url_dict = url.to_dict()
            
            assert 'id' in url_dict
            assert url_dict['original_url'] == 'https://www.example.com'
            assert url_dict['short_code'] == 'abc123'
            assert url_dict['short_url'] == 'http://localhost:5000/abc123'
            assert 'created_at' in url_dict
            assert url_dict['is_active'] == True
            assert url_dict['click_count'] == 0
    
    def test_url_model_expiration(self, app):
        """Test URL model expiration functionality"""
        with app.app_context():
            # Test non-expired URL
            future_time = datetime.utcnow() + timedelta(hours=1)
            url = URL(
                original_url='https://www.example.com',
                short_code='future',
                expires_at=future_time
            )
            assert url.is_expired() == False
            
            # Test expired URL
            past_time = datetime.utcnow() - timedelta(hours=1)
            expired_url = URL(
                original_url='https://www.example.com',
                short_code='expired',
                expires_at=past_time
            )
            assert expired_url.is_expired() == True
            
            # Test URL without expiration
            permanent_url = URL(
                original_url='https://www.example.com',
                short_code='permanent'
            )
            assert permanent_url.is_expired() == False
    
    def test_click_model_creation(self, app):
        """Test Click model creation"""
        with app.app_context():
            # Create URL first
            url = URL(
                original_url='https://www.example.com',
                short_code='test123'
            )
            db.session.add(url)
            db.session.commit()
            
            # Create click
            click = Click(
                url_id=url.id,
                ip_address='192.168.1.1',
                user_agent='Test Browser',
                referrer='https://google.com'
            )
            
            db.session.add(click)
            db.session.commit()
            
            # Test retrieval
            retrieved = Click.query.first()
            assert retrieved is not None
            assert retrieved.url_id == url.id
            assert retrieved.ip_address == '192.168.1.1'
            assert retrieved.user_agent == 'Test Browser'
            assert retrieved.referrer == 'https://google.com'
    
    def test_url_click_relationship(self, app):
        """Test URL-Click relationship"""
        with app.app_context():
            # Create URL
            url = URL(
                original_url='https://www.example.com',
                short_code='test123'
            )
            db.session.add(url)
            db.session.commit()
            
            # Create multiple clicks
            for i in range(3):
                click = Click(
                    url_id=url.id,
                    ip_address=f'192.168.1.{i}'
                )
                db.session.add(click)
            
            db.session.commit()
            
            # Test relationship
            assert url.clicks.count() == 3
            
            # Test backref
            click = Click.query.first()
            assert click.url.short_code == 'test123'