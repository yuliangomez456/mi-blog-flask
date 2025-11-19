from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import Post, User, Comment, Category, Tag, post_likes
from app.forms import PostForm, CommentForm, LoginForm, RegistrationForm, CategoryForm, TagForm
from slugify import slugify

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
admin = Blueprint('admin', __name__)

# ===== RUTAS PÚBLICAS =====
@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(published=True)\
                     .order_by(Post.created_at.desc())\
                     .paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)

@main.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        posts = Post.query.filter(
            Post.published == True,
            (Post.title.ilike(f'%{query}%') | Post.content.ilike(f'%{query}%') | Post.excerpt.ilike(f'%{query}%'))
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    else:
        posts = Post.query.filter_by(published=True)\
                         .order_by(Post.created_at.desc())\
                         .paginate(page=page, per_page=5)
    
    return render_template('search.html', posts=posts, query=query, title=f"Búsqueda: {query}")

@main.route('/post/<string:slug>', methods=['GET', 'POST'])
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not post.published and (not current_user.is_authenticated or not current_user.is_admin):
        abort(404)
    
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para comentar.', 'warning')
            return redirect(url_for('auth.login'))
        
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('¡Comentario publicado!', 'success')
        return redirect(url_for('main.post', slug=slug))
    
    comments = Comment.query.filter_by(post_id=post.id, approved=True)\
                          .order_by(Comment.created_at.asc()).all()
    
    # Obtener posts anterior y siguiente para navegación
    prev_post = Post.query.filter(
        Post.created_at < post.created_at, 
        Post.published == True
    ).order_by(Post.created_at.desc()).first()
    
    next_post = Post.query.filter(
        Post.created_at > post.created_at, 
        Post.published == True
    ).order_by(Post.created_at.asc()).first()
    
    # Información de likes para el usuario actual
    user_has_liked = current_user.is_authenticated and current_user.has_liked_post(post)
    user_has_favorited = current_user.is_authenticated and current_user.has_favorited_post(post)
    
    return render_template('post.html', 
                         post=post, 
                         form=form, 
                         comments=comments,
                         prev_post=prev_post,
                         next_post=next_post,
                         user_has_liked=user_has_liked,
                         user_has_favorited=user_has_favorited)

@main.route('/category/<string:slug>')
def category_posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(published=True, category_id=category.id)\
                     .order_by(Post.created_at.desc())\
                     .paginate(page=page, per_page=5)
    return render_template('category.html', category=category, posts=posts)

@main.route('/tag/<string:slug>')
def tag_posts(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.published == True, Post.tags.any(id=tag.id))\
                     .order_by(Post.created_at.desc())\
                     .paginate(page=page, per_page=5)
    return render_template('tag.html', tag=tag, posts=posts)

# ===== RUTAS DE LIKES Y FAVORITOS =====
@main.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.has_liked_post(post):
        # Quitar like
        current_user.liked_posts.remove(post)
        action = 'quitado like'
    else:
        # Dar like
        current_user.liked_posts.append(post)
        action = 'dado like'
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'likes_count': post.likes_count,
            'action': action
        })
    
    flash(f'Has {action} al post', 'success')
    return redirect(url_for('main.post', slug=post.slug))

@main.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if current_user.has_liked_comment(comment):
        # Quitar like
        current_user.liked_comments.remove(comment)
        action = 'quitado like'
    else:
        # Dar like
        current_user.liked_comments.append(comment)
        action = 'dado like'
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'likes_count': comment.likes_count,
            'action': action
        })
    
    flash(f'Has {action} al comentario', 'success')
    return redirect(url_for('main.post', slug=comment.post.slug))

@main.route('/post/<int:post_id>/favorite', methods=['POST'])
@login_required
def favorite_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.has_favorited_post(post):
        # Quitar de favoritos
        current_user.favorite_posts.remove(post)
        action = 'quitado de favoritos'
    else:
        # Añadir a favoritos
        current_user.favorite_posts.append(post)
        action = 'añadido a favoritos'
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'favorites_count': post.favorites_count,
            'action': action
        })
    
    flash(f'Has {action}', 'success')
    return redirect(url_for('main.post', slug=post.slug))

@main.route('/user/favorites')
@login_required
def user_favorites():
    page = request.args.get('page', 1, type=int)
    favorites = current_user.favorite_posts
    posts = Post.query.filter(Post.id.in_([post.id for post in favorites]))\
                     .filter_by(published=True)\
                     .order_by(Post.created_at.desc())\
                     .paginate(page=page, per_page=10)
    return render_template('favorites.html', posts=posts)

@main.route('/popular')
def popular_posts():
    page = request.args.get('page', 1, type=int)
    
    # Obtener posts populares (ordenados por número de likes)
    posts = Post.query.filter_by(published=True)\
                     .outerjoin(post_likes)\
                     .group_by(Post.id)\
                     .order_by(db.func.count(post_likes.c.post_id).desc())\
                     .paginate(page=page, per_page=10)
    
    return render_template('popular.html', posts=posts)

