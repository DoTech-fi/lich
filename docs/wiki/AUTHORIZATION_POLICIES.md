# 🔐 Authorization Policies - Complete Guide

> **کنترل دسترسی: چه کسی می‌تونه چه کاری رو انجام بده**

---

## 📚 مفاهیم پایه

### Policy چیست؟
یه کلاس که تعیین می‌کنه یه User می‌تونه روی یه Resource چه کارهایی انجام بده.

```python
class PostPolicy:
    def can_view(self, user, post) -> bool: ...
    def can_edit(self, user, post) -> bool: ...
    def can_delete(self, user, post) -> bool: ...
```

---

## 🛠️ چطور بسازیم؟

```bash
lich make policy Post
```

```python
# backend/internal/policies/post_policy.py
class PostPolicy:
    """
    Authorization policy for Post resource.
    """
    
    def can_view(self, user, post) -> bool:
        """Anyone can view published posts."""
        return post.is_published or self.is_owner(user, post)
    
    def can_create(self, user) -> bool:
        """Any authenticated user can create."""
        return user is not None
    
    def can_edit(self, user, post) -> bool:
        """Only owner or admin can edit."""
        return self.is_owner(user, post) or self.is_admin(user)
    
    def can_delete(self, user, post) -> bool:
        """Only owner or admin can delete."""
        return self.can_edit(user, post)
    
    # Helper methods
    def is_owner(self, user, post) -> bool:
        return user and user.id == post.author_id
    
    def is_admin(self, user) -> bool:
        return user and user.role == "admin"
```

---

## 🎬 استفاده در API

### روش 1: Direct Usage

```python
# backend/api/http/posts.py
from internal.policies.post_policy import PostPolicy

@router.put("/{post_id}")
async def update_post(
    post_id: UUID,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    post = await post_service.get_by_id(post_id)
    
    # Check authorization
    if not PostPolicy().can_edit(current_user, post):
        raise HTTPException(403, "Not allowed to edit this post")
    
    return await post_service.update(post_id, data)
```

### روش 2: با Dependency

```python
# backend/api/deps/auth.py
from functools import wraps

def authorize(policy_class, action: str):
    """Decorator for authorization."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            resource = kwargs.get("resource")
            
            policy = policy_class()
            check_method = getattr(policy, f"can_{action}")
            
            if not check_method(user, resource):
                raise HTTPException(403, f"Not allowed to {action}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

```python
# Usage
@router.delete("/{post_id}")
@authorize(PostPolicy, "delete")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    resource: Post = Depends(get_post),
):
    ...
```

---

## 🎯 سناریوهای واقعی

### Scenario 1: Blog Platform

```bash
lich make policy Post
lich make policy Comment
```

```python
class PostPolicy:
    def can_view(self, user, post):
        # Published posts are public
        return post.is_published or self.is_owner(user, post)
    
    def can_edit(self, user, post):
        # Only author can edit
        return self.is_owner(user, post)
    
    def can_delete(self, user, post):
        # Author or admin
        return self.is_owner(user, post) or self.is_admin(user)

class CommentPolicy:
    def can_create(self, user, post):
        # Anyone can comment on published posts
        return post.is_published and user is not None
    
    def can_delete(self, user, comment):
        # Comment author, post author, or admin
        return (
            user.id == comment.author_id or
            user.id == comment.post.author_id or
            user.role == "admin"
        )
```

---

### Scenario 2: E-commerce

```bash
lich make policy Order
lich make policy Product
lich make policy Review
```

```python
class OrderPolicy:
    def can_view(self, user, order):
        # Only order owner or admin
        return user.id == order.customer_id or user.role == "admin"
    
    def can_cancel(self, user, order):
        # Only if pending and owner
        return (
            user.id == order.customer_id and
            order.status == "pending"
        )

class ProductPolicy:
    def can_view(self, user, product):
        return True  # Public
    
    def can_edit(self, user, product):
        # Only admin or vendor owner
        return user.role == "admin" or user.id == product.vendor_id

