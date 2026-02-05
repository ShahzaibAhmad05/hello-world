from flask import Blueprint, request, jsonify, redirect, current_app
from sqlalchemy import func
from models import db, URL, Click
from utils import generate_short_code, normalize_url, is_safe_url, get_domain_from_url
from datetime import datetime, timedelta
import validators

api = Blueprint('api', __name__)

@api.route('/shorten', methods=['POST'])
def shorten_url():
    """Create a short URL from original URL"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        original_url = data['url']
        
        # Validate and normalize URL
        try:
            original_url = normalize_url(original_url)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Check if URL is safe
        if not is_safe_url(original_url):
            return jsonify({'error': 'URL points to restricted address'}), 400
        
        # Check URL length
        if len(original_url) > current_app.config.get('MAX_URL_LENGTH', 2048):
            return jsonify({'error': 'URL too long'}), 400
        
        # Check if URL already exists
        existing_url = URL.query.filter_by(original_url=original_url, is_active=True).first()
        if existing_url:
            return jsonify({
                'message': 'URL already exists',
                'data': existing_url.to_dict()
            }), 200
        
        # Generate unique short code
        short_code_length = current_app.config.get('SHORT_CODE_LENGTH', 6)
        max_attempts = 100
        
        for attempt in range(max_attempts):
            short_code = generate_short_code(short_code_length)
            
            # Check if short code already exists
            if not URL.query.filter_by(short_code=short_code).first():
                break
        else:
            return jsonify({'error': 'Failed to generate unique short code'}), 500
        
        # Handle optional expiration
        expires_at = None
        if 'expires_in_hours' in data:
            try:
                hours = int(data['expires_in_hours'])
                if hours > 0:
                    expires_at = datetime.utcnow() + timedelta(hours=hours)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid expiration time'}), 400
        
        # Create new URL record
        new_url = URL(
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at
        )
        
        db.session.add(new_url)
        db.session.commit()
        
        return jsonify({
            'message': 'URL shortened successfully',
            'data': new_url.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error shortening URL: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/<string:short_code>', methods=['GET'])
def redirect_url(short_code):
    """Redirect to original URL and track click"""
    try:
        # Find URL by short code
        url_record = URL.query.filter_by(short_code=short_code, is_active=True).first()
        
        if not url_record:
            return jsonify({'error': 'Short URL not found'}), 404
        
        # Check if URL has expired
        if url_record.is_expired():
            return jsonify({'error': 'Short URL has expired'}), 410
        
        # Track the click
        click = Click(
            url_id=url_record.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.headers.get('Referer')
        )
        
        db.session.add(click)
        db.session.commit()
        
        # Redirect to original URL
        return redirect(url_record.original_url, code=302)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error redirecting URL: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/stats/<string:short_code>', methods=['GET'])
def get_url_stats(short_code):
    """Get statistics for a short URL"""
    try:
        # Find URL by short code
        url_record = URL.query.filter_by(short_code=short_code).first()
        
        if not url_record:
            return jsonify({'error': 'Short URL not found'}), 404
        
        # Get click statistics
        total_clicks = url_record.clicks.count()
        
        # Get clicks by day (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clicks = url_record.clicks.filter(Click.clicked_at >= thirty_days_ago)
        
        # Group clicks by date
        daily_stats = db.session.query(
            func.date(Click.clicked_at).label('date'),
            func.count(Click.id).label('clicks')
        ).filter(
            Click.url_id == url_record.id,
            Click.clicked_at >= thirty_days_ago
        ).group_by(func.date(Click.clicked_at)).all()
        
        # Get top referrers
        referrer_stats = db.session.query(
            Click.referrer,
            func.count(Click.id).label('count')
        ).filter(
            Click.url_id == url_record.id,
            Click.referrer.isnot(None),
            Click.referrer != ''
        ).group_by(Click.referrer).order_by(func.count(Click.id).desc()).limit(10).all()
        
        # Prepare response data
        stats_data = {
            'url': url_record.to_dict(),
            'statistics': {
                'total_clicks': total_clicks,
                'clicks_last_30_days': recent_clicks.count(),
                'daily_stats': [
                    {'date': str(stat.date), 'clicks': stat.clicks}
                    for stat in daily_stats
                ],
                'top_referrers': [
                    {'referrer': stat.referrer, 'count': stat.count}
                    for stat in referrer_stats
                ],
                'created_at': url_record.created_at.isoformat(),
                'is_expired': url_record.is_expired()
            }
        }
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting URL stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/urls', methods=['GET'])
def list_urls():
    """List all URLs with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        urls = URL.query.filter_by(is_active=True).order_by(URL.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'urls': [url.to_dict() for url in urls.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': urls.total,
                'pages': urls.pages,
                'has_next': urls.has_next,
                'has_prev': urls.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing URLs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/urls/<string:short_code>', methods=['DELETE'])
def delete_url(short_code):
    """Soft delete a URL (deactivate it)"""
    try:
        url_record = URL.query.filter_by(short_code=short_code, is_active=True).first()
        
        if not url_record:
            return jsonify({'error': 'Short URL not found'}), 404
        
        url_record.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'URL deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting URL: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500