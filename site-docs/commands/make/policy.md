# lich make policy

Create authorization policies for access control.

## What is a Policy?

**Policies** define who can do what:

- `UserPolicy.can_edit(user, target_user)`
- `OrderPolicy.can_cancel(user, order)`
- `DocumentPolicy.can_view(user, document)`

## Usage

```bash
lich make policy <Name>
```

## Example

```bash
$ lich make policy Article

✅ Policy ArticlePolicy created!

Files created:
  backend/internal/policies/article_policy.py
```

## Generated Code

```python
"""
Article authorization policy.
"""
from internal.entities.user import User
from internal.entities.article import Article


class ArticlePolicy:
    """
    Authorization policy for Article.
    
    Methods return True if action is allowed.
    """
    
    def can_view(self, user: User, article: Article) -> bool:
        """Can user view this article?"""
        if article.is_public:
            return True
        return article.author_id == user.id
    
    def can_edit(self, user: User, article: Article) -> bool:
        """Can user edit this article?"""
        return article.author_id == user.id or user.is_admin
    
    def can_delete(self, user: User, article: Article) -> bool:
        """Can user delete this article?"""
        return article.author_id == user.id or user.is_admin
    
    def can_publish(self, user: User, article: Article) -> bool:
        """Can user publish this article?"""
        return article.author_id == user.id
```

## Use in API

```python
from internal.policies.article_policy import ArticlePolicy

@router.put("/{id}")
async def update_article(id: UUID, current_user: User = Depends(get_current_user)):
    article = await service.get(id)
    
    if not ArticlePolicy().can_edit(current_user, article):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Continue with update...
```

## Why Policies?

| Benefit | Description |
|---------|-------------|
| 🔒 **Centralized** | All rules in one place |
| 🧪 **Testable** | Easy to unit test |
| 📖 **Readable** | Clear authorization logic |

## See Also

- [Security Guide](../../best-practices/security.md)