class ReviewPolicy:
    def can_create(self, user, product):
        # Only if user bought the product
        return user.has_purchased(product.id)
    
    def can_edit(self, user, review):
        # Only review author
        return user.id == review.author_id
```

---

### Scenario 3: Team Collaboration

```bash
lich make policy Workspace
lich make policy Project
lich make policy Task
```

```python
class WorkspacePolicy:
    def can_view(self, user, workspace):
        return user in workspace.members
    
    def can_edit(self, user, workspace):
        return user.id == workspace.owner_id
    
    def can_invite(self, user, workspace):
        return user.role in ["owner", "admin"]

class ProjectPolicy:
    def can_view(self, user, project):
        return user in project.workspace.members
    
    def can_edit(self, user, project):
        return user in project.editors or user.role == "admin"

class TaskPolicy:
    def can_view(self, user, task):
        return ProjectPolicy().can_view(user, task.project)
    
    def can_complete(self, user, task):
        return user.id == task.assignee_id or user.role == "admin"
```

---

## 🧩 Role-Based Access Control (RBAC)

```python
# Roles
ROLES = {
    "admin": ["view", "create", "edit", "delete", "manage"],
    "editor": ["view", "create", "edit"],
    "viewer": ["view"],
}

class RBACPolicy:
    def has_permission(self, user, permission: str) -> bool:
        if user is None:
            return False
        return permission in ROLES.get(user.role, [])

class PostPolicy(RBACPolicy):
    def can_view(self, user, post):
        return self.has_permission(user, "view")
    
    def can_edit(self, user, post):
        return self.has_permission(user, "edit")
```

---

## 🔗 Policy Chaining

```python
class OrderPolicy:
    def can_refund(self, user, order):
        # Must be able to view AND have refund permission
        return (
            self.can_view(user, order) and
            user.has_permission("refund") and
            order.is_refundable
        )
```

---

## 🧪 تست نوشتن

```python
import pytest
from internal.policies.post_policy import PostPolicy

class TestPostPolicy:
    def setup_method(self):
        self.policy = PostPolicy()
    
    def test_owner_can_edit(self):
        user = MockUser(id=1)
        post = MockPost(author_id=1)
        
        assert self.policy.can_edit(user, post) is True
    
    def test_stranger_cannot_edit(self):
        user = MockUser(id=2)
        post = MockPost(author_id=1)
        
        assert self.policy.can_edit(user, post) is False
    
    def test_admin_can_edit_any(self):
        admin = MockUser(id=99, role="admin")
        post = MockPost(author_id=1)
        
        assert self.policy.can_edit(admin, post) is True
```

---

## ✅ Best Practices

### 1. Policy های کوچیک و Focused

```python
# ❌ Bad - One policy for everything
class GodPolicy:
    def can_do_everything(self, user, anything):
        ...

# ✅ Good - Separate policies
class PostPolicy: ...
class CommentPolicy: ...
class UserPolicy: ...
```

### 2. DRY با Base Policy

```python
class BasePolicy:
    def is_admin(self, user) -> bool:
        return user and user.role == "admin"
    
    def is_owner(self, user, resource) -> bool:
        owner_id = getattr(resource, 'owner_id', None)
        return user and user.id == owner_id

class PostPolicy(BasePolicy):
    def can_edit(self, user, post):
        return self.is_owner(user, post) or self.is_admin(user)
```

### 3. Explicit over Implicit

```python
# ❌ Bad - implicit deny
def can_edit(self, user, post):
    if user.role == "admin":
        return True
    # Implicitly returns None (falsy)

# ✅ Good - explicit deny
def can_edit(self, user, post):
    if user.role == "admin":
        return True
    if user.id == post.author_id:
        return True
    return False  # Explicit deny
```

---

## 📋 Cheat Sheet

```bash
# Make policy
lich make policy Post

# Methods to implement
can_view(user, resource) -> bool
can_create(user) -> bool
can_edit(user, resource) -> bool
can_delete(user, resource) -> bool

# Usage in API
if not PostPolicy().can_edit(user, post):
    raise HTTPException(403)
```

---

**حالا برو Authorization بزن! 🔐**
