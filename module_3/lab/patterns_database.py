"""Pattern Library: Database Models

Few-shot examples for creating database models with SQLAlchemy.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    Enum as SQLEnum, UniqueConstraint, Index, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


# Many-to-many association table for posts and tags
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_post_tags_post', 'post_id'),
    Index('idx_post_tags_tag', 'tag_id')
)


class PostStatus(enum.Enum):
    """Post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class User(Base):
    """
    User model - Example 1 from pattern library.
    
    Demonstrates: primary key, unique constraints, timestamps,
    relationships, and basic validation.
    """
    __tablename__ = 'users'

    # Primary key with auto-increment
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unique fields with constraints
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Encrypted password (store hash, not plain text)
    password_hash = Column(String(255), nullable=False)
    
    # Timestamps with auto-generation
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships with foreign key constraints
    posts = relationship('Post', back_populates='author', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Category(Base):
    """Category model for organizing posts."""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Relationships
    posts = relationship('Post', back_populates='category')
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Tag(Base):
    """Tag model for post tagging."""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    
    # Many-to-many relationship with posts
    posts = relationship('Post', secondary=post_tags, back_populates='tags')
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Post(Base):
    """
    Post model - Example 2 from pattern library.
    
    Demonstrates: multiple relationships, enums, URL-friendly slugs,
    status tracking, view counting, and complex indexing.
    """
    __tablename__ = 'posts'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Content fields
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Foreign keys with relationships
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'))
    
    # Status enumeration
    status = Column(SQLEnum(PostStatus), default=PostStatus.DRAFT, nullable=False, index=True)
    
    # Timestamps
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metrics
    view_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    author = relationship('User', back_populates='posts')
    category = relationship('Category', back_populates='posts')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    tags = relationship('Tag', secondary=post_tags, back_populates='posts')
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_posts_author_status', 'author_id', 'status'),
        Index('idx_posts_published_status', 'published_at', 'status'),
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', status='{self.status.value}')>"


class Comment(Base):
    """
    Comment model - Example 3 from pattern library.
    
    Demonstrates: self-referential relationships (nested comments),
    cascade delete, approval workflow, and optimized indexing.
    """
    __tablename__ = 'comments'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Self-referential for nested comments (replies)
    parent_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Moderation
    is_approved = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship('Post', back_populates='comments')
    user = relationship('User', back_populates='comments')
    parent = relationship('Comment', remote_side=[id], backref='replies')
    
    # Indexes for fast retrieval
    __table_args__ = (
        Index('idx_comments_post_approved', 'post_id', 'is_approved'),
        Index('idx_comments_user', 'user_id'),
        Index('idx_comments_parent', 'parent_id'),
    )
    
    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, post_id={self.post_id})>"


# Example usage demonstrating the patterns
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create in-memory SQLite database
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create user (Example 1 pattern)
        user = User(
            username='johndoe',
            email='john@example.com',
            password_hash='hashed_password_here',
            is_active=True
        )
        session.add(user)
        
        # Create category
        category = Category(
            name='Technology',
            slug='technology',
            description='Tech-related posts'
        )
        session.add(category)
        
        # Create tags
        tag1 = Tag(name='Python', slug='python')
        tag2 = Tag(name='Database', slug='database')
        session.add_all([tag1, tag2])
        
        session.commit()
        
        # Create post (Example 2 pattern)
        post = Post(
            title='Introduction to SQLAlchemy',
            slug='intro-to-sqlalchemy',
            content='SQLAlchemy is a powerful ORM...',
            author_id=user.id,
            category_id=category.id,
            status=PostStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            tags=[tag1, tag2]
        )
        session.add(post)
        session.commit()
        
        # Create comment (Example 3 pattern)
        comment = Comment(
            post_id=post.id,
            user_id=user.id,
            content='Great article!',
            is_approved=True
        )
        session.add(comment)
        
        # Create nested reply
        reply = Comment(
            post_id=post.id,
            user_id=user.id,
            parent_id=comment.id,
            content='Thanks for reading!',
            is_approved=True
        )
        session.add(reply)
        session.commit()
        
        # Query examples
        print("\n=== Query Results ===")
        print(f"User: {user}")
        print(f"User's posts: {len(user.posts)}")
        print(f"Post: {post}")
        print(f"Post tags: {[tag.name for tag in post.tags]}")
        print(f"Comments on post: {len(post.comments)}")
        print(f"Comment replies: {len(comment.replies)}")
        
    finally:
        session.close()
