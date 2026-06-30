import logging
from flask import Blueprint, request, jsonify
from services import PostGenerator, AIProviderError, NonRetryableAIProviderError, RetryableAIProviderError
from database import PostHelper, Post


logger = logging.getLogger(__name__)
generator_bp = Blueprint('generator', __name__)
post_generator = PostGenerator()


@generator_bp.route('/api/generate/post', methods=['POST'])
def generate_single_post():
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data['topic']
        title = data.get('title')
        project = data.get('project')
        audience = data.get('audience')
        tone = data.get('tone')
        domains = data.get('domains')
        hashtags = data.get('hashtags')
        character_limit = data.get('character_limit')
        
        logger.info(f"Generating post for topic: {topic}")
        post = post_generator.generate_single_post(
            topic=topic,
            title=title,
            project=project,
            audience=audience,
            tone=tone,
            domains=domains,
            hashtags=hashtags,
            character_limit=character_limit
        )
        
        logger.info(f"Generated post {post.id} successfully!")
        return jsonify({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'status': post.status.value,
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'linkedin_post_id': post.linkedin_post_id,
                'retry_count': post.retry_count,
                'last_error': post.last_error,
                'job_id': post.job_id,
                'created_at': post.created_at.isoformat()
            }
        }), 201
        
    except NonRetryableAIProviderError as e:
        logger.error(f"Non-retryable error generating post: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
    except RetryableAIProviderError as e:
        logger.error(f"Retryable error generating post (tried max retries): {e}", exc_info=True)
        return jsonify({'error': str(e)}), 503
    except AIProviderError as e:
        logger.error(f"AI provider error generating post: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error generating post: {e}", exc_info=True)
        return jsonify({'error': f'Failed to generate post: {str(e)}'}), 500


@generator_bp.route('/api/generate/batch', methods=['POST'])
def generate_batch_posts():
    try:
        data = request.get_json()
        
        if not data or 'topics' not in data or not isinstance(data['topics'], list):
            return jsonify({'error': 'List of topics is required'}), 400
        
        topics = data['topics']
        project = data.get('project')
        audience = data.get('audience')
        tone = data.get('tone')
        domains = data.get('domains')
        hashtags = data.get('hashtags')
        character_limit = data.get('character_limit')
        
        posts = post_generator.generate_batch_posts(
            topics=topics,
            project=project,
            audience=audience,
            tone=tone,
            domains=domains,
            hashtags=hashtags,
            character_limit=character_limit
        )
        
        return jsonify({
            'success': True,
            'count': len(posts),
            'posts': [
                {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'status': post.status.value,
                    'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                    'published_at': post.published_at.isoformat() if post.published_at else None,
                    'linkedin_post_id': post.linkedin_post_id,
                    'retry_count': post.retry_count,
                    'last_error': post.last_error,
                    'job_id': post.job_id,
                    'created_at': post.created_at.isoformat()
                }
                for post in posts
            ]
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate batch posts: {str(e)}'}), 500


@generator_bp.route('/api/posts', methods=['GET'])
def get_posts():
    posts = PostHelper.get_all(Post, Post.created_at.desc())
    return jsonify({
        'success': True,
        'posts': [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'status': post.status.value,
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'linkedin_post_id': post.linkedin_post_id,
                'retry_count': post.retry_count,
                'last_error': post.last_error,
                'job_id': post.job_id,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            }
            for post in posts
        ]
    }), 200