# ===== RUTAS DE AUTENTICACIÓN =====
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('¡Has iniciado sesión correctamente!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Correo o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('main.index'))

# ===== RUTAS DE ADMINISTRACIÓN =====
@admin.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    stats = {
        'total_posts': Post.query.count(),
        'published_posts': Post.query.filter_by(published=True).count(),
        'total_comments': Comment.query.count(),
        'pending_comments': Comment.query.filter_by(approved=False).count(),
        'total_users': User.query.count(),
        'total_categories': Category.query.count(),
        'total_tags': Tag.query.count()
    }
    
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_posts=recent_posts, 
                         recent_comments=recent_comments)

@admin.route('/admin/posts')
@login_required
def admin_posts():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/posts.html', posts=posts)

@admin.route('/admin/comments')
@login_required
def admin_comments():
    if not current_user.is_admin:
        abort(403)
    
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)

@admin.route('/admin/comment/<int:comment_id>/toggle', methods=['POST'])
@login_required
def toggle_comment(comment_id):
    if not current_user.is_admin:
        abort(403)
    
    comment = Comment.query.get_or_404(comment_id)
    comment.approved = not comment.approved
    db.session.commit()
    
    status = "aprobado" if comment.approved else "rechazado"
    flash(f'¡Comentario {status}!', 'success')
    return redirect(url_for('admin.admin_comments'))

@admin.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    if not current_user.is_admin:
        abort(403)
    
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('¡Comentario eliminado!', 'success')
    return redirect(url_for('admin.admin_comments'))

@admin.route('/admin/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if not current_user.is_admin:
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        base_slug = slugify(form.title.data)
        slug = base_slug
        counter = 1
        while Post.query.filter_by(slug=slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        post = Post(
            title=form.title.data,
            excerpt=form.excerpt.data,
            content=form.content.data,
            published=form.published.data,
            slug=slug,
            user_id=current_user.id,
            category_id=form.category.data if form.category.data != 0 else None
        )
        
        # Añadir etiquetas seleccionadas
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        post.tags = selected_tags
        
        db.session.add(post)
        db.session.commit()
        flash('¡Post creado exitosamente!', 'success')
        return redirect(url_for('admin.admin_posts'))
    
    return render_template('admin/post_form.html', form=form, title='Nuevo Post')

@admin.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.is_admin:
        abort(403)
    
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.excerpt = form.excerpt.data
        post.content = form.content.data
        post.published = form.published.data
        post.category_id = form.category.data if form.category.data != 0 else None
        
        # Actualizar etiquetas
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        post.tags = selected_tags
        
        new_slug = slugify(form.title.data)
        if new_slug != post.slug:
            base_slug = new_slug
            counter = 1
            while Post.query.filter(Post.slug == base_slug, Post.id != post.id).first() is not None:
                base_slug = f"{new_slug}-{counter}"
                counter += 1
            post.slug = base_slug
        
        db.session.commit()
        flash('¡Post actualizado exitosamente!', 'success')
        return redirect(url_for('admin.admin_posts'))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.excerpt.data = post.excerpt
        form.content.data = post.content
        form.published.data = post.published
        form.category.data = post.category_id if post.category_id else 0
        form.tags.data = [tag.id for tag in post.tags]
    
    return render_template('admin/post_form.html', form=form, title='Editar Post', post=post)

@admin.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        abort(403)
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('¡Post eliminado exitosamente!', 'success')
    return redirect(url_for('admin.admin_posts'))

@admin.route('/admin/post/<int:post_id>/toggle-publish', methods=['POST'])
@login_required
def toggle_publish(post_id):
    if not current_user.is_admin:
        abort(403)
    
    post = Post.query.get_or_404(post_id)
    post.published = not post.published
    db.session.commit()
    status = "publicado" if post.published else "oculto"
    flash(f'¡Post {status} exitosamente!', 'success')
    return redirect(url_for('admin.admin_posts'))

# ===== RUTAS DE CATEGORÍAS =====
@admin.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def admin_categories():
    if not current_user.is_admin:
        abort(403)
    
    form = CategoryForm()
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        
        category = Category(
            name=form.name.data,
            slug=slug,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('¡Categoría creada exitosamente!', 'success')
        return redirect(url_for('admin.admin_categories'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', form=form, categories=categories)

@admin.route('/admin/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        abort(403)
    
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('¡Categoría eliminada!', 'success')
    return redirect(url_for('admin.admin_categories'))

# ===== RUTAS DE ETIQUETAS =====
@admin.route('/admin/tags', methods=['GET', 'POST'])
@login_required
def admin_tags():
    if not current_user.is_admin:
        abort(403)
    
    form = TagForm()
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        
        tag = Tag(
            name=form.name.data,
            slug=slug
        )
        db.session.add(tag)
        db.session.commit()
        flash('¡Etiqueta creada exitosamente!', 'success')
        return redirect(url_for('admin.admin_tags'))
    
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tags.html', form=form, tags=tags)

@admin.route('/admin/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    if not current_user.is_admin:
        abort(403)
    
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('¡Etiqueta eliminada!', 'success')
    return redirect(url_for('admin.admin_tags'))